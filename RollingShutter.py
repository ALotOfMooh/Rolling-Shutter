# https://core-electronics.com.au/tutorials/using-usb-and-bluetooth-controllers-with-python.html
# https://python-evdev.readthedocs.io/en/latest/tutorial.html
"""Implementation of Rolling Shutter Effect. For now it works on a desktop PC with attatched camera.
    """
import time
import sys
import cv2
import numpy as np

from threading import Thread


#MODE = "desktop"
MODE = "controller"
direction = "tb"

if MODE == "controller":
    #import evdev
    from evdev import InputDevice, categorize, ecodes

class RollingShutter(Thread):
    def __init__(self, controller, windowname="rs"):
        super().__init__(name="rs", target=self.show)
        self.controller = controller
    #    self.direction = None
    #    self.textdirection = None
        self.sec_height = None

        self.history = []

        self.vc = cv2.VideoCapture(0)
        self.windowname = windowname




    def replace_sections_iterative(self):
        """Iterative (slow) algorithm that fills the resulting image from the history.
        """
        if self.controller.direction_status == "tb":
            image = self.history[0][:self.sec_height]
            for i in range(1, self.controller.num_sections):
                image = cv2.vconcat([image, self.history[i][self.sec_height*i:self.sec_height*(i+1)]])
        elif self.controller.direction_status == "bt":
            image = self.history[0][:self.sec_height]
            for i in range(1, self.controller.num_sections):
                image = cv2.vconcat([image, self.history[-i][self.sec_height*i:self.sec_height*(i+1)]])
        elif self.controller.direction_status == "lr":
            image = self.history[0][:, :self.sec_height]
            for i in range(1, self.controller.num_sections):
                image = cv2.hconcat([image, self.history[i][:, self.sec_height*i:self.sec_height*(i+1)]])
        elif self.controller.direction_status == "rl":
            image = self.history[0][:, :self.sec_height]
            for i in range(1, self.controller.num_sections):
                image = cv2.hconcat([image, self.history[-i][:, self.sec_height*i:self.sec_height*(i+1)]])
        return image


    def show(self):
        """Shows current image.
        """
        cv2.namedWindow(self.windowname, cv2.WINDOW_FREERATIO)
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

        self.get_sec_height(frame)
        print(frame.shape)


        while rval:
            time.sleep(.1)
            if self.controller.edit_mode == "direction_set":
                self.get_sec_height(frame)
                self.controller.edit_mode = None

            elif self.controller.edit_mode == "num_sections_set":
                self.get_sec_height(frame)

            rval, frame = self.vc.read()
            self.history.append(frame)

            if len(self.history) > self.controller.num_sections:
                self.history.pop(0)
                img = self.replace_sections_iterative()
                if self.controller.show_text_status:
                    self.add_text(img)


                cv2.imshow(self.windowname, img)

            key = cv2.waitKey(1)
            if key == 27: # exit on ESC
                break
        cv2.destroyWindow(self.windowname)

    def get_sec_height(self, frame):
        if self.controller.direction_status in ("tb", "bt"):
            self.sec_height = frame.shape[0] // self.controller.num_sections
        elif self.controller.direction_status in ("lr", "rl"):
            self.sec_height = frame.shape[1] // self.controller.num_sections


    def add_text(self, image):
        font_scale = .5
        color = (255, 0, 0)
        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness=1
        line_type=cv2.LINE_AA
        cv2.putText(image, "Direction: {}".format(self.controller.textdirection), (50, 50), font, fontScale=font_scale, color=color, thickness=thickness, lineType=line_type)
        cv2.putText(image, "Number of Slices: {}".format(self.controller.num_sections), (50, 75), font, fontScale=font_scale, color=color, thickness=thickness, lineType=line_type)
        return image

class Controller(Thread):
    def __init__(self, direction, section_num):

        super().__init__(name="controller", target=self.detect_event)
        self.show_text_status = False
        self.direction_status = direction
        self.textdirection = None
        self.set_direction(direction)

        self.num_sections = section_num
        self.edit_mode = None

    def detect_event(self):
        raise NotImplementedError()

    def show_text(self):
        self.show_text_status = not(self.show_text_status)


    def set_direction(self, d):
        """Sets new direction.
        @param d: new direction"""
        self.direction_status = d
        if d == "lr":
            self.textdirection = "left to right"
        elif d == "rl":
            self.textdirection = "right to left"
        elif d == "tb":
            self.textdirection = "top to bottom"
        elif d == "bt":
            self.textdirection = "bottom to top"
        self.edit_mode = "direction_set"

    def set_num_sections(self, ns):
        """Sets new number of sections.
        @param ns: new number of sections"""
        self.num_sections = ns
        self.edit_mode = "num_sections_set"



