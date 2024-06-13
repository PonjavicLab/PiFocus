# Before running calibration make sure voltage of AD5693 is 65536/2
# Run the following in console
# --------------------------
# import busio
# import board
# import adafruit_ad569x
# i2c = busio.I2C(board.SCL, board.SDA, frequency=400_000)
# MCP_DAC = adafruit_ad569x.Adafruit_AD569x(i2c)
# MCP_DAC.value = int(65536/2)
# --------------------------

# Then you can move your stage until focused on the beam and run a symmetric in z calibration scan

import busio
import board
import adafruit_ad569x

import os
import sys
import time
import math
import timeit
import datetime
import numpy as np
import matplotlib.pyplot as plt

from picamera2 import Picamera2
import RPi.GPIO as GPIO
from PIL import Image

# Camera settings
# Note that the ROI (500x500 here) should be centered on the beam.
# Easiest way is to align
picam2 = Picamera2()
size = (400, 400)
flim = 500
exp = 60
gain = 1.0
still_config = picam2.create_still_configuration(raw={'format': 'R10', 'size': size}, controls = {"FrameDurationLimits": (flim, flim), "ExposureTime": exp, "AnalogueGain": gain})
picam2.configure(still_config)
picam2.start()

# -----------------------------------------------------------------------------
scanrange = 24 	#In micron
step_size = 1000	#In nanometers
V_cal = 0.01	#nm per voltage (piezo specific)
VDD = 2.47			#Check your DAC voltage at max value 65536 ours is 2.47
V0 = int(65536/2)	#Starting value for DAC
print("Scan range should be in um and step size should be in nm.")

# DAC settings
i2c = busio.I2C(board.SCL, board.SDA, frequency=400_000)
MCP_DAC = adafruit_ad569x.Adafruit_AD569x(i2c)
print("DAC settings are fine!")

# Set the output voltage to specified value.
# Value is a 16-bit number (0-65535) that is used to calculate the output voltage from:
#      Vout =  (VDD*value)/65536
# i.e. the output voltage is the VDD reference scaled by value/65536.
# If persist is true it will save the voltage value in EEPROM 
# so it continues after reset (MCP_DAC.valuedefault is false, no persistence).

V_step = (step_size*V_cal)/100 
StepValue = (V_step*65536)/VDD
StepValue = round(StepValue)

V_scan = ((scanrange)*V_cal)/0.1
ScanValue = (V_scan*65536)/VDD

NumSteps = int(scanrange/step_size*1000)
print("Conversion completed!")

# print("Start initialization!")
# MCP_DAC.value = 1
# print("Value initialization!")
# print(MCP_DAC.value)
# print("MCP_DAC.value works!!!")

StartingPoint = V0 - ScanValue/2	 # set the MCP_DAC.value to the starting point for the scan
MCP_DAC.value = int(StartingPoint)
V_pos = int(StartingPoint)
print("The starting point for the scanning is "+str(V0))

# Acquisition directory
directory = time.strftime("%Y%m%d_%H%M")+"_test"
parent_dir = "/home/pifocus/Documents/" # depends on your system, you need to change this.
Acq_path = os.path.join(parent_dir, directory)
os.mkdir(Acq_path)
print("Directory '% s' is created" % Acq_path)

# Capture data
for i in range(1, NumSteps):
    filename = "Test"+str(i).zfill(4)+".tiff"
    
    raw = picam2.capture_array("raw")	# Capture image
    arr = np.copy(raw[50:350,320:920].view('uint16'))	# 300x300 pixels centred on camera (2nd axis is double for bit reasons)
    im2 = Image.fromarray(arr)		#Convert to 16 bit TIFF
    im2.save(Acq_path+"/"+filename)
    #Optional plotting
    ##plt.imshow(im2)
    ##plt.show()
    
    V_pos = V_pos + StepValue			# Move stage
    MCP_DAC.value = V_pos
    if V_pos >= 65535:								# Check overflow
        V_pos = V_pos - 2*ScanValue
        print("Piezo is out of range.")
    time.sleep(0.1)	# Giue stage time to move
    print("Axial scanning is running. Z position is "+ str(V_pos) + " and " + str(V_pos/65536*2.47/0.1) + " um")
V_pos = V0	# Reset
