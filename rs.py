"""Implementation of Rolling Shutter Effect. For now it works on a desktop PC with attatched camera.
    """
import time
import cv2
import numpy as np

MODE = "desktop"
direction = "left_to_right"
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
    image2=history[0][:, 0:sec_height]
    s = time.time()
    if direction == "top_to_bottom":
        for i in range(1,num_sections):
            image2=cv2.vconcat([image2,history[i][sec_height*i:sec_height*(i+1)]])
    elif direction == "bottom_to_top":
        for i in range(1,num_sections):
            image2=cv2.vconcat([image2,history[-i][sec_height*i:sec_height*(i+1)]])
    elif direction == "left_to_right":
        for i in range(1,num_sections):
            image2=cv2.hconcat([image2,history[i][:, sec_height*i:sec_height*(i+1)]])
    elif direction == "right_to_left":
        for i in range(1,num_sections):
            image2=cv2.hconcat([image2,history[-i][:, sec_height*i:sec_height*(i+1)]])
    t = time.time() - s
    cv2.imshow("preview", image2)

def replace_sections_by_slicing():
    global history
    img = np.zeros(history[0].shape)


cv2.namedWindow("preview", cv2.WINDOW_FREERATIO)
vc = cv2.VideoCapture(0)


if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
    history.append(frame)
else:
    rval = False


sec_height = frame.shape[1] // num_sections

while rval:
    rval, frame = vc.read()
    history.append(frame)

    if len(history) > num_sections:
        history.pop(0)
        replace_sections_iterative()


    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break
cv2.destroyWindow("preview")
