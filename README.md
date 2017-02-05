# Spectrometer #

## What is this repository for

* Build a simple GUI for Ocean Optics spectrometer

## Hardware & Software

* Ocean Optics spectrometer (Tested on QE65000)
* Anaconda Python 3.5
* PyQt4

## How to set up spectrometer

* https://github.com/ap--/python-seabreeze

## Usage
```
$ python spectrometer.py -h

usage: python spectrometer.py [-h] [-d]

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  Use dummy module to debug
```

## To do

* Add absorbance calculation
* Plot multiple spectra

## Acknowlegements

Thanks to [Andreas Poehlmann](https://github.com/ap--) for developing python support for Ocean Optics instruments.
