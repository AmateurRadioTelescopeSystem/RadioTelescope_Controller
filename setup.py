try:
    import setuptools
except ImportError:
    print("=========================================================")
    print(" Software requires setuptools for installing.            ")
    print(" You can install setuptools using pip:                   ")
    print("    $ pip install setuptools                             ")
    print("=========================================================")
    exit(1)

from setuptools import setup
import Core
import os

packages = [
    "Core",
    "Core.Astronomy",
    "Core.Client",
    "Core.Configuration",
    "Core.GUI",
    "Core.Handlers",
    "Core.Server",
    "Core.Stellarium",
]

data_files = [
    ('Icons', [os.path.abspath('calibration.png'),
               os.path.abspath('location.png'),
               os.path.abspath('manControl.png'),
               os.path.abspath('Net.png'),
               os.path.abspath('planetary.png'),
               os.path.abspath('radiotelescope.png'),
               os.path.abspath('skyScanning.png'),
               os.path.abspath('TCP.png'),
               os.path.abspath('GUI_Images/ScanExplanation.png')
               ]),
    ('UI_Files', [os.path.abspath('Calibration.ui'),
                  os.path.abspath('Location.ui'),
                  os.path.abspath('ManualControl.ui'),
                  os.path.abspath('MapsDialog.ui'),
                  os.path.abspath('PlanetaryObject.ui'),
                  os.path.abspath('RadioTelescope.ui'),
                  os.path.abspath('SkyScanning.ui'),
                  os.path.abspath('TCPSettings.ui')
                  ]),
]

setup(
    name="Radio_Telescope_Controller",
    version=Core.__version__,
    description="Control software for a radio telescope installation. It is used with a Raspberry Pi, "
                "controlling the antenna motors.",
    author="Dimitrios Stoupis",
    author_email="dstoupis@auth.gr",
    maintainer="Dimitrios Stoupis",
    maintainer_email="dstoupis@auth.gr",
    license="GPLv3",
    packages=packages,
    data_files=data_files,
    classifiers=[
        'Development Status :: Beta',
        'Environment :: Window GUI',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Amateur Radio astronomers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Communications :: Ham Radio',
    ],
)
