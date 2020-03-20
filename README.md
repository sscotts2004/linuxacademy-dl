# linuxacademy-dl

A utility to download Linux Academy (linuxacademy.com) courses, for personal offline use.

> [![Python Version](https://img.shields.io/pypi/pyversions/linuxacademy-dl.svg)](https://pypi.python.org/pypi/linuxacademy-dl)
[![PyPI Version](https://img.shields.io/pypi/v/linuxacademy-dl.svg)](https://pypi.python.org/pypi/linuxacademy-dl)
[![PyPI Status](https://img.shields.io/pypi/status/linuxacademy-dl.svg)](https://pypi.python.org/pypi/linuxacademy-dl)
[![Build Status](https://travis-ci.org/vassim/linuxacademy-dl.svg?branch=master)](https://travis-ci.org/vassim/linuxacademy-dl)

> [![Docker Image](https://img.shields.io/docker/automated/vassim/linuxacademy-dl.svg)](https://hub.docker.com/r/vassim/linuxacademy-dl/)
[![Docker Metadata](https://images.microbadger.com/badges/image/vassim/linuxacademy-dl.svg)](https://microbadger.com/images/vassim/linuxacademy-dl)


### Version
**1.0a4**


### Prerequisites

* Python (>=2.7.9 or >=3.5)
* `pip` (Python Install Packager)
* `ffmpeg` (Cross-platform solution to record, convert and stream audio and video - Optional)
* If there are any missing packages, they will be automatically installed by `pip`


### Preinstall

If you don't have `pip` installed, look at their [install doc](http://pip.readthedocs.org/en/latest/installing.html).
Easy install (if you trust them) is to run their bootstrap installer directly by using:

```
    sudo curl https://bootstrap.pypa.io/get-pip.py | sudo python
```


### Install

`linuxacademy-dl` can be installed using `pip`

```
    pip install linuxacademy-dl
```

or

```
    python -m pip install linuxacademy-dl
```

 In OS X and Linux you need to `sudo` installing `linuxacademy-dl` or you may face some errors

```
sudo pip install linuxacademy-dl
```

Also you need to use `sudo` installing `pip` itself or you run into the same problem.


### Update

`linuxacademy-dl` can be updated using `pip`

```
    pip install --upgrade linuxacademy-dl
```

or

```
    python -m pip install --upgrade linuxacademy-dl
```

 In OS X and Linux you need to `sudo` upgrade `linuxacademy-dl`

 ```
 sudo pip install --upgrade linuxacademy-dl
 ```


### Docker Image
Docker Image for this tool is also available. Just [install the Docker](https://docs.docker.com/engine/installation/) in your machine and use the following command to pull the image:

```
docker pull vassim/linuxacademy-dl
```

Once you've finished pulling the image, you can run the container using the following command. Replace `<download-dir>` with the folder location where you want to put your downloaded contents.

```
docker run -it -v "<download-dir>":"/media" vassim/linuxacademy-dl
```


### Usage

Simply call `linuxacademy-dl` with the full URL to the course page.

```
    linuxacademy-dl https://linuxacademy.com/cp/modules/view/id/course_id
```

or

```
    python -m linuxacademy_dl https://linuxacademy.com/cp/modules/view/id/course_id
```

`linuxacademy-dl` will ask for your username (or email address) and password then start downloading the videos.

By default, `linuxacademy-dl` will download all the course materials directly into the current working directory.  If you wish to have the files downloaded to a specific location, use the `-o /path/to/directory/` parameter.

If you wish, you can include the username/email and password on the command line using the -u and -p parameters.

```
    linuxacademy-dl -u user@domain.com -p $ecRe7w0rd https://linuxacademy.com/cp/modules/view/id/course_id
```

For information about all available parameters, use the `--help` parameter

```
    linuxacademy-dl --help
```


### Advanced Usage

```
usage: linuxacademy-dl [-h] [-u USERNAME] [-p PASSWORD] [-o OUTPUT]
                       [--use-ffmpeg] [-q {1080,720,480,360}] [--debug] [-v]
                       link

Fetch all the lectures for a Linux Academy (linuxacademy.com) course

positional arguments:
  link                  Link for Linux Academy course

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Username / Email
  -p PASSWORD, --password PASSWORD
                        Password
  -o OUTPUT, --output OUTPUT
                        Output directory
  --use-ffmpeg          Download videos from m3u8/hls with ffmpeg
                        (Recommended)
  -q {1080,720,480,360}, --video-quality {1080,720,480,360}
                        Select video quality [default is 1080]
  --debug               Enable debug mode
  -v, --version         Display the version of linuxacademy-dl and exit
```


### Uninstall

`linuxacademy-dl` can be uninstalled using `pip`

```
    sudo pip uninstall linuxacademy-dl
```

You may uninstall the dependant packages too but be aware that those might be required for other Python modules.