class DesktopController(Controller):
    def __init__(self, direction, num_sec):
        super().__init__(direction, num_sec)

    def detect_event(self):
        keypressed = cv2.waitKey(33)
        if keypressed == ord('t'):
            self.show_text()

        if keypressed == ord('u'):
            self.set_direction("bt")
        if keypressed == ord('d'):
            self.set_direction("tb")
        if keypressed == ord('l'):
            self.set_direction("rl")
        if keypressed == ord('r'):
            self.set_direction("lr")


class ControllerController(Controller):
    def __init__(self, direction, num_sec):
        super().__init__(direction, num_sec)

        self.controller = InputDevice('/dev/input/event3')

        # Mapping of controller buttons
        self.a_butt = 304
        self.b_butt = 305
        self.x_butt = 307
        self.y_butt = 308

        self.up = 17
        self.down = 17

        self.left = 16
        self.right = 16

        self.start_butt = 315
        self.select_butt = 314

        self.l_trig = 310
        self.r_trig = 311

    def detect_event(self):

        for event in self.controller.read_loop():
            if event.type == ecodes.EV_KEY:
                if event.value == 1:
                    if event.code == self.y_butt:
                        print("Y")
                    elif event.code == self.b_butt:
                        if self.edit_mode == "num_sections":
                            self.edit_mode = None
                        else:
                            self.edit_mode = "num_sections"


                    elif event.code == self.a_butt:
                        self.edit_mode = "direction"

                    elif event.code == self.x_butt:
                        print("X")

                    elif event.code == self.start_butt:
                        print("start")
                    elif event.code == self.select_butt:
                        self.show_text()

                    elif event.code == self.l_trig:
                        print("left bumper")
                    elif event.code == self.r_trig:
                        print("right bumper")

            elif event.type == ecodes.EV_ABS:
                if event.value == -1:
                    if event.code == self.up:
                        if self.edit_mode == "direction":
                            self.set_direction("bt")
                        elif self.edit_mode == "num_sections":
                            self.set_num_sections(self.num_sections + 1)

                    elif event.code == self.left:
                        if self.edit_mode == "direction":
                            self.set_direction("rl")
                        elif self.edit_mode == "num_sections":
                            self.set_num_sections(self.num_sections - 1)
                elif event.value == 1:
                    # elif event.code == self.up:
                    #     print("up")
                    if event.code == self.down:
                        if self.edit_mode == "direction":
                            self.set_direction("tb")
                        elif self.edit_mode == "num_sections":
                            self.set_num_sections(self.num_sections - 1)
                    # elif event.code == self.left:
                    #     print("left")
                    elif event.code == self.right:
                        if self.edit_mode == "direction":
                            self.set_direction("lr")
                        elif self.edit_mode == "num_sections":
                            self.set_num_sections(self.num_sections + 1)




    #
    # def test_controller(self):
    #     #prints out device info at start
    #     print(self.controller)
    #     time.sleep(1)
    #     #loop and filter by event code and print the mapped label
    #     for event in self.controller.read_loop():
    #         if event.type == ecodes.EV_KEY:
    #             if event.value == 1:
    #                 if event.code == self.y_butt:
    #                     print("Y")
    #                 elif event.code == self.b_butt:
    #                     print("B")
    #                 elif event.code == self.a_butt:
    #                     print("A")
    #                 elif event.code == self.x_butt:
    #                     print("X")
    #
    #                 elif event.code == self.up:
    #                     print("up")
    #                 elif event.code == self.down:
    #                     print("down")
    #                 elif event.code == self.left:
    #                     print("left")
    #                 elif event.code == self.right:
    #                     print("right")
    #
    #                 elif event.code == self.start:
    #                     print("start")
    #                 elif event.code == self.select:
    #                     print("select")
    #
    #                 elif event.code == self.l_trig:
    #                     print("left bumper")
    #                 elif event.code == self.r_trig:
    #                     print("right bumper")


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

    if MODE == "desktop":
        Ctrl = DesktopController(direction, 40)
    elif MODE == "controller":
        Ctrl = ControllerController(direction, 40)
    Ctrl.start()

    RS = RollingShutter(Ctrl)
    RS.start()
