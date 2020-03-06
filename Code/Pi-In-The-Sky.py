import time

import Adafruit_LSM303
from picamera import PiCamera
import RPi.GPIO as GPIO
import math
import smbus

# Get I2C bus
bus = smbus.SMBus(1)

# MPL3115A2 address, 0x60(96)
# Select control register, 0x26(38)
#		0xB9(185)	Active mode, OSR = 128, Altimeter mode
bus.write_byte_data(0x60, 0x26, 0xB9)
# MPL3115A2 address, 0x60(96)
# Select data configuration register, 0x13(19)
#		0x07(07)	Data ready event enabled for altitude, pressure, temperature
bus.write_byte_data(0x60, 0x13, 0x07)
# MPL3115A2 address, 0x60(96)
# Select control register, 0x26(38)
#		0xB9(185)	Active mode, OSR = 128, Altimeter mode
bus.write_byte_data(0x60, 0x26, 0xB9)

time.sleep(1)
#Initialize the accellerometer
lsm303 = Adafruit_LSM303.LSM303()

#Initialize the camera
myCamera = PiCamera()

#Get the starting time
start_time = time.time()

#Initialize the servo
parachuteServoPin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(parachuteServoPin, GPIO.OUT)
p2 = GPIO.PWM(parachuteServoPin, 50) # GPIO 18 for PWM with 50Hz
p2.start(2.5) #Initialize to 90

buzzerPin = 14
GPIO.setup(buzzerPin, GPIO.OUT)

accelValsBeforeMotor = [[0,0,0,0]]

beeped = False
secsPerYear = 60*60*24*365
#make a file to log accelleration data:
startYear = 1970 + math.floor(start_time/31556926)
startMonth = math.floor((start_time%31556926)/2629743)
startDay = math.floor(((start_time%31556926)%2629743)/86400)
startHr = math.floor((((start_time%31556926)%2629743)%86400)/3600)
startMin = math.floor(((((start_time%31556926)%2629743)%86400)%3600)/60)
startSec = math.floor(((((start_time%31556926)%2629743)%86400)%3600)%60)
f= open("Accel_From"+str(startMonth)+"."+str(startDay)+"."+str(startYear)+", "+str(startHr)+"."+str(startMin)+"."+str(startSec)+".txt", "w+")

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
myCamera.start_recording('thrustCam'+str(startMonth)+"."+str(startDay)+"."+str(startYear)+", "+str(startHr)+"."+str(startMin)+"."+str(startSec)+'.h264')
myCamera.start_preview(alpha = 155)
currTime = time.time()-start_time
while currTime<120:
             data = bus.read_i2c_block_data(0x60, 0x00, 6)
             # MPL3115A2 address, 0x60(96)
             # Select control register, 0x26(38)
             #		0xB9(185)	Active mode, OSR = 128, Altimeter mode
             bus.write_byte_data(0x60, 0x26, 0xB9)
             # MPL3115A2 address, 0x60(96)
             # Select data configuration register, 0x13(19)
             #		0x07(07)	Data ready event enabled for altitude, pressure, temperature
             bus.write_byte_data(0x60, 0x13, 0x07)
             # MPL3115A2 address, 0x60(96)
             # Select control register, 0x26(38)
             #		0xB9(185)	Active mode, OSR = 128, Altimeter mode
             bus.write_byte_data(0x60, 0x26, 0xB9)
             time.sleep(1)
             # Convert the data to 20-bits
             data = bus.read_i2c_block_data(0x60, 0x00, 6)
             tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
             temp = ((data[4] * 256) + (data[5] & 0xF0)) / (16)
             altitude = tHeight / (16.0)
             cTemp = temp / 16.0
             fTemp = cTemp * 1.8 + 32
             # MPL3115A2 address, 0x60(96)
             # Select control register, 0x26(38)
             #		0x39(57)	Active mode, OSR = 128, Barometer mode
             bus.write_byte_data(0x60, 0x26, 0x39)

             time.sleep(1)
             # MPL3115A2 address, 0x60(96)
             # Read data back from 0x00(00), 4 bytes
             # status, pres MSB1, pres MSB, pres LSB
             data = bus.read_i2c_block_data(0x60, 0x00, 4)
             # Convert the data to 20-bits
             pres = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
             pressure = (pres / 4.0) / 1000
             #get the current time
             currTime = time.time()-start_time


             #get the accelllerometor values and map them to m/s^2
             accel, mag = lsm303.read()
             accel_x, accel_y, accel_z = accel
             x = realMap(accel_x, -1000, 1000, -9.81, 9.81)
             y = realMap(accel_y, -1000, 1000, -9.81, 9.81)
             z = realMap(accel_z, -1000, 1000, -9.81, 9.81)

             #Append these values so we can get the accelleration data
             f.write(str(x)+" (x)m/s^2, "+str(y)+" (y)m/s^2, "+str(z)
                +" (z)m/s^2,\n"+str(pressure)+"kPa\n"+str(altitude)+"m\n"
                +str(cTemp)+"deg C\n"+str(currTime)+"seconds\n")
             f.flush()
             #If the velocity is low, beep
             if currTime>30 and not beeped:
                beep()
                beeped = True
             #set the servo position and map it to the duty cycle so it can be used
             if(currTime>30):
                parachuteServoPos = 90
             else:
                parachuteServoPos = 0
             parachuteCycle = realMap(parachuteServoPos, 0, 180, 2.5, 12.5)
             p2.ChangeDutyCycle(parachuteCycle)
myCamera.stop_recording()
myCamera.stop_preview()
GPIO.cleanup()
p2.stop()
f.close()
