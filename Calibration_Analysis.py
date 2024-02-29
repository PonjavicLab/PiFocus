# Import packages that are required for the analysis.
import os
import cv2
import time
import numpy as np

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

# Define the model function. In our case, a 2D/1D Gaussian.
def Gaussian(xdata, i0, x0, y0, sX, sY, amp):
    (x, y) = xdata
    x0 = float(x0)
    y0 = float(y0)
    eq =  i0+amp*np.exp(-((x-x0)**2/2/sX**2 + (y-y0)**2/2/sY**2))
    return eq.ravel()

try:
    from scipy.optimize import curve_fit
except ImportError:
    print("Unable to import curve_fit from scipy.optimize.")

from tkinter import Tk
from Tk.filedialog import askdirectory

Tk().withdraw()  # Prevents a full GUI window from appearing
folder_path = askdirectory()  # Show the folder selection dialog and return the selected folder path
print(f"Selected folder: {folder_path}")

import tifffile
import argparse

init_guess = [100,250,170,40,40,12000]
x_c = []
x_sigma = []
y_sigma = []
i_values = []

# To read the acquired images and apply the Gaussian fitting
for i in range(1,101):
    i_values.append(i)
    #Reading the frames
    stacks = folder_path+'Test'+str(i).zfill(4)+'.tif'
    if not os.path.exists(stacks):
        raise IOError(f"File {stacks} not found!")    
    img = cv2.imread(stacks,-1)
    im = np.asarray(img).astype(float)
   
    h1, w1 = im.shape
    x, y = np.meshgrid(np.arange(w1),np.arange(h1))
    
    # fitting the model function
    popt, pcov = curve_fit(Gaussian, (x, y), im.ravel(), p0=init_guess, maxfev = 5000)
    
    # Get the σx and σy
    popt[3] = np.abs(popt[3])
    popt[4] = np.abs(popt[4])
    
    init_guess.clear()
    init_guess.append(popt)
   
    dd = Gaussian((x,y),*popt)
    dd = dd.reshape(h1,w1)
   
    x_sigma.append(popt[3])
    y_sigma.append(popt[4])
    x_c.append(popt[1])

    plt.plot((popt[1],popt[1]+popt[3]),(popt[2],popt[2]))
    plt.plot((popt[1],popt[1]),(popt[2],popt[2]+popt[4]))
    plt.imshow(im)
    plt.show()
    
    # print(popt[3])
    # print(popt[4])
    # print(popt[1])
    # print(popt[4]-popt[3])
    
# This is just to set the x-axis of the graph to the axial values
StepSize = 0.2
i_values = np.array(i_values)
z_values = i_values*StepSize
z_values = z_values.tolist() # This should be based on True/False direction

dataArr = [z_values, x_sigma, y_sigma, x_c]
np.savetxt(dp+"Test.csv", np.transpose(dataArr), delimiter=",")

# Plot the curves
plt.plot(z_values, x_sigma, 'b8', markersize=2, label="σx")
plt.plot(z_values, y_sigma, 'r8', markersize=2, label="σy")
plt.plot(z_values, np.subtract(x_sigma,y_sigma), '--k', markersize=2, label="σy - σx")
plt.grid(True)
plt.xlabel("z-Position (µm)")
plt.ylabel("Width (px)")
plt.legend()
plt.show()
