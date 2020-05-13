import cv2
from flask import Flask, jsonify
import threading


def empty(arg):
    pass


#############################################################
BLUE, GREEN, RED = (255, 0, 0), (0, 255, 0), (0, 0, 255)
CYAN, YELLOW = (255, 255, 0), (0, 255, 255)
pos_line, offset = 150, 30
xy1, xy2 = (20, pos_line), (300, pos_line)
area_ret_min = 3000
side_ret_max = 200
jump_on_x_value = 50
cache_detects = []
total = ppl_out = ppl_in = 0
cap = cv2.VideoCapture('../media/pedestres.mp4')  # 0 to webcam
fgbg = cv2.createBackgroundSubtractorMOG2()
#############################################################


def set_controls():
    cv2.namedWindow('Controls')
    cv2.resizeWindow('Controls', 640, 320)
    cv2.createTrackbar('area ret min', 'Controls', 3000, 10000, empty)
    cv2.createTrackbar('side ret max', 'Controls', 200, 1000, empty)
    cv2.createTrackbar('jump X value', 'Controls', 300, 1000, empty)
    cv2.createTrackbar('line position', 'Controls', 150, 1000, empty)
    cv2.createTrackbar('line offset', 'Controls', 30, 100, empty)


def update_controls_values():
    global area_ret_min, side_ret_max, jump_on_x_value, pos_line, offset
    area_ret_min = cv2.getTrackbarPos('area ret min', 'Controls')
    side_ret_max = cv2.getTrackbarPos('side ret max', 'Controls')
    jump_on_x_value = cv2.getTrackbarPos('jump X value', 'Controls')
    pos_line = cv2.getTrackbarPos('line position', 'Controls')
    offset = cv2.getTrackbarPos('line offset', 'Controls')
#############################################################
