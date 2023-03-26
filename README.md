# Rolling-Shutter
Simulation of rolling shutter effect.

To take a 2-dimensional photo of something is to save the information of light reaching the surface of the photosensitive material. That is only possible with the shutter open. The process of opening or closing the shutter exposes some parts of the photosensitive material to light at different times. 


## RollingShutter.py

### Description
The frames of the output video appear sliced. The number of those slices $n$ is adjustable.
Each output frame is composed of a history of the last $n$ frames that came before. Each $i$-th section of the output frame shows it's corresponding region of the $i$-th last frame.
The first output frame is generated when there are $n$ captured frames stored in a queue. At each new output frame the former oldest stored frame is removed from the history queue and the most recent frame is added to the queue. 
According to the definition of a queue, the history queue works on the principle of *first in first out* (FIFO).

With low $n$ (short history of past frames) the slices appear wider.
The first slice shows the most recent frame at that area.

### Interaction
In my specific setup, the buttons of the game controller are mapped as follows:
* `A` --> Raise number of slices
* `B` --> Reduce number of slices
* `SELECT` --> Show/hide information text
* `up` --> direction: bottom to top
* `down` --> direction: top to bottom
* `left` --> direction: right to left
* `right` --> direction: left to right


### Setup
`.../Rolling-Shutter $` `python RollingShutter.py`

Intended to run on a **Rasperry Pi 4**.
The script assumes a USB-gamecontroller to be connected as well as a USB-camera.
The names of these devices may be different. 
Find out device name listed in:
`$` `cat "/proc/bus/input/devices"`
In **autoplay.py** the names are defined; change them if necessary. (You only have to provide the beginning of the name that can be found uniquely among the other listed device names.)

Make sure **opencv** is installed; install it via:
`sudo apt-get install python-opencv` or `pip install opencv-python`
