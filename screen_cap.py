# This code is adapted from:
# "OpenCV in Python Tutorial : Fast Window Capture - OpenCV Object Detection in Games #4"
# https://www.youtube.com/watch?v=WymCpVUPWQ4

import numpy as np
import win32gui, win32ui, win32con

class WindowCapture:

    def __init__(self):
        self.w = 1920  # depends on monitor
        self.h = 1080  # depends on monitor

        # change this depending on whatever the splash text is on Terraria
        self.window_name = "Terraria: Digger T' Blocks"

    # handy function to list the true names of active windows
    def list_window_names(self):
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    # capture the user's entire screen and return it as an array.
    # code adapted from https://stackoverflow.com/questions/3586046/fastest-way-to-take-a-screenshot-with-python-on-windows

    def capture_window(self):
        hwnd = win32gui.FindWindow(None, self.window_name)
        if not hwnd:
            raise Exception(f'Window named "{self.window_name}" not found')

        # get window size
        window_rect = win32gui.GetWindowRect(hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        # get dimensions of excess portion to cut it out
        border_px = 8
        top_border_px = 30
        self.w -= (border_px * 2)
        self.h -= top_border_px - border_px

        # retrieve the device context from the game window
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)

        # create a new device context compatible with this device
        cDC = dcObj.CreateCompatibleDC()

        # create a new bitmap containing information about the game window
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)

        # transfer colour data to the target device context dcObj
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (border_px, top_border_px), win32con.SRCCOPY)

        # save screenshot using an opencv-readable format
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # delete used resources; saves space
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # avoid error by dropping the alpha channel
        img = img[...,:3]

        # return the image as a contiguous array
        img = np.ascontiguousarray(img)
        return img



