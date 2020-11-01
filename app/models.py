from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import ValidationError
import pytz
import io
import base64

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    #posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

class Sensors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_type = db.Column(db.Integer)
    sensor_pin = db.Column(db.Integer, unique = True)
    readings = db.relationship('Readings', backref='generator', lazy='dynamic')
    #timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    #sensor_type = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<Sensor {self.id}>'
    
class Light(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    starting_time = db.Column(db.Time)
    duration = db.Column(db.Time)
    
class PlotInterval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    starting_time = db.Column(db.DateTime, default=datetime.utcnow)
    ending_time = db.Column(db.DateTime, default=datetime.utcnow)

    
class Readings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    reading_type = db.Column(db.String(140))
    reading_value = db.Column(db.Numeric)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'))

    def __repr__(self):
        return f'{self.reading_type} type data, value: {self.reading_value} from sensor {self.sensor_id}'
    
class DHTData(object):
    
    def validate_sensor(self, sensor):
        sensor_type = Sensors.query.filter_by(sensor_type=sensor.sensor_type).first()
        sensor_pin = Sensors.query.filter_by(sensor_pin=sensor.sensor_pin).first()
        if (sensor_pin and sensor_type) is not None:
            raise ValidationError(f'Sensor already exist.')
        else:
            return sensor_pin
    
    def define_sensor(self,sensor_type, sensor_pin):
        sensor = Sensors(sensor_type=sensor_type, sensor_pin=sensor_pin)
        if self.validate_sensor(sensor) is None:
            db.session.add(sensor)
            db.session.commit()
        else:
            sensor = Sensors.query.filter_by(sensor_pin = sensor_pin).first()
            sensor.sensor_type=sensor_type
            db.session.commit()
        
    def get_sensors(self):
        return Sensors.query.all()
    
    def add_reading(self, timestamp, reading_type, reading_value, sensor_id):
        reading = Readings(timestamp = timestamp, reading_type = reading_type,
                 reading_value = reading_value, sensor_id = sensor_id)
        db.session.add(reading)
        db.session.commit()
        
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

class PlotData(object):
    
    def convert_to_utc(local_datetime):
        return local_datetime.astimezone(pytz.utc)
    
    def data_for_plot(reading_type, start, end):
        if reading_type == 'hum':
            data = Readings.query.filter_by(reading_type = 'hum').order_by(Readings.timestamp.asc())
        elif reading_type == 'temp':
            data = Readings.query.filter_by(reading_type = 'temp').order_by(Readings.timestamp.asc())
        else:
            print(f'reading type should be a string between "hum" and "temp"')

        return data.filter((Readings.timestamp >= PlotData.convert_to_utc(start)) & 
                    (Readings.timestamp <= PlotData.convert_to_utc(end))).values('timestamp','reading_value')
    
    def convert_to_localstr(utc_datetime):
        if isinstance(utc_datetime,str):
            utc_datetime = datetime.strptime(utc_datetime,'%Y-%m-%d %H:%M:%S.%f')
        utc_datetime  = utc_datetime.replace(tzinfo=pytz.utc)
        la = pytz.timezone('Europe/Rome')
        return datetime.strftime(utc_datetime.astimezone(la),'%m-%d %H:%M:%S')

    def Plot_Image(hum,temp):
        fig = Figure(figsize=(12,5))
        plt.gcf().subplots_adjust(bottom=0.15)

        axis= fig.add_subplot(1, 2, 1)
        axis.tick_params(axis = 'x',labelrotation=90)
        axis.set_ylabel("humidity")
        axis.xaxis.set_major_locator(plt.MaxNLocator(10))
        axis.yaxis.set_major_locator(plt.MaxNLocator(10))
        axis.grid()
        xy = [i for i in hum]
        x = [PlotData.convert_to_localstr(a[0]) for a in xy]
        y = [a[1] for a in xy] 
        axis.set_title(f'Umidity from {x[0]} to {x[-1]}')
        axis.plot(x, y, "-")

        axis2= fig.add_subplot(1, 2, 2)
        axis2.tick_params(axis = 'x',labelrotation=90)
        axis2.set_ylabel("temperature")
        axis2.xaxis.set_major_locator(plt.MaxNLocator(10))
        axis2.yaxis.set_major_locator(plt.MaxNLocator(10))
        axis2.grid()
        xy = [i for i in temp]
        x = [PlotData.convert_to_localstr(a[0]) for a in xy]
        y = [a[1] for a in xy] 
        axis2.set_title(f'Temperature from {x[0]} to {x[-1]}')
        axis2.plot(x, y, "r-")

        # Convert plot to PNG image
        pngImage = io.BytesIO()
        FigureCanvas(fig).print_png(pngImage)

        # Encode PNG image to base64 string
        pngImageB64String = "data:image/png;base64,"
        pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
        return  pngImageB64String

        
@login.user_loader
def load_user(id):
    return User.query.get(int(id))