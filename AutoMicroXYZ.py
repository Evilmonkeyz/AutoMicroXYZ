# #!/usr/bin/env python3

#########################################
# AutoMicroXYZ
# V 0.1
# Written by: Kenton Smith
#########################################

# TODO:
# Write all of the code.
#

# GOALS:
# Text and GUI versions.
#   -> Text mode allows for commands to be entered in from the command line
#   -> GUI mode is for use with a touchscreen mounted on the microscope for
#      easy input.
# Manual Move
#   -> Move microscope X,Y,Z with manual input
# Auto Move Modes
#   -> Auto Stitch - Takes all images necessary for a full stitch to be
#                    performed
#   -> Auto Stack  - Takes specified number of images at different depths for
#                    a focus-stack image.
#
# STRETCH GOALS:
# Add 4th motor for controlling Objective lenses
# Take the microscope to Twitch :)

#########################################
# Motor section
#########################################
# Motor control Functions:
# Motor 1 = X direciton
# Motor 2 = Y direction
# Motor 3 = Z direction
# Motor 4 = Objective Select

# imports
from smbus import SMBus
import time
from threading import Timer


def usleep(x):
    time.sleep(x/1000000)


# Variables
OFF = 1
ON = 0

GPIOVAL = 0x01
GPIOCTL = 0x03


# Initialize I2C bus
i2cbus = SMBus(1)  # Create a new I2C bus


# Motor class
class SMotor:
    # number      = motor number, either 1,2,3 or 4
    # digipotI2C  = I2C address for digipot. 0x48, 0x49, 0x4A, or 0x4B
    # gpioI2C     = I2C address for GPIO. 0x20, 0x21, 0x22, or 0x23
    # digipotVAL  = Value for digipot, controls motor current.
    #               Should be less than 0x7F.
    # enable      = 1 = motor disabled, 0 = motor enabled.
    # sleep       = 1 = normal operation, 0 = sleep mode
    # reset       = 1 = normal operation, 0 = jeld in reset.
    # stepsize    = 0 = Full, 1 = 1/2th, 2 = 1/4th, 3 = 1/8th , 7 = 1/16th

    def __init__(self, number, digipotI2C, gpioI2C):
        self.number = number
        self.digipotI2C = digipotI2C
        self.gpioI2C = gpioI2C

    digipotVAL = 0x1F
    enable = 1
    sleep = 1
    reset = 0
    stepsize = 0
    mdir = 0
# end Motor Class


# Initialize all four motors
mx = SMotor(1, 0x48, 0x20)
my = SMotor(1, 0x49, 0x21)
mz = SMotor(1, 0x4A, 0x22)
m4 = SMotor(1, 0x4B, 0x23)

# Set up digipot
def initDigipot(motor, intVal):
    motor.digipotVAL = intVal
    i2cbus.write_word_data(motor.digipotI2C, 0xD1, 0xE511)
    i2cbus.write_word_data(motor.digipotI2C, 0x21, 0xF001)

# Turn a motor on or off with ON and OFF variables
def motorONOFF(motor, intVal):
    motor.enable = intVal
    # read data from gpio
    tempd = i2cbus.read_byte_data(motor.gpioI2C, 0x00)
    tempval = i2cbus.read_byte_data(motor.gpioI2C, GPIOVAL)
    tempctl = i2cbus.read_byte_data(motor.gpioI2C, GPIOCTL)
    print("Value of motor  GPIO: " + str(hex(tempd)))
    print("Value of motor  val: " + str(hex(tempval)))
    print("Value of motor  ctl: " + str(hex(tempctl)))
    if(intVal == 1):
        tempd = bitmanip(tempd, 7, 1)      # set to 1, disable motor
        tempval = bitmanip(tempval, 7, 1)  # set to 1, don't care
        tempctl = bitmanip(tempctl, 7, 1)  # Set to 1, GPIO is input
        i2cbus.write_byte_data(motor.gpioI2C, GPIOVAL, tempval)
        i2cbus.write_byte_data(motor.gpioI2C, GPIOCTL, tempctl)
        print("Value of motor GPIO: " + str(hex(tempd)))
        print("Value of motor val: " + str(hex(tempval)))
        print("Value of motor  ctl: " + str(hex(tempctl)))
        print("Turning off Motor")
    elif(intVal == 0):
        tempd = bitmanip(tempd, 7, 0)      # set to 0, enable motor
        tempval = bitmanip(tempval, 7, 0)  # set to 0, drive low
        tempctl = bitmanip(tempctl, 7, 0)  # Set to 0, GPIO is output
        i2cbus.write_byte_data(motor.gpioI2C, GPIOVAL, tempval)
        i2cbus.write_byte_data(motor.gpioI2C, GPIOCTL, tempctl)
        print("Value of motor  GPIO: " + str(hex(tempd)))
        print("Value of motor  val: " + str(hex(tempval)))
        print("Value of motor  ctl: " + str(hex(tempctl)))
        print("Turning on Motor")


