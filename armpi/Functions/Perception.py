#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
import rospy
import math
import numpy as np
from CameraCalibration.CalibrationConfig import *
from ArmIK.Transform import *

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

global __isRunning
global __target_color
global count
global track
global get_roi
global rect
global center_list
global detect_color
global action_finish
global start_count_t1
global start_pick_up, first_move

t1 = 0
roi = ()
last_x, last_y = 0, 0
rect = None
range_rgb = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

class Perception(object):
    def __init__(self, func='color_track', target_c=('blue', ) ):
        print("Perception Init")
        self.func = func
        self.size = (640, 480)
        self.start()
        self.setTargetColor(target_c)
        self.color_range = rospy.get_param('/lab_config_manager/color_range_list', {})  # get lab range from ros param server


    # begin start running
    def start(self):
        global __isRunning
        self.reset()
        __isRunning = True
        print("ColorTracking Start")

    # reset variables
    def reset(self):
        global count
        global track
        global _stop
        global get_roi
        global first_move
        global center_list
        global __isRunning
        global detect_color
        global action_finish
        global start_pick_up
        global __target_color
        global start_count_t1
        
        count = 0
        _stop = False
        track = False
        get_roi = False
        center_list = []
        first_move = True
        __target_color = ()
        detect_color = 'None'
        action_finish = True
        start_pick_up = False
        start_count_t1 = True
    
    # app stop games 
    def stop():
        global __isRunning
        __isRunning = False
        print("Stop")

    # app exit to games
    def exit():
        global __isRunning
        __isRunning = False
        print("Exit")

    # set be detected color
    def setTargetColor(self, target_color):
        global __target_color

        #print("COLOR", target_color)
        __target_color = target_color
        return (True, ())
   
    # find the maximum area contour
    # the parameter is a list of contours to be compared
    def getAreaMaxContour(self, contours):
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:  # traversal all the contours 
            contour_area_temp = math.fabs(cv2.contourArea(c))  # calculate the countour area
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:  # only when the area is greater than 300, the contour of the maximum area is effective to filter interference
                    area_max_contour = c

        return area_max_contour, contour_area_max  # return the maximum area countour

    # begin image provessing
    def run(self, img):
        self.size = (640, 480)
        self.img_copy = img.copy()

        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

        # check if camera is running
        if not __isRunning:
            return img
        else:
            self.noise_filtering(img.copy())
    
    # initial noise filtering
    def noise_filtering(self, img_org):
        # resize the image 
        frame_resize = cv2.resize(self.img_copy, self.size, interpolation=cv2.INTER_NEAREST)

        # smoothen the image using gaussian blur
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)

        # If it is detected with a aera recognized object, the area will be detected ubtil there is no object
        # all become black except for the roi area
        if get_roi and start_pick_up:
            get_roi = False
            # frame_gb = getMaskROI(frame_gb, roi, self.size)

        # convert the image to LAB space
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB) 
        if self.func == 'color_track':
            self.color_track(frame_lab.copy(), img_org) 
        elif self.func == 'color_sort':
            self.color_sort(frame_lab.copy(), img_org)
    
    # track a single color
    def color_track(self, img_trans, img_org):
        global rect
        global get_roi
        area_max = 0
        areaMaxContour = 0
        # while the object is being detected
        if not start_pick_up:
            for i in self.color_range:
                if i in __target_color:
                    detect_color = i
                    # identigy if the color lies in the color range
                    frame_mask = cv2.inRange(img_trans, self.color_range[detect_color][0], self.color_range[detect_color][1])  # mathematical operation on the original image and mask

                    # removing noise
                    opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # Opening (morphology)
                    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # Closing (morphology)

                    # finding boundary of the object from black background
                    contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # find countour

                    # find the maximum area contour
                    areaMaxContour, area_max = self.getAreaMaxContour(contours)  # find the maximum countour

                # if area max obtained lesser than a limit
                if area_max > 2500:  # find the maximum area
                    # Finds a rotated rectangle of the minimum area enclosing the input 2D point set.
                    rect = cv2.minAreaRect(areaMaxContour)
                    box = np.int0(cv2.boxPoints(rect))

                    # get max min co-ordinates for roi
                    roi = getROI(box) # get roi zone
                    get_roi = True

                    img_centerx, img_centery = getCenter(rect, roi, self.size, square_length)  # get the center coordinates of block
                    world_x, world_y = convertCoordinate(img_centerx, img_centery, self.size) # convert to world coordinates
                    
                    
                    cv2.drawContours(img_org, [box], -1, range_rgb[detect_color], 2)
                    cv2.putText(img_org, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, range_rgb[detect_color], 1) # draw center position
                    distance = math.sqrt(pow(world_x - last_x, 2) + pow(world_y - last_y, 2)) # compare the last coordinate to determine whether to move
                    last_x, last_y = world_x, world_y
                    track = True
                    # print(count,distance)
                    # cumulative judgment
                    if action_finish:
                        if distance < 0.3:
                            center_list.extend((world_x, world_y))
                            count += 1
                            if start_count_t1:
                                start_count_t1 = False
                                t1 = time.time()
                            if time.time() - t1 > 1.5:
                                rotation_angle = rect[2]
                                start_count_t1 = True
                                world_X, world_Y = np.mean(np.array(center_list).reshape(count, 2), axis=0)
                                count = 0
                                center_list = []
                                start_pick_up = True
                        else:
                            t1 = time.time()
                            start_count_t1 = True
                            count = 0
                            center_list = []
        return img_org

    # track multiple color boxes to place them in respective bins
    def color_sort(self, img_trans, img_org):
        if not start_pick_up:
            for i in self.color_range:
                if i in __target_color:
                    frame_mask = cv2.inRange(img_trans, self.color_range[i][0], self.color_range[i][1])  # mathematical operation on the original image and mask
                    opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6,6),np.uint8))  # Opening (morphology)
                    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6,6),np.uint8)) # Closing (morphology)
                    contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # find countour
                    areaMaxContour, area_max = self.getAreaMaxContour(contours)  # find the maximum countour
                    if areaMaxContour is not None:
                        if area_max > max_area:# find the maximum area
                            max_area = area_max
                            color_area_max = i
                            areaMaxContour_max = areaMaxContour
        if max_area > 2500:  # have found the maximum area
            rect = cv2.minAreaRect(areaMaxContour_max)
            box = np.int0(cv2.boxPoints(rect))
            
            roi = getROI(box) # get roi zone
            get_roi = True
            img_centerx, img_centery = getCenter(rect, roi, self.size, square_length)  # get the center coordinates of block
             
            world_x, world_y = convertCoordinate(img_centerx, img_centery, self.size) # convert to world coordinates
            
            cv2.drawContours(img_org, [box], -1, range_rgb[color_area_max], 2)
            cv2.putText(img_org, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, range_rgb[color_area_max], 1) # draw center position
            
            distance = math.sqrt(pow(world_x - last_x, 2) + pow(world_y - last_y, 2)) # compare the last coordinate to determine whether to move
            last_x, last_y = world_x, world_y
            if not start_pick_up:
                if color_area_max == 'red':  # red area is the maximum
                    color = 1
                elif color_area_max == 'green':  # green area is the maximum
                    color = 2
                elif color_area_max == 'blue':  # blue area is the maximum
                    color = 3
                else:
                    color = 0
                color_list.append(color)
                # cumulative judgment
                if distance < 0.5:
                    count += 1
                    center_list.extend((world_x, world_y))
                    if start_count_t1:
                        start_count_t1 = False
                        t1 = time.time()
                    if time.time() - t1 > 1:
                        rotation_angle = rect[2] 
                        start_count_t1 = True
                        world_X, world_Y = np.mean(np.array(center_list).reshape(count, 2), axis=0)
                        center_list = []
                        count = 0
                        start_pick_up = True
                else:
                    t1 = time.time()
                    start_count_t1 = True
                    center_list = []
                    count = 0

                if len(color_list) == 3:  # multipe judgments
                    # take evaluation value
                    color = int(round(np.mean(np.array(color_list))))
                    color_list = []
                    if color == 1:
                        detect_color = 'red'
                        draw_color = range_rgb["red"]
                    elif color == 2:
                        detect_color = 'green'
                        draw_color = range_rgb["green"]
                    elif color == 3:
                        detect_color = 'blue'
                        draw_color = range_rgb["blue"]
                    else:
                        detect_color = 'None'
                        draw_color = range_rgb["black"]
        else:
            if not start_pick_up:
                draw_color = (0, 0, 0)
                detect_color = "None"

        cv2.putText(img_org, "Color: " + detect_color, (10, img_org.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, draw_color, 2)
        return img_org

if __name__ == '__main__':

    # define a color to track
    __target_color = ('red', )

    # define an camera object
    my_camera = Camera.Camera()

    # define a video capture object and its parameters
    my_camera.camera_open()

    # define a perception object
    perception_obj = Perception('color_sort', __target_color)

    # until keyboard interrupted
    while True:
        # extracting frames from the video captured
        img = my_camera.frame

        # if frame was found
        if img is not None:
            # create a copy of the image for processing
            frame = img.copy()

            # detect an object
            Frame = perception_obj.run(frame)   

            # show the manipulated image        
            cv2.imshow('Frame', Frame)

            # sleep for 27ms second
            key = cv2.waitKey(1)
            if key == 27:
                break
    # exit statement
    perception_obj.stop()
    perception_obj.exit()
    my_camera.camera_close()
    cv2.destroyAllWindows()