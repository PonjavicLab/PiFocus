[![DOI:10.1101/2024.01.15.575442](http://img.shields.io/badge/DOI-10.1364/OE.520845-B31B1B.svg)](<https://doi.org/10.1364/OE.520845>)
[![Contributors](https://img.shields.io/github/contributors-anon/PonjavicLab/PiFocus)](https://github.com/PonjavicLab/PiFocus/graphs/contributors)
[![CC BY 4.0][cc-by-shield]][cc-by]
[![GitHub stars](https://img.shields.io/github/stars/PonjavicLab/PiFocus?style=social)](https://github.com/PonjavicLab/PiFocus/)
[![GitHub forks](https://img.shields.io/github/forks/PonjavicLab/PiFocus?style=social)](https://github.com/PonjavicLab/PiFocus/)

# PiFocus: Acquisition, Analysis and Hardware Control

<p align="justify">
In this repository, you will find a semi-protocol detailing the process for setting up the PiFocus system. The collection encompasses designs, hardware specifications, and software components that are all listed below. Additionally, there are scripts available for replicating calibration outcomes, along with the necessary Python code for conducting autofocus operations and a Beanshell script to perform autofocusing through MicroManager. For a comprehensive understanding of the entire project, please refer to the provided documentation link.
</p>

## Materials and Methods
   
### 1. Set up the Raspberry Pi 4
1.1. 16-bit DAC
To get the MAX5216 SPI DAC to work with the Raspberry Pi.

```
sudo apt-get install i2c-tools
pip3 install adafruit-blinka
sudo pip3 install adafruit-circuitpython-mcp4725
```
> [!TIP]
> If you want to detect the DAC to make sure it is connected. Run in the Raspberry Pi terminal:

```
sudo i2cdetect -y 1
```

1.2. Raspberry Pi camera (OV9281)
Change the config file with: `sudo nano /boot/config.txt` and add the following lines to the end:

```
dtparam=i2c_arm=on
dtparam=i2c1=on
```

exit with ctrl-x and save with y.

Next need to enable the camera and I2C interface. Go to the Raspberry Pi terminal and type:

```
sudo raspi-config
```

Then go to the interfacing options. Enable the camera and I2C.

1.3. Install dependencies

To install opencv-python:
```
suod apt install python3-opencv
```
> [!TIP]
> if you need to downgrade opencv:

```
pip3 install git+https://github.com/opencv/opencv-python
```

In the Raspberry Pi terminal, run the following commands:

```
sudo apt-get install libcblas-dev
```

```
sudo apt-get install libhdf5-dev
```

```
sudo apt-get install libhdf5-serial-dev
```

```
sudo apt-get install libatlas-base-dev
```

```
sudo apt-get install libjasper-dev
```

```
sudo apt-get install libqtgui4
```

```
sudo apt-get install libqt4-test
```

### 2. Optomechanics and Optics
- Multimode laser diode (OFL311, OdicForce Lasers)
- Single-mode fibre (P1-780A-FC-1, Thorlabs)
- Beamsplitter (CCM1-BS014/M, Thorlabs)
- NIR shortpass dichroic (#69-196, Edmund Optics)
- NIR longpass filter (FELH0800, Thorlabs)
- Cylindrical lens (f = 150 - 1000 mm)
- Tube lens
- Camera (ZWO ASI290MM/OV9281)

### 3. Calibration
For calibration, a z-image stack should be acquired by scanning the stage in the axial direction and capturing an image for each step to form the calibration stack. The z-stack scan range and step size should be chosen in a way that ensures the entire range of astigmatism is covered, encompassing the full range of potential focal plane deviations. The stack can be acquired through micromanager.

Using the calibration analysis code, the calibration curve for the acquired z-stack can be obtained. This curve maps the relationship between the axial position of the sample and the corresponding beam shape, which is crucial for the focus stabilisation process.

> [!NOTE]
> The calibration curve does not change significantly over time other than if corrections are made using the correction collar. If corrections are made, the sensitivity and thus relative movements remain unchanged. However, for absolute positioning a new calibration would have to be carried out.

## Required libraries

```
   SciPy
   NumPy
   Matplotlib
   OpenCV
   tkinter
   tifffile
   argparse
```

## **Cite our paper**
[PiFocus paper on Optics Express](https://opg.optica.org/oe/fulltext.cfm?uri=oe-32-8-13331&id=548369)

Amir Rahmani, Tabitha Cox, Akhila Thamaravelil Abhimanue Achary, and Aleks Ponjavic, "Astigmatism-based active focus stabilisation with universal objective lens compatibility, extended operating range and nanometer precision," Opt. Express 32, 13331-13341 (2024)

[Zenodo repository for supporting datasets](https://zenodo.org/doi/10.5281/zenodo.10726262)
Rahmani, A., Cox, T. and Ponjavic, A. "PiFocus: Acquisition, Analysis and Hardware Control," Zenodo, (2023)

## Issues
In the event that you come across any difficulties, please don't hesitate to file an issue and make sure to provide a thorough description of the problem.

## License
This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
