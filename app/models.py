import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import ValidationError
import pytz
import io
import base64
from sqlalchemy.sql import func
import numpy as np
import itertools

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
    starting_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    ending_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    
class Readings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
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
        
    def consistence(self, humidity,temperature):
        if (humidity==None or temperature==None):
            return False
        elif ((humidity>= 15 and humidity<=100) and (temperature>= -50 and temperature<=150)):
            return True
        else:
            return False

    def filter_parameter_last_day(self,reading_type):
        try:
            mean = float(Readings.query.order_by(Readings.timestamp.desc()).\
                        with_entities(func.avg(Readings.reading_value).label('average')).\
                        filter(Readings.reading_type == reading_type).limit(10)[0][0])
            return mean
        except:
            pass
        return None
    
    def filtering(self, humidity,temperature , std_factor = 2):
        h_mean = self.filter_parameter_last_day('hum')
        t_mean = self.filter_parameter_last_day('temp')
        
        if (h_mean is not None) & (t_mean is not None):
            h_standard_deviation = 20
            t_standard_deviation = 10
        else:
            return True             


        if (humidity > h_mean - std_factor * h_standard_deviation) and \
            (humidity < h_mean + std_factor * h_standard_deviation) and \
            (temperature > t_mean - std_factor * t_standard_deviation) and \
            (temperature < t_mean + std_factor * t_standard_deviation):
            return True    

        else:
            return False
        
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

        return list(data.filter((Readings.timestamp >= PlotData.convert_to_utc(start)) & 
                    (Readings.timestamp <= PlotData.convert_to_utc(end))).values('timestamp','reading_value'))
    
    def convert_to_localstr(utc_datetime):
        if isinstance(utc_datetime,str):
            utc_datetime = datetime.datetime.strptime(utc_datetime,'%Y-%m-%d %H:%M:%S.%f')
        utc_datetime  = utc_datetime.replace(tzinfo=pytz.utc)
        la = pytz.timezone('Europe/Rome')
        return datetime.datetime.strftime(utc_datetime.astimezone(la),'%Y-%m-%d %H:%M:%S.%f')

    def subplot(fig, measures,y_label, plot_number , line_color):
        axis= fig.add_subplot(1, 2, plot_number)
        axis.tick_params(axis = 'x',labelrotation=90)
        axis.set_ylabel(y_label)
        axis.xaxis.set_major_locator(plt.MaxNLocator(10))
        axis.yaxis.set_major_locator(plt.MaxNLocator(10))
        axis.grid()
        x_hum = []
        y_hum = []
        step = int(len(measures)/300)
        
        if step:
            pass
        else: 
            step = 1
            
        for (x,y) in  itertools.islice(measures,0,len(measures),):
            x_hum.append(PlotData.convert_to_localstr(x))
            y_hum.append(y)
        if x:
            axis.set_title(f'{y_label} from {x_hum[0]} to {x_hum[-1]}')
        axis.plot(x_hum, y_hum, line_color)

    def Plot_Image(hum,temp):
        fig = plt.figure(figsize=(12,5))
        plt.gcf().subplots_adjust(bottom=0.15)
        
        if hum:
            PlotData.subplot(fig,hum, 'humidity',1,"-")
            PlotData.subplot(fig,temp, 'temperature',2,"r-")

        # Convert plot to PNG image
        pngImage = io.BytesIO()
        FigureCanvas(fig).print_png(pngImage)

        # Encode PNG image to base64 string
        pngImageB64String = "data:image/png;base64,"
        pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
        #plt.show()
        return  pngImageB64String

    
from app import dasht
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly
import plotly.graph_objs as go
from collections import deque

class DashPlot(object):
    
    def plot_data():
        
        start = datetime.datetime(2020,11,16,10,0).astimezone(pytz.timezone('Europe/Rome'))
        end = datetime.datetime.now()
        
        hum = pd.DataFrame.from_records(PlotData.data_for_plot('hum', start, end), 
                                        columns = ('datetime', 'value'))
        hum.datetime = hum.datetime.apply(PlotData.convert_to_localstr)
        
        temp = pd.DataFrame.from_records(PlotData.data_for_plot('temp', start, end),
                                         columns = ('datetime', 'value'))
        temp.datetime = temp.datetime.apply(PlotData.convert_to_localstr)
        
        X = deque(maxlen = 100)
        Y = deque(maxlen = 100)
        
        dasht.layout = html.Div(children=[
            html.H1(children='Hello Dash'),

            html.Div(children='''
                Dash: A web application framework for Python.
            '''),
#             [
#                 dcc.Graph(id = 'live-graph', animate = True),
#                 dcc.Interval(
#                     id = 'graph-update',
#                     interval = 2000
#                     )
#             ],
 

            dcc.Graph(
                id='example-graph',
                    figure={
                        'data': [
                            {'x': hum.datetime, 'y': hum.value, 'type': 'line', 'name': 'SF'},
                        ],
                        'layout': {
                            'title': 'Dash Data Visualization'
                        }
                    }
                
                ),
            
             dcc.Graph(
                id='example-graph',
                    figure={
                        'data': [
                            {'x': temp.datetime, 'y': temp.value, 'type': 'line', 'name': 'SF'},
                        ],
                        'layout': {
                            'title': 'Dash Data Visualization'
                        }
                    }
                
                )
            ])            
        return dasht.index()
        
@login.user_loader
def load_user(id):
    return User.query.get(int(id))