# Place a motor driver into reset or bring it out of reset
def motorRESET(motor, intVal):
    motor.reset = intVal
    # Update output value
    tempval = i2cbus.read_byte_data(motor.gpioI2C, GPIOVAL)
    tempval = bitmanip(tempval, 6, intVal)  # Set bit 6 to 1
    i2cbus.write_byte_data(motor.gpioI2C, GPIOVAL, tempval)
    # Update control regsiter (1 = input, 0 = output)
    tempctl = i2cbus.read_byte_data(motor.gpioI2C, GPIOCTL)
    tempctl = bitmanip(tempctl, 6, 0)  # Set bit 6 to output
    i2cbus.write_byte_data(motor.gpioI2C, GPIOCTL, tempctl)


# Set motor step size.
def motorSTEPSIZE(motor, stepsize):
    # stepsize    = 0 = Full, 1 = 1/2th, 2 = 1/4th, 3 = 1/8th , 7 = 1/16th
    bitM1 = 0
    bitM2 = 0
    bitM3 = 0
    # Fullstep
    if(stepsize == 0):
        motor.stepsize = stepsize
    # Halfstep
    elif(stepsize == 1):
        motor.stepsize = stepsize
        bitM1 = 1
    # Fourthstep
    elif(stepsize == 2):
        motor.stepsize = stepsize
        bitM2 = 1
    # Eightstep
    elif(stepsize == 3):
        motor.stepsize = stepsize
        bitM1 = 1
        bitM2 = 1
    # Sixteenthstep
    elif(stepsize == 7):
        motor.stepsize = stepsize
        bitM1 = 1
        bitM2 = 1
        bitM3 = 1
    else:
        raise ValueError("stepsize can only be 0,1,2,3 or 7")

    # Update output value for steps
    tempval = i2cbus.read_byte_data(motor.gpioI2C, GPIOVAL)
    tempval = bitmanip(tempval, 4, bitM1)
    tempval = bitmanip(tempval, 3, bitM2)
    tempval = bitmanip(tempval, 2, bitM3)
    i2cbus.write_byte_data(motor.gpioI2C, GPIOVAL, tempval)
    # Update control regsiter (1 = input, 0 = output)
    tempctl = i2cbus.read_byte_data(motor.gpioI2C, GPIOCTL)
    tempctl = bitmanip(tempctl, 4, 0)
    tempctl = bitmanip(tempctl, 3, 0)
    tempctl = bitmanip(tempctl, 2, 0)
    i2cbus.write_byte_data(motor.gpioI2C, GPIOCTL, tempctl)


# Set one motor direction
def motorDIR(motor, mdir):
    if(motor == mx):
        dirbit = 6
    elif(motor == my):
        dirbit = 4
    elif(motor == mz):
        dirbit = 2
    elif(motor == m4):
        dirbit = 0
    else:
        raise ValueError("Wrong value for motor specified.")
    motor.mdir = mdir
    tempval = i2cbus.read_byte_data(0x10, GPIOVAL)
    tempval = bitmanip(tempval, dirbit, mdir)
    i2cbus.write_byte_data(0x10, GPIOVAL, tempval)
    tempctl = i2cbus.read_byte_data(0x10, GPIOCTL)
    tempctl = bitmanip(tempctl, dirbit, 0)
    i2cbus.write_byte_data(0x10, GPIOCTL, tempctl)


