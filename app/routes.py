from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, LightConfiguration, PlotConfiguration
from app.models import User, Light, PlotInterval, PlotData


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
#@login_required #questa riga può bloccare le nuove registrazioni
def register():
    #if current_user.is_authenticated:
    #    return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/light', methods=['GET', 'POST'])
@login_required
def light():
    form = LightConfiguration()
    if form.validate_on_submit():
        if Light.query.all():
            q = db.session.query(Light)
            q = q.filter(Light.id==1)
            record = q.one()
            record.starting_time = form.starting_time.data
            record.duration = form.duration.data
            db.session.commit()
        else:
            light = Light(starting_time=form.starting_time.data, duration=form.duration.data)
            db.session.add(light)
            db.session.commit()
        flash('Succesfully light configuration saved')
        return redirect(url_for('light'))
    elif request.method == 'GET':
        form.starting_time.data = Light.query.first().starting_time
        form.duration.data = Light.query.first().duration
    return render_template('light.html', form = form)
                      
    

from datetime import datetime
import pytz

@app.route("/ploty", methods=["GET", 'POST'])
def ploty():
    form = PlotConfiguration()
    if form.validate_on_submit():
        if PlotInterval.query.all():
            q = db.session.query(PlotInterval)
            q = q.filter(PlotInterval.id==1)
            record = q.one()
            record.starting_time = form.starting_time.data
            record.ending_time = form.ending_time.data
            db.session.commit()
        else:
            plot_d = PlotInterval(starting_time = form.starting_time.data,
                              ending_time = form.ending_time.data)

            db.session.add(plot_d) 
            db.session.commit()    
        start = form.starting_time.data#datetime(2020,10,31,18,0).astimezone(pytz.timezone('Europe/Rome'))
        end = form.ending_time.data#datetime(2020,10,31,19,15).astimezone(pytz.timezone('Europe/Rome'))
        
        # Generate plot
        #hum = PlotData.data_for_plot('hum', start, end)
        #temp = PlotData.data_for_plot('temp', start, end)

        flash('Succesfully Interval Configured')
        return redirect(url_for('ploty'))
    
    elif request.method == 'GET':
        form.starting_time.data = PlotInterval.query.first().starting_time
        form.ending_time.data = PlotInterval.query.first().ending_time

        start = form.starting_time.data#datetime(2020,10,31,18,0).astimezone(pytz.timezone('Europe/Rome'))
        end = form.ending_time.data#datetime(2020,10,31,19,15).astimezone(pytz.timezone('Europe/Rome'))
        
    hum = PlotData.data_for_plot('hum', start, end)
    temp = PlotData.data_for_plot('temp', start, end)        
    
    pngImageB64String = PlotData.Plot_Image(hum,temp)
    return render_template("ploty.html", image=pngImageB64String, form = form)

                      