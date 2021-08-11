# https://core-electronics.com.au/tutorials/using-usb-and-bluetooth-controllers-with-python.html
"""Script for checking the mapping of the controller."""


#import evdev
from evdev import InputDevice, categorize, ecodes

#creates object 'gamepad' to store the data
#you can call it whatever you like
gamepad = InputDevice('/dev/input/event7')

#prints out device info at start
print(gamepad)

#evdev takes care of polling the controller in a loop
for event in gamepad.read_loop():
    # print(categorize(event))
    print()
    print("code ", event.code)
    print("type ", event.type)
    print("value ", event.value)
    
    print(10*"=")
