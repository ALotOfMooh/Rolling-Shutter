# https://core-electronics.com.au/tutorials/using-usb-and-bluetooth-controllers-with-python.html
# https://python-evdev.readthedocs.io/en/latest/tutorial.html
"""Implementation of Rolling Shutter Effect. For now it works on a desktop PC with attatched camera.
    """
import time
import sys
import cv2
# import numpy as np

from threading import Thread

import autoplay



#MODE = "desktop"
MODE = "controller"
direction = "tb"
device = '/dev/input/' + autoplay.camera_dev

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


        # width = self.vc.get(cv2.CAP_PROP_FRAME_WIDTH)
        # height = self.vc.get(cv2.CAP_PROP_FRAME_HEIGHT)
        # print(width, height)
        cv2.namedWindow(self.windowname,cv2.WINDOW_FREERATIO)

    #    cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
        cv2.setWindowProperty(self.windowname, cv2.WND_PROP_FULLSCREEN,
                             cv2.WINDOW_FULLSCREEN)


    def replace_sections_iterative(self):
        """Iterative (slow) algorithm that fills the resulting image from history.
        """
        if self.controller.direction_status == "bt":
            image = self.history[0][:self.sec_height]
            for i in range(1, self.controller.num_sections):
                image = cv2.vconcat([image, self.history[i][self.sec_height*i:self.sec_height*(i+1)]])
        elif self.controller.direction_status == "tb":
            image = self.history[-1][:self.sec_height]
            for i in range(1, self.controller.num_sections):
                image = cv2.vconcat([image, self.history[-i][self.sec_height*i:self.sec_height*(i+1)]])
        elif self.controller.direction_status == "lr":
            image = self.history[0][:, :self.sec_height]
            for i in range(1, self.controller.num_sections):
                image = cv2.hconcat([image, self.history[i][:, self.sec_height*i:self.sec_height*(i+1)]])
        elif self.controller.direction_status == "rl":
            image = self.history[-1][:, :self.sec_height]
            for i in range(1, self.controller.num_sections):
                image = cv2.hconcat([image, self.history[-i][:, self.sec_height*i:self.sec_height*(i+1)]])
        return image


    def show(self):
        """Shows current image.
        """
        if self.vc.isOpened(): # try to get the first frame
            rval, frame = self.vc.read()
            self.history.append(frame)
        else:
            rval = False

        self.get_sec_height(frame)
    #    print(frame.shape)

        while rval:
            s = time.time()
        #    time.sleep(.1)
            if self.controller.edit_mode == "direction_set":
                self.get_sec_height(frame)
                self.controller.edit_mode = None

            elif self.controller.edit_mode == "num_sections_set":
                while len(self.history) > self.controller.num_sections:
                    self.history.pop()
                self.get_sec_height(frame)

            rval, frame = self.vc.read()
            self.history.append(frame)

            if len(self.history) > self.controller.num_sections:
                self.history.pop(0)
                img = self.replace_sections_iterative()
                if self.controller.show_text_status:
                    self.add_text(img)
          #    flipHorizontal = cv2.flip(originalImage, 1)
                cv2.imshow(self.windowname, img) #, cv2.flip(img, 1))

            key = cv2.waitKey(1)
            if key == 27: # exit on ESC
                break
            # print(time.time() - s)
        cv2.destroyWindow(self.windowname)

    def get_sec_height(self, frame):
        """Calculates section height (pixel rows/columns per secion)
        @param frame: current frame (numpy arrays)"""
        if self.controller.direction_status in ("tb", "bt"):
            self.sec_height = frame.shape[0] // self.controller.num_sections
        elif self.controller.direction_status in ("lr", "rl"):
            self.sec_height = frame.shape[1] // self.controller.num_sections


    def add_text(self, image):
        """Add Text with credentials to current image.
        @param image: current image (numpy array)
        """
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
        self.show_text_status = True
        self.direction_status = direction
        self.textdirection = None
        self.set_direction(direction)
        self.num_sections = section_num

        self.edit_mode = None

    def detect_event(self):
        raise NotImplementedError()

    def show_text(self):
        """Changes show text status.
        """
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
        """Detects Key events."""
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

        self.controller = InputDevice(device)
    #    print(self.controller)

        # Mapping of controller buttons
        self.a_butt = 288 #304
        self.b_butt = 289#305
        self.x_butt = 290#307
        self.y_butt = 291#308

        self.up = 1#17
        self.down = 1#17

        self.left = 0#16
        self.right = 0#16

        self.start_butt = 297#315
        self.select_butt = 296#314

        self.l_trig = 292#310
        self.r_trig = 293#311

        self.stop_code = [self.start_butt for i in range(5)]
        self.current_stop_event = 0
        self.stop_event_detect = []
        

    def detect_event(self):
        """Detects key events from controller.
        """
        for event in self.controller.read_loop():
            if event.type == ecodes.EV_KEY:
                if event.value == 1:
                    if event.code == self.stop_code[self.current_stop_event]:
                        self.current_stop_event += 1
                        self.stop_event_detect.append(True)
                        if len(self.stop_event_detect) == len(self.stop_code):
                            sys.exit()
                    else:
                        self.current_stop_event = 0
                        self.stop_event_detect = []
                    if event.code == self.y_butt:
                        # print("Y")
                        pass
                    elif event.code == self.b_butt:
                        self.set_num_sections(self.num_sections - 1)

                    elif event.code == self.a_butt:
                        self.set_num_sections(self.num_sections + 1)

                    elif event.code == self.x_butt:
                        # print("X")
                        pass

                    elif event.code == self.start_butt:
                        pass
                        # print("start")
                    elif event.code == self.select_butt:
                        self.show_text()

                    elif event.code == self.l_trig:
                        pass
                        # print("left bumper")
                    elif event.code == self.r_trig:
                        pass
                        # print("right bumper")

                # elif event.value == -1:
                #     if event.code == self.b_butt:
                #         self.edit_mode = None
            elif event.type == ecodes.EV_ABS:
                if event.value == 0 and event.type == 3:
                #    print("jup")
                    if event.code == self.up:
                #        print("jup2")
                        self.set_direction("bt")


                    elif event.code == self.left:
                        self.set_direction("rl")
                elif event.value == 255:
                    if event.code == self.down:
                        self.set_direction("tb")
                    elif event.code == self.right:
                        self.set_direction("lr")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if 'event' in sys.argv[1]:
            device = '/dev/input/' + sys.argv[1]
    else:
        device = autoplay.gamepad_dev
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
