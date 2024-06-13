# Import packages that are required for the analysis.
import numpy as np
import cv2
import time
import math
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Import camera stuff
from PIL import Image
from picamera2 import MappedArray, Picamera2
from picamera2.encoders import Encoder
from picamera2.outputs import CircularOutput

# Set up the camera
size = (400, 400)
picam2 = Picamera2()
picam2.encode_stream_name = "raw"
video_config = picam2.create_video_configuration(raw={'format': 'R10', 'size': size}, controls = {"FrameDurationLimits": (500, 500), "ExposureTime": 60, "AnalogueGain": 1})
picam2.configure(video_config)
encoder = Encoder()

# Define the model function. In our case, a 1D Gaussian.
def Gaussian1D(xdata, i0, x0, sX, amp):
    x = xdata
    x0 = float(x0)
    eq = i0+amp*np.exp(-((x-x0)**2/2/sX**2))
    return eq

# Variables
global gg, times, t0
gg = []
times = []

x_sigma = []
y_sigma = []
init_guess_x = [1200,250,50,300]	# Guesses for fits
init_guess_y = [1200,150,50,300]

global frame_count
global im
frame_count = 0

tt = time.time()
t0 = tt

def apply_timestamp(request):
    global frame_count, im, first, mTot, setP, pos, gg, times

    with MappedArray(request, "raw") as m:
    
        # Get image and convert to 16 bit (technically 10 bit)
        tt = time.time()
        times.append(tt-t0)
        frame_count = frame_count + 1
        im = np.copy(m.array[50:350,320:920].view('uint16'))	# 300x300 pixels centred on camera (2nd axis is double for bit reasons)

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
        
        # Every 100 frames, report things
        if frame_count % 100 == 0:
            print("MAX: " + str(np.max(im)))
            print("gg: " + str(sy-sx))

# main control sequence
picam2.pre_callback = apply_timestamp
tt = time.time()	# Set time
picam2.start_recording(encoder,CircularOutput())	# Start running
time.sleep(5)	# Run for 5 seconds
picam2.stop_recording() # End recording

# Print fps
print("FPS: " + str(frame_count/(time.time()-tt)))

# Plot control signal
plt.plot(times, gg, 'b8', markersize=2, label="σx")
plt.grid(True)
plt.xlabel("Time (s)")
plt.ylabel("Width (px)")
plt.show()

# Report std (divide this by gradient from calibration to get precision in nm)
print("Standard deviation of control signal: " + str(np.std(gg)))

# Optional save control signal
#np.savetxt("drift60min.csv",np.transpose(gg),delimiter = ',')
