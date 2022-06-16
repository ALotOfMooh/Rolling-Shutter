

file = "/proc/bus/input/devices"

with open(file, 'r') as f:
    content = f.read()
#print(content)

startstr = "HDA Intel PCH Mic"
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
