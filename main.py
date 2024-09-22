from time import time
import cv2 as cv
import pyautogui
from pynput import keyboard
from screen_cap import WindowCapture

# TODO make opencv part run on GPU
class TerrariaCV:

    def __init__(self):
        self.auto_mouse_follow = False
        self.threshold = 0.85
        self.found = False

        self.matching_attempts = 0
        self.matches_found = 0

        self.create_keyboard_listener()
        self.begin()

    def begin(self):

        needle_img = cv.imread('torch.png', cv.IMREAD_UNCHANGED)
        window_cap = WindowCapture()

        # record curr time for benchmarking purposes
        loop_time = time()

        # execute the video recorder until the user presses 'q'
        while True:

            # take a screenshot of user's screen, and convert to a cv-readable format
            screen_cap = window_cap.capture_window()
            print(screen_cap.shape)

            # find the needle image in the haystack image by trying multiple different sizes
            scale = 0.5
            while scale <= 1.0:
                if self.find_image(needle_img, screen_cap, scale):
                    self.matches_found += 1
                    break
                scale += 0.1
            self.matching_attempts += 1

            # display time for benchmarking
            print(f'FPS: {1 / ((time() - loop_time))}')
            loop_time = time()

            # exit the program if user presses 'q'
            if cv.waitKey(1) == ord('q'):
                cv.destroyAllWindows()
                break
            cv.waitKey(1)

        print("finsihed!")

    def toggle_auto_mouse_follow(self):
        if self.auto_mouse_follow:
            self.auto_mouse_follow = False
        else:
            self.auto_mouse_follow = True

    def on_press(self, key):
        try:
            print('alphanumeric key {0} pressed'.format(
                key.char))
            if key.char == 'f':
                self.toggle_auto_mouse_follow()
                print("auto mouse follow is " + str(self.auto_mouse_follow))
        except AttributeError:
            print('special key {0} pressed'.format(
                key))

    def on_release(self, key):
        print('{0} released'.format(
            key))
        if key == keyboard.Key.esc:
            # Stop listener
            return False

    def create_keyboard_listener(self):
        # collect use input in non-blocking way
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        listener.start()

    def find_image(self, needle_img, haystack_img, scale=1.0):

        new_height = (int)(needle_img.shape[0] * scale)
        new_width = (int)(needle_img.shape[1] * scale)
        #print("Haystack img shape: " + str(haystack_img.shape[0]) + ", " + str(haystack_img.shape[1]))
        #print("Needle img shape: " + str(needle_img.shape[0]) + ", " + str(needle_img.shape[0]))
        resized_needle_img = cv.resize(needle_img, dsize=(new_width, new_height), interpolation=cv.INTER_CUBIC)
        result = cv.matchTemplate(haystack_img, resized_needle_img, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

        print('match confidence: %s' % max_val)
        print('total matching attempts: ' + str(self.matching_attempts))
        print('successful matches: ' + str(self.matches_found))
        if max_val >= self.threshold:

            # calc boundaries to draw rect
            resized_needle_w = resized_needle_img.shape[1]
            resized_needle_h = resized_needle_img.shape[0]
            top_left = max_loc
            bottom_right = (top_left[0] + resized_needle_w, top_left[1] + resized_needle_h)

            # draw rect around found match
            cv.rectangle(haystack_img, top_left, bottom_right,
                         color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)

            # print the position of the rectangle
            print('found!')

            # print coordinates of the top left of the CV rectangle ( (0,0) is top left of Terraria window)
            print('match top left pos: %s' % str(max_loc))

            # move mouse to top left coordinate of CV box: https://www.geeksforgeeks.org/mouse-keyboard-automation-using-python/
            if self.auto_mouse_follow:
                pyautogui.moveTo(top_left[0], top_left[1], duration=0)

            cv.namedWindow('Result', cv.WINDOW_NORMAL)
            cv.imshow('Result', haystack_img)
            cv.resizeWindow('Result', 540, 360)
            return True
        else:
            print('not found')
            return False

if __name__ == '__main__':
    program = TerrariaCV()