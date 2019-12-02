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


def realMap(number, lowFirst, highFirst,lowSecond, highSecond):
    newNumber =(number-lowFirst)/(highFirst-lowFirst)*(highSecond-lowSecond)+lowSecond
    return newNumber
while True:
	accel, mag = lsm303.read()
    #get the accelerations and map them to the gravity thing
    accel_x, accel_y, accel_z = accel
    x = realMap(accel_x, -1000, 1000, -9.81, 9.81)
    y = realMap(accel_y, -1000, 1000, -9.81, 9.81)
    z = realMap(accel_z, -1000, 1000, -9.81, 9.81)
    dutyCycle = map(servoPos, 0, 180, 1, 2)
    if(time.time()-start_time>180):
    	myCamera.stop_recording()