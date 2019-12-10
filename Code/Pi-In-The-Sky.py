import time

import Adafruit_LSM303
import servo
from picamera import PiCamera
import RPi.GPIO as GPIO
import math
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
motorOn = True
totalAccel = 0
accelValsBeforeMotor = [[0,0,0,0]]
#make a map function for the servo and acsellerometer values
def realMap(number, lowFirst, highFirst,lowSecond, highSecond):
    newNumber =(number-lowFirst)/(highFirst-lowFirst)*(highSecond-lowSecond)+lowSecond
    return newNumber

def beep():
	#beep on the buzzer

while !motorOn:
	accel, mag = lsm303.read()
    accel_x, accel_y, accel_z = accel
    x = realMap(accel_x, -1000, 1000, -9.81, 9.81)
    y = realMap(accel_y, -1000, 1000, -9.81, 9.81)
    z = realMap(accel_z, -1000, 1000, -9.81, 9.81)
    currentAccel = math.sqrt(x**2+y**2+z**2)
    if(currentAccel>15):
    	motorOn = True
while True:
	#get the accelllerometor values and map them to m/s^2
	currTime = time.time()-start_time
	accel, mag = lsm303.read()
    accel_x, accel_y, accel_z = accel
    x = realMap(accel_x, -1000, 1000, -9.81, 9.81)
    y = realMap(accel_y, -1000, 1000, -9.81, 9.81)
    z = realMap(accel_z, -1000, 1000, -9.81, 9.81)
    deltat = currTime-accelVals[len(accelVals)-1][3]

    #if motor is on, append the values to the array describing the accelleratiion before
    #The Motor cuts out, otherwise add it to the one describing after the motor cuts out
    if(motorOn):
    	accelValsBeforeMotor.append([x,y,z,deltat])
   	else:
   		accelValsAfterMotor.append([x,y,z,deltat])
    currentAccel = math.sqrt(x**2+y**2+z**2)
    if(currentAccel<10):
    	motorOn = False

    #Integrate Accelleratian over the flight time to get current velocity
    for a in range(len(accelValsBeforeMotor)):
    	xVel += math.sqrt(a[0]**2+a[1]**2+a[2]**2)*a[3]
    for b in range(len(accelValsAfterMotor)):
    	xVel += b[0]*b[3]
    	yVel += b[1]*b[3]
    	zVel +=
    currentVelocity = totalAccel

    #If the velocity is low, beep
    if currentVelocity<1:
    	beep()

    #set the servo position and map it to the duty cycle so it can be used
    if(currTime>90):
    	servoPos = 180
    else:
    	servoPos = 90
    dutyCycle = realMap(servoPos, 0, 180, 1, 2)#If duty cycle is 1 angle is  0, 2 angle is 180
    p.ChangeDutyCycle(servoPos)


    #Record video for three minutes
    if(time.time()-start_time>180):
    	myCamera.stop_recording()