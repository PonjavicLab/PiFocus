# When this runs first time it will show a preview image with the attempted fit
# If you do not see blue/orange lines the fit has failed, use the cursor to check
# good values for the x fit (background, x0, sx, amplitude) and same for y
# Once the fit starts working set plotY to 0 and run through the stack

# If your scan range is too large (nothing to fit) it might struggle
# You can start the for loop in the middle instead to get an idea of fit
# Do this by setting starting value to int(Range/2)

# Import packages that are required for the analysis.
import os
import cv2
import time
import numpy as np
import matplotlib.pyplot as plt

Range = 24  	# Number of files
zval = 1    	# Step size in microns
plotY = 1			# 1 to plot preview of fit, 0 to remove and run through stack
starting = 1	# Start point for scan, if you want to start in the middle set to int(Range/2) instead

# Define the model function. In our case, a 1D Gaussian.
def Gaussian1D(xdata, i0, x0, sX, amp):
    x = xdata
    x0 = float(x0)
    eq = i0+amp*np.exp(-((x-x0)**2/2/sX**2))
    return eq

try:
    from scipy.optimize import curve_fit
except ImportError:
    print("Unable to import curve_fit from scipy.optimize.")

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

#tk.withdraw()  # Prevents a full GUI window from appearing
folder_path = fd.askdirectory()  # Show the folder selection dialog and return the selected folder path
print(f"Selected folder: {folder_path}")

import tifffile
import argparse

init_guess_x = [40,150,50,300]	# Guesses for fits Background, Centre, Width, Amplitude
init_guess_y = [40,150,50,300]	# Guesses for fits
x_c = []
x_sigma = []
y_sigma = []
i_values = []

# To read the acquired images and apply the Gaussian fitting
for i in range(starting,Range):
    i_values.append(i)
    print("Step " + str(i) + " of " + str(Range))
    #Reading the frames
    stacks = folder_path+'/Test'+str(i).zfill(4)+'.tiff'
    if not os.path.exists(stacks):
        raise IOError(f"File {stacks} not found!")    
    img = cv2.imread(stacks,-1)
    im = np.asarray(img).astype(float)
    im = im-np.mean(im)/2	# Remove background
    im[im<10] = 0			# Threshold
   
    # 1D Gaussian
    h1, w1 = im.shape
    x = np.arange(w1)
    y = np.arange(h1)
    
    # Do x fit
    popt, pcov = curve_fit(Gaussian1D, x, np.mean(im,axis=0), p0=init_guess_x, maxfev = 50000)
    x0 = popt[1]
    sx = popt[2]
    init_guess_x.clear()
    init_guess_x.append(popt)
    # Do y fit
    popt, pcov = curve_fit(Gaussian1D, y, np.mean(im,axis=1), p0=init_guess_y, maxfev = 50000)
    y0 = popt[1]
    sy = popt[2]
    
    # Replaces initial guess with final guess
    init_guess_y.clear()
    init_guess_y.append(popt)
   
    x_sigma.append(sx)
    y_sigma.append(sy)
    x_c.append(popt[1])

    # Optional plot, uncomment if you want live preview during calibration that shows fit
    if plotY:
        plt.plot((x0,x0+sx),(y0,y0))
        plt.plot((x0,x0),(y0,y0+sy))
        plt.imshow(im)
        plt.show()
    
# This is just to set the x-axis of the graph to the axial values
StepSize = zval
i_values = np.array(i_values)
z_values = i_values*StepSize
z_values = z_values.tolist() # This should be based on True/False direction

# Save calibration data
dataArr = [z_values, x_sigma, y_sigma]
np.savetxt(folder_path+"Test.csv", np.transpose(dataArr), delimiter=",")

# Print final guesses that can be used in stabilisation
print("X guess: " + str(init_guess_x))
print("Y guess: " + str(init_guess_y))

# Plot the curves
plt.plot(z_values, x_sigma, 'b8', markersize=2, label="σx")
plt.plot(z_values, y_sigma, 'r8', markersize=2, label="σy")
plt.plot(z_values, np.subtract(x_sigma,y_sigma), '--k', markersize=2, label="σy - σx")
plt.grid(True)
plt.xlabel("z-Position (µm)")
plt.ylabel("Width (px)")
plt.legend()
plt.show()