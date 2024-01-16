# Import packages that are required for the analysis.
import asi
import numpy as np
import cv2
import time
import matplotlib.pyplot as plt
import math
import smaract.ctl as ctl
from scipy.optimize import curve_fit

# set up the z-stage 
#ms and pm
buffer = ctl.FindDevices()
locators = buffer.split("\n")
d_handle = ctl.Open(locators[0])
channel = 2
ctl.SetProperty_i32(d_handle, channel, ctl.Property.MAX_CL_FREQUENCY, 6000)
ctl.SetProperty_i32(d_handle, channel, ctl.Property.HOLD_TIME, 1000)
ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_VELOCITY, 5000000)
ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_ACCELERATION, 100000000)
ctl.SetProperty_i32(d_handle, channel, ctl.Property.MOVE_MODE, ctl.MoveMode.CL_RELATIVE)

ctl.SetProperty_i32(d_handle, channel, ctl.Property.STEP_FREQUENCY, 20000)
ctl.SetProperty_i32(d_handle, channel, ctl.Property.STEP_AMPLITUDE, 10000)
# ctl.SetProperty_i32(d_handle, channel, ctl.Property.MOVE_MODE, ctl.MoveMode.STEP)

# Set up the camera (here is for ZWO ASI290MM)
width = 200
height = 200
asi.ASIGetNumOfConnectedCameras()
rtn, info = asi.ASIGetCameraProperty(0)
frame_size = width * height
asi.ASIOpenCamera(info.CameraID)
asi.ASIInitCamera(info.CameraID)
asi.ASISetROIFormat(info.CameraID, width, height, 2, asi.ASI_IMG_RAW16)
asi.ASISetStartPos(info.CameraID, 250, 80)
asi.ASISetControlValue(info.CameraID, asi.ASI_BANDWIDTHOVERLOAD, 65, asi.ASI_FALSE)
asi.ASISetControlValue(info.CameraID, asi.ASI_HIGH_SPEED_MODE, 1, asi.ASI_FALSE)
asi.ASISetControlValue(info.CameraID, asi.ASI_EXPOSURE, 6000, asi.ASI_FALSE)
asi.ASISetControlValue(info.CameraID, asi.ASI_GAIN, 300, asi.ASI_FALSE)
asi.ASIDisableDarkSubtract(info.CameraID)
asi.ASIStartVideoCapture(info.CameraID)

# Define the model function. In our case, a 1D Gaussian.
def Gaussian1D(xdata, i0, x0, sX, amp):
    x = xdata
    x0 = float(x0)
    eq = i0+amp*np.exp(-((x-x0)**2/2/sX**2))
    return eq

# cv2.namedWindow('video', cv2.WINDOW_NORMAL)
# cv2.resizeWindow('video', 100, 100)

gg = []
mTot = 0
first = 1
frame_count = 1

x_sigma = []
y_sigma = []
init_guess_x = [1200,250,50,300]
init_guess_y = [1200,150,50,300]

tt = time.time()

while (time.time()-tt)<3600:
# while (frame_count)<400:
#     dropped_frame_count = asi.ASICheck(asi.ASIGetDroppedFrames(info.CameraID))
    (rtn, im) = asi.ASIGetVideoData(info.CameraID, frame_size*2, 1000)
#     print(im.shape)
#     print(rtn)
    if rtn == 11:
        print("TIMEOUT!")
    if rtn == 13:
        print("BUFFER!")
    if rtn == 0:
        frame_count += 1
#         print(frame_count)
#         dd = im
        im = im.reshape(width,height*2).view('uint16')
#         cv2.imwrite("test"+str(frame_count).zfill(4)+".tif",im)
#         print(np.mean(im))
        im = im-np.mean(im)/2
#         im[im60000] = 0
#         statistics.median(im.ravel())
        im[im<10] = 0
        
        #1D Gaussian
        h1, w1 = im.shape
        x = np.arange(w1)
        y = np.arange(h1)

        popt, pcov = curve_fit(Gaussian1D, x, np.mean(im,axis=0), p0=init_guess_x, maxfev = 50000)
        
        init_guess_x.clear()
        init_guess_x.append(popt)
        
        x_sigma.append(popt[2])
        xT = popt[2]
        sx = xT

        popt, pcov = curve_fit(Gaussian1D, y, np.mean(im,axis=1), p0=init_guess_y, maxfev = 50000)
        
        init_guess_y.clear()
        init_guess_y.append(popt)

        y_sigma.append(popt[2])
        gg.append(xT-popt[2])
        sy = sx-popt[2]

        #Movement stuff
        if first:
            first = 0
            setP = sy-sx
     
        #Movement stuff
        if abs(mTot)<3000:
            error = (sy-sx)-setP
            if(abs(error)>1):
                mm = 1
            else:
                mm = abs(error)
            # MOVEMENT MOVEMENT MOVEMENT MOVEMENT               
            if (error)>0.08:
                mTot = mTot + 0.1
                ctl.Move(d_handle, channel, int(mm*40*100), 0)
            elif (error)<-0.08:
                mTot = mTot - 0.1
                ctl.Move(d_handle, channel, int(mm*-40*100), 0)
            else:
                ctl.Move(d_handle, channel, 0, 0)
            # MOVEMENT MOVEMENT MOVEMENT MOVEMENT  
        else:
            print("Out of range")
            
    if frame_count % 100 == 0:
        print("MAX: " + str(np.max(im)))
        print("gg: " + str(sy-sx))
        print("Total Time: " + str(time.time()-tt))
        print("Total Mot: " + str(mTot))
    
asi.ASIStopVideoCapture(info.CameraID)
print(frame_count/(time.time()-tt))
# np.savetxt("drift60min.csv",np.transpose(gg),delimiter = ',')
