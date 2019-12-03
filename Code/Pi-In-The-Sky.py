import time

import Adafruit_LSM303
import servo
from picamera import PiCamera
import RPi.GPIO as GPIO
#Initialize the accellerometer 
lsm303 = Adafruit_LSM303.LSM303()

#Initialize the camera
myCamera = PiCamera()
start_time = time.time()
myCamera.start_recording('thrustCam.h264')

#Initialize the servo
servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(2.5)#Initialize to 90

accelVals = [[0,0,0]]
#make a map function for the servo and acsellerometer values
def realMap(number, lowFirst, highFirst,lowSecond, highSecond):
    newNumber =(number-lowFirst)/(highFirst-lowFirst)*(highSecond-lowSecond)+lowSecond
    return newNumber
while True:
	#get the accelllerometor values and map them to m/s^2
	currTime = time.time()-start_time
	accel, mag = lsm303.read()
    accel_x, accel_y, accel_z = accel
    x = realMap(accel_x, -1000, 1000, -9.81, 9.81)
    y = realMap(accel_y, -1000, 1000, -9.81, 9.81)
    z = realMap(accel_z, -1000, 1000, -9.81, 9.81)
    accelVals.append((x,y,z))

    #set the servo position and map it to the duty cycle so it can be used
    if(currTime>90):
    	servoPos = 180
    else:
    	servoPos = 90
    dutyCycle = map(servoPos, 0, 180, 1, 2)#If duty cycle is 1 angle is  0, 2 angle is 180
    p.ChangeDutyCycle(servoPos)


    #Record video for three minutes
    if(time.time()-start_time>180):
    	myCamera.stop_recording()