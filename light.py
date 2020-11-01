from app.models import Light
import RPi.GPIO as GPIO
import datetime

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)

def time_retriver():
    for row in Light.query.all():
        starting_time = row.starting_time
        end_time = row.duration
    return starting_time, end_time
    
def on_or_off(now,starting_time,end_time):
    if starting_time < end_time:
        if now > starting_time and now < end_time:
            return True
        else:
            return False
    else:
        if now > starting_time and now < datetime.time(23,0):
            return True
        elif now >= datetime.time(0,0) and now < end_time:
            return True
        else:
            return False
try:  
    while True:
        starting_time, end_time = time_retriver()
        now = datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute)
        if on_or_off(now, starting_time, end_time):
            GPIO.output(26, GPIO.LOW)
        else:
            GPIO.output(26, GPIO.HIGH)
except:
    raise
   