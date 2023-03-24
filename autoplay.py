
def find_devices(startstr):
    dev_path = "/proc/bus/input/devices"
    with open(dev_path, 'r') as f:
        content = f.read()
    #print(content)
    startidx = content.find(startstr)
    cropstr = content[startidx:]
    endstr = "Bus"
    endidx = cropstr.find(endstr)
    cropstr = cropstr[:endidx]


    #endidx = content.find(endstr)

    eventidx = cropstr.find("event")
    eventstr = cropstr[eventidx:eventidx+7]
    eventstr = eventstr.strip()
    print(eventstr)
    return eventstr

# Find out camera device Name in "/proc/bus/input/devices"
startstr = "UVC Camera" #"HDA Intel PCH Mic"
camera_dev = find_devices(startstr)
gamepad_dev = find_devices("USB Gamepad")
