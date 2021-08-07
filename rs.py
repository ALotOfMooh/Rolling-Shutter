"""Implementation of Rolling Shutter Effect. For now it works on a desktop PC with attatched camera.
    """
import time
import sys
import cv2
import numpy as np
import screeninfo

screen_id = 0
screen = screeninfo.get_monitors()[screen_id]
width, height = screen.width, screen.height

if len(sys.argv) > 1:
    MODE = sys.argv[1]
direction = "top_to_bottom"
if "lr" in sys.argv:
    direction = "left_to_right"
elif "rl" in sys.argv:
    direction = "right_to_left"
elif "tb" in sys.argv:
    direction = "top_to_bottom"
elif "bt" in sys.argv:
    direction = "bottom_to_top"


num_sections = 80
history = []

def test():
    rgb = np.random.randint(255, size=(1000,700,3),dtype=np.uint8)
    green = np.zeros((50, 700, 3))
    green[:,:,1] = 1
    green *= 255
    rgb[:green.shape[0], :, :] = green

    cv2.imshow('RGB',rgb)
    cv2.imshow('green',green)

def replace_sections_iterative():
    global history
    global direction
#    s = time.time()
    if direction == "top_to_bottom":
        image2 = history[0][ 0:sec_height]
        for i in range(1,num_sections):
            image2=cv2.vconcat([image2,history[i][sec_height*i:sec_height*(i+1)]])
    elif direction == "bottom_to_top":
        image2 = history[0][ 0:sec_height]
        for i in range(1,num_sections):
            image2 = cv2.vconcat([image2,history[-i][sec_height*i:sec_height*(i+1)]])
    elif direction == "left_to_right":
        image2 = history[0][:, 0:sec_height]
        for i in range(1,num_sections):
            image2 = cv2.hconcat([image2,history[i][:, sec_height*i:sec_height*(i+1)]])
    elif direction == "right_to_left":
        image2 = history[0][:, 0:sec_height]
        for i in range(1,num_sections):
            image2 = cv2.hconcat([image2,history[-i][:, sec_height*i:sec_height*(i+1)]])
#    t = time.time() - s
    image2 = add_text(image2)
    return image2

def replace_sections_by_slicing(): #TODO
    global history
    img = np.zeros(history[0].shape)


def add_text(image):
    textdirection = direction.replace("_", " ")
    cv2.putText(image, "Direction: {}".format(textdirection), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 0, 0), thickness=1, lineType=cv2.LINE_AA)
    cv2.putText(image, "Number of Slices: {}".format(num_sections), (50, 85), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 0, 0), thickness=1, lineType=cv2.LINE_AA)


    return image

window_name = 'preview'
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                      cv2.WINDOW_FULLSCREEN)
# cv2.namedWindow("preview", cv2.WINDOW_NORMAL)
# cv2.setWindowProperty("preview", cv2.CV_WND_PROP_FULLSCREEN, 1)
#cv2.namedWindow("preview", cv2.WINDOW_NORMAL);

#cv2.namedWindow("preview", cv2.WINDOW_FREERATIO)
#cv2.namedWindow("preview", cv2.WINDOW_FULLSCREEN );
#cv2.setWindowProperty("preview",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
#   cv2.setWindowProperty("preview", cv2.WND_PROP_FULLSCREEN, cv2.CV_WINDOW_FULLSCREEN)

vc = cv2.VideoCapture(0)


if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
    history.append(frame)
else:
    rval = False

print(frame.shape)
if direction in ("top_to_bottom", "bottom_to_top"):
    sec_height = frame.shape[0] // num_sections
elif direction in ("left_to_right", "right_to_left"):
    sec_height = frame.shape[1] // num_sections

while rval:
    rval, frame = vc.read()
    history.append(frame)

    if len(history) > num_sections:
        history.pop(0)
        img = replace_sections_iterative()
        cv2.imshow("preview", img)




    key = cv2.waitKey(1)
    if key == 27: # exit on ESC
        break
cv2.destroyWindow("preview")
