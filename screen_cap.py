# This code is not my own, here is the source:
# OpenCV in Python Tutorial : Fast Window Capture - OpenCV Object Detection in Games #4
# https://www.youtube.com/watch?v=WymCpVUPWQ4

import os
from time import time
import cv2 as cv
import numpy as np
import pyautogui
from PIL import ImageGrab
import win32gui, win32ui, win32con

class WindowCapture:

    def __init__(self):
        self.w = 1920  # change depending on your monitor
        self.h = 1080  # change depending on your monitor

        # TODO furnish these
        self.offset_x = None
        self.offset_y = None

        # change this depending on whatever the splash text is on Terraria
        self.window_name = "Terraria: Legend of Maxx"


    def list_window_names(self):
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    def capture_window(self):
        # code adapted from https://stackoverflow.com/questions/3586046/fastest-way-to-take-a-screenshot-with-python-on-windows
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

        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (border_px, top_border_px), win32con.SRCCOPY)

        # save screenshot as an opencv-compatable format
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # Delete Open Resources to save space
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # drop alpha channel to avoid error
        img = img[...,:3]

        img = np.ascontiguousarray(img)

        return img

    # TODO: make this function functional
    def get_screen_pos(self, window_pos: tuple[int, int], offset_x: int, offset_y: int) -> tuple[int, int]:
        """
        Return the position of this window coordinate as a position on the entire screen.
        """
        return (window_pos[0] + offset_x, window_pos[1] + offset_y)