# Motor driving Functions
def motorSTEP(motor, delay, stepnum):
    # First check if motor if enabled
    if(motor.enable == 0):
        motorRESET(motor, 1)  # Bring motor out of reset
        time.sleep(0.1)
    else:
        raise ValueError("motor is not enabled")
    if(motor == mx):
        stepbit = 7
    elif(motor == my):
        stepbit = 5
    elif(motor == mz):
        stepbit = 3
    elif(motor == m4):
        stepbit = 1
    else:
        raise ValueError("Wrong value for motor specified.")
    # Enable GPIO outputs
    i2cbus.write_byte_data(0x10, GPIOCTL, 0x00)  # set all to outputs
    # Get state of all outputs
    tempval = i2cbus.read_byte_data(0x10, GPIOVAL)
    # Loop through the step function for "stepnum", at "delay" us rate
    print("Stepping for: " + str(stepnum) + " steps")
    delayON = delay/1000000
    delayOFF = delay/10000000
    lowDrive = bitmanip(tempval, stepbit, 0)
    highDrive = bitmanip(tempval, stepbit, 1)
    
    tON = Timer(delayON, stepLOW(lowDrive))
    tOFF = Timer(delayOFF, stepHIGH(highDrive))

    for x in range(stepnum):
        stepLOW(lowDrive)
        time.sleep(delayON)
        #delayloop(delay)
        stepHIGH(highDrive)
        time.sleep(delayON)
        #delayloop(delay)

        #tON.start()
        #tOFF.start()
        #tON.cancel()
        #tOFF.cancel()
        #tON = Timer(delayON, stepLOW(lowDrive))
        #tOFF = Timer(delayOFF, stepHIGH(highDrive))
        #time.sleep(delayON)
        # delayloop(delay)
        #i2cbus.write_byte_data(0x10, GPIOVAL, lowDrive)
        #time.sleep(delayOFF)
        #delayloop(delay)
        #i2cbus.write_byte_data(0x10, GPIOVAL, highDrive)
        #print(x)


# Function to step high
def stepLOW(databyte):
    i2cbus.write_byte_data(0x10, GPIOVAL, databyte)


# Function to step low
def stepHIGH(databyte):
    i2cbus.write_byte_data(0x10, GPIOVAL, databyte)


# Method for manipulating individual bits in a byte
def bitmanip(byte, bitpos, bitval):
    if(bitval == 1):
        byte = byte | (1 << bitpos)
    elif(bitval == 0):
        byte = byte & ~(1 << bitpos)
    return byte

def delayloop(delay):
    for x in range(delay):
        pass

# Test section
#print("Please select the motor you want to drive from mx, my, mz, or m4, and then press ENTER")
#motorSEL = str(input())
#print(motorSEL)
#print(mx.enable)
initDigipot(mx, 0x1F)
initDigipot(my, 0x1F)
initDigipot(mz, 0x1F)
initDigipot(m4, 0x1F)

motorDIR(m4, 1)
motorSTEPSIZE(m4, 7)
motorRESET(m4, 0)
motorONOFF(m4, ON)
#motorRESET(mz, 1)
motorSTEP(m4, 10,1600)
# motorONOFF(m4, OFF)
motorRESET(m4, 0)
#motorRESET(mz, 1)


#time.sleep(0.0001)
#motorSTEPSIZE(mz, 1)
#motorSTEP(mz, 2000, 2000)
# motorRESET(m4, 0)
#motorRESET(mz, 0)
#motorRESET(mz, 1)
#time.sleep(0.0001)
#motorSTEPSIZE(mz, 2)
#motorSTEP(mz, 2000, 2000)
# motorRESET(m4, 0)
#motorRESET(mz, 0)
# motorRESET(mz, 1)
#time.sleep(0.0001)
#motorSTEPSIZE(mz, 3)
#motorSTEP(mz, 2000, 2000)
# motorRESET(m4, 0)
#motorRESET(mz, 0)
# motorRESET(mz, 1)
#time.sleep(0.0001)
#motorSTEPSIZE(mz, 7)
#motorDIR(mz, 0)
#motorSTEP(mz, 2000, 2000)
#motorONOFF(mz, OFF)
#motorRESET(mz, 0)
#motorRESET(mx, 0)

i2cbus.close()

