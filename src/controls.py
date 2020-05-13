import cv2
from src import consts


def set_controls():
    cv2.namedWindow('Controls')
    cv2.resizeWindow('Controls', 640, 320)
    cv2.createTrackbar('area ret min', 'Controls', 3000, 10000, lambda empty: None)
    cv2.createTrackbar('side ret max', 'Controls', 200, 1000, lambda empty: None)
    cv2.createTrackbar('jump X value', 'Controls', 300, 1000, lambda empty: None)
    cv2.createTrackbar('line position', 'Controls', 150, 1000, lambda empty: None)
    cv2.createTrackbar('line offset', 'Controls', 30, 100, lambda empty: None)


def update_controls_values():
    consts.area_ret_min = cv2.getTrackbarPos('area ret min', 'Controls')
    consts.side_ret_max = cv2.getTrackbarPos('side ret max', 'Controls')
    consts.jump_on_x_value = cv2.getTrackbarPos('jump X value', 'Controls')
    consts.pos_line = cv2.getTrackbarPos('line position', 'Controls')
    consts.offset = cv2.getTrackbarPos('line offset', 'Controls')
