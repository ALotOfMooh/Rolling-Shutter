"""Implementation of Rolling Shutter Effect. For now it works on a desktop PC with attatched camera.
    """
import time
import sys
import cv2
import numpy as np

class RollingShutter:
    def __init__(self, direction, num_sections, windowname="rs"):
        self.direction = None
        self.textdirection = None
        self.set_direction(direction)
        self.num_sections = num_sections
        self.sec_height = None

        self.history = []

        self.vc = cv2.VideoCapture(0)
        self.windowname = windowname


    def set_direction(self, d):
        """Sets new direction.
        @param d: new direction"""
        self.direction = d
        if d == "lr":
            self.textdirection = "left to right"
        elif d == "rl":
            self.textdirection = "right to left"
        elif d == "tb":
            self.textdirection = "top to bottom"
        elif d == "bt":
            self.textdirection = "bottom to top"

    def set_num_sections(self, ns):
        """Sets new number of sections.
        @param ns: new number of sections"""
        self.num_sections = ns

    def replace_sections_iterative(self):
        """Iterative (slow) algorithm that fills the resulting image from the history.
        """
        if self.direction == "tb":
            image = self.history[0][:self.sec_height]
            for i in range(1, self.num_sections):
                image = cv2.vconcat([image, self.history[i][self.sec_height*i:self.sec_height*(i+1)]])
        elif self.direction == "bt":
            image = self.history[0][:self.sec_height]
            for i in range(1, self.num_sections):
                image = cv2.vconcat([image, self.history[-i][self.sec_height*i:self.sec_height*(i+1)]])
        elif self.direction == "lr":
            image = self.history[0][:, :self.sec_height]
            for i in range(1, self.num_sections):
                image = cv2.hconcat([image, self.history[i][:, self.sec_height*i:self.sec_height*(i+1)]])
        elif self.direction == "rl":
            image = self.history[0][:, :self.sec_height]
            for i in range(1,num_sections):
                image = cv2.hconcat([image, self.history[-i][:, self.sec_height*i:self.sec_height*(i+1)]])
        image = self.add_text(image)
        return image


    def show(self):
        cv2.namedWindow(self.windowname, cv2.WND_PROP_FULLSCREEN)
    #    cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
        cv2.setWindowProperty(self.windowname, cv2.WND_PROP_FULLSCREEN,
                              cv2.WINDOW_FULLSCREEN)
        # cv2.namedWindow("preview", cv2.WINDOW_NORMAL)
        # cv2.setWindowProperty("preview", cv2.CV_WND_PROP_FULLSCREEN, 1)
        #cv2.namedWindow("preview", cv2.WINDOW_NORMAL);

        #cv2.namedWindow("preview", cv2.WINDOW_FREERATIO)
        #cv2.namedWindow("preview", cv2.WINDOW_FULLSCREEN );
        #cv2.setWindowProperty("preview",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        #   cv2.setWindowProperty("preview", cv2.WND_PROP_FULLSCREEN, cv2.CV_WINDOW_FULLSCREEN)

        if self.vc.isOpened(): # try to get the first frame
            rval, frame = self.vc.read()
            self.history.append(frame)
        else:
            rval = False

        print(frame.shape)
        if self.direction in ("tb", "bt"):
            self.sec_height = frame.shape[0] // self.num_sections
        elif self.direction in ("lr", "rl"):
            self.sec_height = frame.shape[1] // self.num_sections


        while rval:
            rval, frame = self.vc.read()
            self.history.append(frame)

            if len(self.history) > self.num_sections:
                self.history.pop(0)
                img = self.replace_sections_iterative()
                cv2.imshow(self.windowname, img)

            key = cv2.waitKey(1)
            if key == 27: # exit on ESC
                break
        cv2.destroyWindow(self.windowname)



    def add_text(self, image):
        cv2.putText(image, "Direction: {}".format(self.textdirection), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, fontScale=.5, color=(255, 0, 0), thickness=1, lineType=cv2.LINE_AA)
        cv2.putText(image, "Number of Slices: {}".format(self.num_sections), (50, 85), cv2.FONT_HERSHEY_SIMPLEX, fontScale=.5, color=(255, 0, 0), thickness=1, lineType=cv2.LINE_AA)
        return image




if __name__ == "__main__":
    if len(sys.argv) > 1:
        MODE = sys.argv[1]
    direction = "tb"
    if "lr" in sys.argv:
        direction = "lr"
    elif "rl" in sys.argv:
        direction = "rl"
    elif "tb" in sys.argv:
        direction = "tb"
    elif "bt" in sys.argv:
        direction = "bt"

    RS = RollingShutter(direction, 40)
    RS.show()
