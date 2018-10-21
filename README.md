# Radio Telescope Controller Software #

 [![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=plastic)](https://github.com/dimst23/RadioTelescope_Controller/blob/master/LICENSE)  
 [![Python 3.5+](https://img.shields.io/badge/python-3.5%2B-blue.svg?style=plastic)](https://www.python.org/downloads/release/python-350/)
<p align="center">
<img src="http://www.marysrosaries.com/collaboration/images/0/0b/Radio_Telescope_3_%28PSF%29.png" width="35%" />
</p>

![GitHub last commit (branch)](https://img.shields.io/github/last-commit/dimst23/RadioTelescope_Controller.svg?style=plastic)
[![Build Status](https://img.shields.io/travis/dimst23/RadioTelescope_Controller/master.svg?style=plastic)](https://travis-ci.org/dimst23/RadioTelescope_Controller)

Below you will find installation instructions to get the controller up and running on your own system.
This installation information are not the final ones, since more packages may be used and/or a different approach will be used.

### What is this repository for? ###

* In this repository you will find the necessary files to get the telescope controller software up and running on your system.
* This is still a beta version and it is relatively unstable, but usable.

### How do I get set up? ###

<p>
<img src="https://assets.ubuntu.com/v1/048f7fde-ubuntu_black-orange_hex.jpg" width="10%" />
</p>

* Before proceeding, make sure that `pip` is installed on your system.
* _Installation command for pip_: `$ sudo apt-get install python3-pip`
* Also you will need to run the command `$ sudo apt-get install qt5-defaults`, to make sure you have the required Qt5
commands.
* In the setup process the important part is to install the required package/packages
* Use the `configure.sh` script to install the necessary packages for python and do the initial setup.
* _Configuration command_: `$ (sudo) ./configure.sh`. Note that you may be required to run the script as sudo, in order to properly work.
* After the installation of packages, you can run the main program from the `run.sh` script.
* _Running command_: `$ ./run.sh`. Make sure the run script has executable permissions.
* If executable permissions are needed for the run script type `$ chmod +x run.sh`, and the run the script as described above.

<p>
<img src="https://vignette.wikia.nocookie.net/harimau-malaya/images/c/c9/Windows-logo.png/revision/latest?cb=20160322033433" width="12%" />
</p>

* First of all Python3.5+ needs to be installed. To install Python go to [Python's website](https://www.python.org) and get the latest stable release.
* It is important also to install Qt5, by downloading it from the [Qt's website](https://www.qt.io).
* Make sure that the installation of the Qt5 is in the direcory `C:\Qt` on your computer and you have Qt5.
* Also make sure that `pip` for Python is installed.
* The next step is to open a terminal window in the program direcoty and execute the `configure_windows.bat` file.
* If the execution of the configuration file is successful, then proceed with running the program by executing
`run_windows.bat`.

### Who do I talk to? ###

* Repo owner or admin
