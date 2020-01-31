import time

import Adafruit_LSM303
from picamera import PiCamera
import RPi.GPIO as GPIO
import math

#Initialize the accellerometer
lsm303 = Adafruit_LSM303.LSM303()

#Initialize the camera
#myCamera = PiCamera()

#Get the starting time
start_time = time.time()

#Initialize the servo
servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(2.5) #Initialize to 90

parachuteServoPin = 18
GPIO.setup(parachuteServoPin, GPIO.OUT)
p2 = GPIO.PWM(parachuteServoPin, 50) # GPIO 18 for PWM with 50Hz
p2.start(2.5) #Initialize to 90

buzzerPin = 14
GPIO.setup(buzzerPin, GPIO.OUT)

accelValsBeforeMotor = [[0,0,0,0]]

beeped = False
#make a map function for the servo and acsellerometer values
def realMap(number, lowFirst, highFirst,lowSecond, highSecond):
	newNumber =(number-lowFirst)/(highFirst-lowFirst)*(highSecond-lowSecond)+lowSecond
	return newNumber

def beep():
	GPIO.output(buzzerPin, GPIO.HIGH)
	time.sleep(.1)
	GPIO.output(buzzerPin, GPIO.LOW)
	time.sleep(.1)
#Start recording the camera
#myCamera.start_recording('thrustCam.h264')
currTime = time.time()-start_time
while currTime<40:
    #get the current time
    currTime = time.time()-start_time

    #get the accelllerometor values and map them to m/s^2
    accel, mag = lsm303.read()
    accel_x, accel_y, accel_z = accel
    x = realMap(accel_x, -1000, 1000, -9.81, 9.81)
    y = realMap(accel_y, -1000, 1000, -9.81, 9.81)
    z = realMap(accel_z, -1000, 1000, -9.81, 9.81)

    #Append these values so we can get the accelleration data
    accelValsBeforeMotor.append([x,y,z, currTime])
    print(str(x)+", "+str(y)+", "+str(z)+" ,"+str(currTime))
    #If the velocity is low, beep
    if currTime>20 and not beeped:
    	beep()
    	beeped = True

    #set the servo position and map it to the duty cycle so it can be used
    if(currTime>20):
    	servoPos = 180

    	parachuteServoPos = 180
    else:
    	servoPos = 90

    	parachuteServoPos = 0
    dutyCycle = realMap(servoPos, 0, 180, 1, 2)#If duty cycle is 1 angle is  0, 2 angle is 180
    p.ChangeDutyCycle(dutyCycle)
    parachuteCycle = realMap(parachuteServoPos, 0, 180, 1, 2)
    p2.ChangeDutyCycle(parachuteCycle)

    #Record video for three minutes
    #if(time.time()-start_time>180):
    #	myCamera.stop_recording()
GPIO.cleanup()
