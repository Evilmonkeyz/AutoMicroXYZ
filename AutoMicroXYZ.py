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
# end Motor Class


# Initialize all four motors
m1 = SMotor(1, 0x48, 0x20)
m2 = SMotor(1, 0x49, 0x21)
m3 = SMotor(1, 0x4A, 0x22)
m4 = SMotor(1, 0x4B, 0x23)


# Turn a motor on or off with ON and OFF variables
def motorONOFF(motor, intVal):
    motor.enable = intVal
    # read data from gpio
    tempd = i2cbus.read_byte_data(motor.gpioI2C, 0x00)
    tempval = i2cbus.read_byte_data(motor.gpioI2C, GPIOVAL)
    tempctl = i2cbus.read_byte_data(motor.gpioI2C, GPIOCTL)
    print("Value of motor" + motor + " GPIO: " + tempd)
    print("Value of motor" + motor + " val: " + tempval)
    print("Value of motor" + motor + " ctl: " + tempctl)
    if(intVal == 1):
        tempd = bitmanip(tempd, 7, 1)      # set to 1, disable motor
        tempval = bitmanip(tempval, 7, 1)  # set to 1, don't care
        tempctl = bitmanip(tempctl, 7, 1)  # Set to 1, GPIO is input
        i2cbus.write_byte_data(motor.gpioI2C, GPIOVAL, tempval)
        i2cbus.write_byte_data(motor.gpioI2C, GPIOCTL, tempctl)
        print("Value of motor" + motor + " GPIO: " + tempd)
        print("Value of motor" + motor + " val: " + tempval)
        print("Value of motor" + motor + " ctl: " + tempctl)
        print("Turning off Motor" + motor)
    elif(intVal == 0):
        tempd = bitmanip(tempd, 7, 0)      # set to 0, enable motor
        tempval = bitmanip(tempval, 7, 0)  # set to 0, drive low
        tempctl = bitmanip(tempctl, 7, 0)  # Set to 0, GPIO is output
        i2cbus.write_byte_data(motor.gpioI2C, GPIOVAL, tempval)
        i2cbus.write_byte_data(motor.gpioI2C, GPIOCTL, tempctl)
        print("Value of motor" + motor + " GPIO: " + tempd)
        print("Value of motor" + motor + " val: " + tempval)
        print("Value of motor" + motor + " ctl: " + tempctl)
        print("Turning on Motor" + motor)


# Motor driving Functions
def motorSTEP(motor, dir, speed, stepnum):
    # First check if motor if enabled
    if(motor.enable == 0):
        motor.reset = 1  # Bring motor out of reset
        tempd = i2cbus.read_byte_data(motor.gpioI2C, 0x00)
        tempd = bitmanip(tempd, 7, 1)      # set to 1, disable motor


# Method for manipulating individual bits in a byte
def bitmanip(byte, bitpos, bitval):
    if(bitval == 1):
        byte = byte | (1 << bitpos)
    elif(bitval == 0):
        byte = byte & ~(1 << bitpos)
    return byte


# Test section
# print(m1.enable)
# motorONOFF(m1, ON)
# print(m1.enable)
# motorONOFF(m1, OFF)
# print(m1.enable)
