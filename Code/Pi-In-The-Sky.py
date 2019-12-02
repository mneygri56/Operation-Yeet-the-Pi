import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_LSM303

# Create a LSM303 instance.
lsm303 = Adafruit_LSM303.LSM303()

RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

def realMap(number, lowFirst, highFirst,lowSecond, highSecond):
    newNumber =(number-lowFirst)/(highFirst-lowFirst)*(highSecond-lowSecond)+lowSecond
    return newNumber