import time
import cv2
import numpy as np

num_sections = 60
history = []

def test():
    z = np.ones((1, 100))
def replace_sections_iterative():
    global history


cv2.namedWindow("preview", cv2.WINDOW_FREERATIO)
vc = cv2.VideoCapture(0)


if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
    history.append(frame)
else:
    rval = False


sec_height = frame.shape[1] // num_sections
while rval:
    s = time.time()

    rval, frame = vc.read()
    history.append(frame)

    if len(history) > num_sections:
        history.pop(0)
        image2=history[0][0:sec_height]
        for i in range(1,num_sections):
            image2=cv2.vconcat([image2,history[i][sec_height*i:sec_height*(i+1)]])
        cv2.imshow("preview", image2)

    e = time.time()
    print(s-e)



    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break
cv2.destroyWindow("preview")
