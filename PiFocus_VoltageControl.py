# Import packages that are required for the analysis.
import asi
import numpy as np
import cv2
import time
import math
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Set up the z-stage 
import board
import busio
import adafruit_ad569x
i2c = busio.I2C(board.SCL, board.SDA, frequency=400_000)
dac = adafruit_ad569x.Adafruit_AD569x(i2c)

# Start at some known value of voltage/z position
pos = 65536/2			# Current position
dac.value = 65536/2		# Half of VDD if 3V then 1.5V = 15 micron
scaling = 65536/30000	# Conversion DAC value to nm

# Set up the camera
###################

# Define the model function. In our case, a 1D Gaussian.
def Gaussian1D(xdata, i0, x0, sX, amp):
    x = xdata
    x0 = float(x0)
    eq = i0+amp*np.exp(-((x-x0)**2/2/sX**2))
    return eq

# Variables
gg = []
mTot = 0
first = 1
frame_count = 1

x_sigma = []
y_sigma = []
init_guess_x = [1200,250,50,300]	# Guesses for fits
init_guess_y = [1200,150,50,300]

tt = time.time()

while (time.time()-tt)<3600:
    
    # Your gode here for getting image
    #im = getImage
    
    # If data is in double wide 8-bit matrix 
    im = im.reshape(width,height*2).view('uint16')

    im = im-np.mean(im)/2	# Remove background
    im[im<10] = 0			# Threshold
        
    # 1D Gaussian
    h1, w1 = im.shape
    x = np.arange(w1)
    y = np.arange(h1)

    # Do x fit
    popt, pcov = curve_fit(Gaussian1D, x, np.mean(im,axis=0), p0=init_guess_x, maxfev = 50000)
    
    init_guess_x.clear()
    init_guess_x.append(popt)
    
    x_sigma.append(popt[2])
    xT = popt[2]	# Store x value
    sx = xT			# Store x value

    # Do y fit
    popt, pcov = curve_fit(Gaussian1D, y, np.mean(im,axis=1), p0=init_guess_y, maxfev = 50000)
    
    init_guess_y.clear()
    init_guess_y.append(popt)

    y_sigma.append(popt[2])
    gg.append(xT-popt[2])	# Store x-y control value
    sy = sx-popt[2]			# Store y value

    # Movement stuff
    if first:
        first = 0
        setP = sy-sx	# Control signal setpoint
 
    # Movement stuff
    if abs(mTot)<3000:	# This controls max movement for safety
        error = (sy-sx)-setP
        
        # We do proportional motion but min motion with 16 bit is about 0.5 nm so let's do that
        # Ignore this for now
        if(abs(error)>1):	# Set a limit to how much motion to perform
            mm = 1
        else:
            mm = abs(error)	#If below limit, motion is proportional
        
        # MOVEMENT MOVEMENT MOVEMENT MOVEMENT
        # All these numbers depend on calibration and setup
        # Direction +- depends on your cylindrical lens setup
        if (error)>0.08:		# Minimum threshold for movement	
            mTot = mTot + 1	# Monitor total movement
            # Perform movement (set voltage), we usually move max 400pm in one frame
                #ctl.Move(d_handle, channel, int(mm*40*100), 0)
            # Voltage equivalent would be something like this
            pos = pos + 1
            dac.value = pos
            
        elif (error)<-0.08:		# Minimum threshold for movement
            mTot = mTot - 1	# Monitor total movement
            # Perform movement (set voltage), we usually move max 400pm in one frame
                #ctl.Move(d_handle, channel, int(-mm*40*100), 0)
            # Voltage equivalent would be something like this
            pos = pos - 1
            dac.value = pos
            
        # This stops our controller but can't do this with voltage
        #else:
        #    ctl.Move(d_handle, channel, 0, 0)
        # MOVEMENT MOVEMENT MOVEMENT MOVEMENT
        
    else:
        print("Out of range")
    
    # Every 100 frames, report things
    if frame_count % 100 == 0:
        print("MAX: " + str(np.max(im)))
        print("gg: " + str(sy-sx))
        print("Total Time: " + str(time.time()-tt))
        print("Total Mot: " + str(mTot))

# Close camera
asi.ASIStopVideoCapture(info.CameraID)
# Print fps
print(frame_count/(time.time()-tt))
# Optional save control signal
#np.savetxt("drift60min.csv",np.transpose(gg),delimiter = ',')
