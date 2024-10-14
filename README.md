[![DOI:10.1101/2024.01.15.575442](http://img.shields.io/badge/DOI-10.1364/OE.520845-B31B1B.svg)](<https://doi.org/10.1364/OE.520845>)
[![Contributors](https://img.shields.io/github/contributors-anon/PonjavicLab/PiFocus)](https://github.com/PonjavicLab/PiFocus/graphs/contributors)
[![GitHub stars](https://img.shields.io/github/stars/PonjavicLab/PiFocus?style=social)](https://github.com/PonjavicLab/PiFocus/)
[![GitHub forks](https://img.shields.io/github/forks/PonjavicLab/PiFocus?style=social)](https://github.com/PonjavicLab/PiFocus/)

# PiFocus: Acquisition, Analysis and Hardware Control

<p align="justify">
In this repository, you will find a semi-protocol detailing the process for setting up the PiFocus system. The collection encompasses designs, hardware specifications, and software components that are all listed below. Additionally, there are scripts available for replicating calibration outcomes, along with the necessary Python code for conducting autofocus operations and a Beanshell script to perform autofocusing through MicroManager. For a comprehensive understanding of the entire project, please refer to the provided documentation link.
</p>

## Optics
See paper for full optical setup instructions.

In short, setup multimode laser, pass through single-mode fiber, then collimate beam and direct through beam splitter and finally into objective lens. Use a tube lens (any 200 mm lens will do) after the beam splitter to focus the light on the camera. Check that a focused spot can be visualised (see next section for how to use Raspberry PI). When the sample is in focus the camera can be moved to ensure that the autofocus focal point aligns with the imaging focal point. Then insert a cylindrical lens near the tube lens and observe the astigmatic beam shape. 

- Multimode laser diode (OFL311, OdicForce Lasers)
- Single-mode fibre (P1-780A-FC-1, Thorlabs)
- Beamsplitter (CCM1-BS014/M, Thorlabs)
- NIR shortpass dichroic (#69-196, Edmund Optics)
- NIR longpass filter (FELH0800, Thorlabs)
- Cylindrical lens (f = 150 - 1000 mm)
- Tube lens
- Camera (ZWO ASI290MM/OV9281)

<img src="https://github.com/PonjavicLab/PiFocus/blob/main/SI_Figures/S4.png" width="360" height="300">

## Software
The simplest and fastest way to get started with PiFocus on a Raspberry Pi is by imaging the Raspberry Pi SD card using our preloaded image ([download the image file](https://leeds365-my.sharepoint.com/:u:/g/personal/phyapona_leeds_ac_uk/EXfXRBo5S5NMkREcIQCHJQ4B3cDREjjXeYYMZ3RC_1PfZw?e=JTbmnT)).
This avoids having to install all the custom python packages and system configuration required to run PiFocus code.

Instructions for both Windows and Mac can be found in the links below.

Check [here](https://medium.com/@reishim0731/transferring-the-raspberry-pi-os-to-a-micro-sd-card-on-the-mac-terminal-b572266bf79b) for MacOS.

Check [here](https://raspberry-projects.com/pi/pi-operating-systems/win32diskimager) for Windows.

> [!NOTE]
> Currently, a PiFocus_OVCam image is available which works with the OV9281 camera and the AD5693R 16-bit DAC for piezo offset control.


### 16-bit DAC output for piezo control

Full guide [here](https://learn.adafruit.com/adafruit-ad5693r-16-bit-dac-breakout-board/circuitpython-and-python).

Put your soldered AD5693R onto a breadboard (or connect directly to PI) and connect as described in the guide. The terminal will be connected to your Piezo voltage offset.

<img src="https://github.com/PonjavicLab/PiFocus/blob/main/SI_Figures/Picture1.png" width="360" height="220">

[(image credit)](https://www.mouser.com/datasheet/2/737/adafruit_ad5693r_16_bit_dac_breakout_board-3402554.pdf)

### Raspberry PI
If using the recommended OV9281 camera that is compatible with Raspberry PI, upload the SD card image from the PiFocus github page and run the Raspberry PI imager. 
 
This is setup with a PiFocus user with the password pifocus. 
 
To use the camera, go into terminal 

<img src="https://github.com/PonjavicLab/PiFocus/blob/main/SI_Figures/Pic2.png" width="380" height="200">

and type:

```
libcamera-hello 
```
This will stream an image while adjusting exposure time which will help you find the beam on the camera. 
 
Everything that follows will be using python scripts on the desktop. 
Right-click [“OV_preview.py”](https://github.com/PonjavicLab/PiFocus/blob/main/PiFocus_OVCam/OV_preview.py) and open using Thonny (or any Python compiler of choice).

<img src="https://github.com/PonjavicLab/PiFocus/blob/main/SI_Figures/Picture3.png" width="380" height="200">

Run the script and you will see a similar preview as you did with libcamera, make sure the beam is close to the centre. 
 
Next, run the [“OV_Volt_Calib.py”](https://github.com/PonjavicLab/PiFocus/blob/main/PiFocus_OVCam/OV_Volt_Calib.py) script. The main variables to set here is the scan range and step size. Typically 200 nm and 10 micron is a good starting point. Note that you need to set the voltage to central (2.47V/2) before starting as described in the code comments. This will create a folder of images at different z positions. 
 
The calibration scan can be analysed with [“Calibration_analysis.py”](https://github.com/PonjavicLab/PiFocus/blob/main/PiFocus_OVCam/Calibration_Analysis.py) that will output sigmax-sigmay as a function of z, make sure you input the correct z step here. It is important to make sure that your initial gaussian fit parameters are reasonable, if you are not getting any output play around with these. The code will show you an image along with the fit so it will be clear if parameters are wrong. A good starting point is to alignyour beam in focus and take note of background, size and amplitude then enter those values into the parameter guess. The gradient from the calibration script can then be used to convert the sigmax-sigmay control signal into nm.
 
If you want to know the sensitivity of your setup, acquire a timelapse using [“OV_timelapse.py”](https://github.com/PonjavicLab/PiFocus/blob/main/PiFocus_OVCam/OV_Timelapse.py). This will output the control signal over time and the std of the control signal. If you divide this by the gradient from your calibration scan you get the resolution in nm. 

Now everything is setup to run the autofocus script [“OV_Volt_Stabilisation.py”](https://github.com/PonjavicLab/PiFocus/blob/main/PiFocus_OVCam/OV_Volt_Stabilisation.py). By default this is set to 300x300 pixels, that will run at about 150 Hz. Important things to set here are the Gaussian guess parameters and to make sure that the direction of autofocus is correct. It will be clear if this is wrong as the control signal error will rapidly increase over time, so reverse the direction if this is the case.  

[comment]: <> (To get the MAX5216 SPI DAC to work with the Raspberry Pi.)
[comment]: <> (```)
[comment]: <> (sudo apt-get install i2c-tools)
[comment]: <> (pip3 install adafruit-blinka)
[comment]: <> (sudo pip3 install adafruit-circuitpython-mcp4725)
[comment]: <> (```)

> [!TIP]
> If you want to detect the DAC to make sure it is connected. Run in the Raspberry Pi terminal:

```
sudo i2cdetect -y 1
```

## Cite our paper
[PiFocus paper on Optics Express](https://opg.optica.org/oe/fulltext.cfm?uri=oe-32-8-13331&id=548369)

Rahmani, A., Cox, T., Achary, A. T. A., and Ponjavic, A., "Astigmatism-based active focus stabilisation with universal objective lens compatibility, extended operating range and nanometer precision," Opt. Express 32, 13331-13341 (2024)

```
@article{rahmani_astigmatism-based_2024,
	title = {Astigmatism-based active focus stabilisation with universal objective lens compatibility, extended operating range and nanometer precision},
	volume = {32},
	issn = {1094-4087},
	url = {https://opg.optica.org/abstract.cfm?URI=oe-32-8-13331},
	doi = {10.1364/OE.520845},
	language = {en},
	number = {8},
	urldate = {2024-03-27},
	journal = {Optics Express},
	author = {Rahmani, Amir and Cox, Tabitha and Achary, Akhila Thamaravelil Abhumanue and Ponjavic, Aleks},
	month = apr,
	year = {2024},
	pages = {13331},
}
```

[Zenodo repository for supporting datasets](https://zenodo.org/doi/10.5281/zenodo.10726262)

Rahmani, A., Cox, T. and Ponjavic, A. "PiFocus: Acquisition, Analysis and Hardware Control," Zenodo, (2023)

## Issues
In the event that you come across any difficulties, please don't hesitate to file an issue and make sure to provide a thorough description of the problem.

Or email us at:

📧 pyara@leeds.ac.uk (Amir Rahmani)

📧 a.ponjavic@leeds.ac.uk (Dr. Aleks Ponjavic)
