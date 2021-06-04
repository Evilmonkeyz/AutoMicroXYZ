# #!/usr/bin/env python3
#######################################
# AutoMicroXYZ
# V 0.1
# Written by: Kenton Smith
#######################################

# TODO:
# Write all of the code.
# 

# GOALS:
# Text and GUI versions.
#   -> Text mode allows for commands to be entered in from the command line
#   -> GUI mode is for use with a touchscreen mounted on the microscope for easy input.
# Manual Move
#   -> Move microscope X,Y,Z with manual input
# Auto Move Modes
#   -> Auto Stitch - Takes all images necessary for a full stitch to be performed
#   -> Auto Stack  - Takes specified number of images at different depths for a focus-stack image.
#
# STRETCH GOALS:
# Add 4th motor for controlling Objective lenses
# Take the microscope to Twitch :)


# Motor control Functions
# Motor 1 = X direciton
# Motor 2 = Y direction
# Motor 3 = Z direction
# Motor 4 = Objective Select

# Motor class
class SMotor:
  # number      = motor number, either 1,2,3 or 4
  # digipotI2C  = I2C address for digipot. 0x48, 0x49, 0x4A, or 0x4B
  # gpioI2C     = I2C address for GPIO. 0x20, 0x21, 0x22, or 0x23
  # digipotVAL  = Value for digipot, controls motor current. Should be less than 0x7F.
  # enable      = 1 = motor disabled, 0 = motor enabled.
  # sleep       = 1 = normal operation, 0 = sleep mode
  # reset       = 1 = normal operation, 0 = jeld in reset.
  # stepsize    = 0 = Full, 1 = 1/2th, 2 = 1/4th, 3 = 1/8th , 7 = 1/16th
    
  def __init__(self, number, digipotI2C, gpioI2C) 
    self.number = number
    self.digipotI2C = digipotI2C
    self.gpioI2C = gpioI2C
    
  digipotVAL = 0x1F
  enable = 1
  sleep = 1
  reset = 0
  stepsize = 0
# end Motor Class  
  
# def initMotor(motornum, ):



