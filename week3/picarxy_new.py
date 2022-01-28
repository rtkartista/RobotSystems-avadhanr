#from ezblock import Servo,PWM,fileDB,Pin,ADC
import logging
import logdecorator
import atexit
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
try :
    from ezblock import *
    from ezblock import __reset_mcu__
    __reset_mcu__ ()
    time.sleep (0.01)
except ImportError :
    print (" This computer does not appear to be a PiCar - X system ( ezblock is not present ) . Shadowing hardware calls with substitute functions ")
    from sim_ezblock import *

from concurrency import Concurrency
logging_format = "%(asctime) s:%(message) s "
logging.basicConfig( format = logging_format , level = logging.INFO ,datefmt ="%H:%M:%S")

logging.getLogger().setLevel( logging.DEBUG )

class Picarx(object):
    PERIOD = 4095
    PRESCALER = 10
    TIMEOUT = 0.02
    def __init__(self):
        self.dir_servo_pin = Servo(PWM('P2'))
        self.config_flie = fileDB('/home/pi/.config')
        self.dir_cal_value = int(self.config_flie.get("picarx_dir_servo", default_value=0))
        self.dir_servo_pin.angle(self.dir_cal_value)
        
        self.left_rear_pwm_pin = PWM("P13")
        self.right_rear_pwm_pin = PWM("P12")
        self.left_rear_dir_pin = Pin("D4")
        self.right_rear_dir_pin = Pin("D5")

        self.motor_direction_pins = [self.left_rear_dir_pin, self.right_rear_dir_pin]
        self.motor_speed_pins = [self.left_rear_pwm_pin, self.right_rear_pwm_pin]
        self.cali_dir_value = self.config_flie.get("picarx_dir_motor", default_value="[1,1]")
        self.cali_dir_value = [int(i.strip()) for i in self.cali_dir_value.strip("[]").split(",")]
        self.cali_speed_value = [0, 0]
        self.dir_current_angle = 0
        self.cali_angle = 0
        # shows a command saying KeyboardInterrupt, and calls the func stop
        for pin in self.motor_speed_pins:
            pin.period(self.PERIOD)
            pin.prescaler(self.PRESCALER)
        
        atexit.register(self.cleanup)

    def set_motor_speed(self,motor,speed):
        # global cali_speed_value,cali_dir_value
        motor -= 1
        if speed >= 0:
            direction = 1 * self.cali_dir_value[motor]
        elif speed < 0:
            direction = -1 * self.cali_dir_value[motor]
        speed = abs(speed)
        #if speed != 0:
        #    speed = int(speed /2 ) + 50
        speed = speed - self.cali_speed_value[motor]
        if direction < 0:
            self.motor_direction_pins[motor].high()
            self.motor_speed_pins[motor].pulse_width_percent(speed)
        else:
            self.motor_direction_pins[motor].low()
            self.motor_speed_pins[motor].pulse_width_percent(speed)

    def motor_speed_calibration(self,value):
        # global cali_speed_value,cali_dir_value
        self.cali_speed_value = value
        if value < 0:
            self.cali_speed_value[0] = 0
            self.cali_speed_value[1] = abs(self.cali_speed_value)
        else:
            self.cali_speed_value[0] = abs(self.cali_speed_value)
            self.cali_speed_value[1] = 0

    def motor_direction_calibration(self,motor, value):
        # 0: positive direction
        # 1:negative direction
        # global cali_dir_value
        motor -= 1
        if value == 1:
            self.cali_dir_value[motor] = -1 * self.cali_dir_value[motor]
        self.config_flie.set("picarx_dir_motor", self.cali_dir_value)

    def dir_servo_angle_calibration(self,value):
        # global dir_cal_value
        self.dir_cal_value = value
        print("calibrationdir_cal_value:",self.dir_cal_value)
        self.config_flie.set("picarx_dir_servo", "%s"%value)
        self.dir_servo_pin.angle(value)

    def set_dir_servo_angle(self,value):
        # global dir_cal_value
        angle_value  = value + self.cali_angle
        # 50 = 40 + 10
        # -30 = -40 + 10
        if angle_value >= 0 and angle_value > 40 + self.cali_angle:
            self.dir_current_angle = 40 + self.cali_angle
        elif angle_value < 0 and angle_value < -40 + self.cali_angle:
            self.dir_current_angle = -40 + self.cali_angle
        else:
            self.dir_current_angle = angle_value
        #print("servo angle after calibration:",self.dir_current_angle)
        # print("set_dir_servo_angle_1:",angle_value)
        # print("set_dir_servo_angle_2:",dir_cal_value)
        self.dir_servo_pin.angle(angle_value)

    def backward(self,speed):
        current_angle = self.dir_current_angle
        if current_angle != 0:
            abs_current_angle = abs(current_angle)
            # if abs_current_angle >= 0:
            if abs_current_angle > 40:
                abs_current_angle = 40
            power_scale = (100 - abs_current_angle) / 100.0 
            print("power_scale:",power_scale)
            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, -1*speed)
                self.set_motor_speed(2, speed * power_scale)
            else:
                self.set_motor_speed(1, -1*speed * power_scale)
                self.set_motor_speed(2, speed )
        else:
            self.set_motor_speed(1, -1*speed)
            self.set_motor_speed(2, speed)  
        return 1
    
    @logdecorator.log_on_start( logging.DEBUG," the car begin to move forward with speed: {speed!s}") # :s for strings
    @logdecorator.log_on_end( logging.DEBUG," the car successfully moved forward")
    def forward(self,speed):
        current_angle = self.dir_current_angle
        if current_angle != 0:
            abs_current_angle = abs(current_angle)
            # if abs_current_angle >= 0:
            if abs_current_angle > 40:
                abs_current_angle = 40
            power_scale = (100 - abs_current_angle) / 100.0 
            print("power_scale:",power_scale)
            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, speed)
                self.set_motor_speed(2, -1*speed * power_scale)
            else:
                self.set_motor_speed(1, speed * power_scale)
                self.set_motor_speed(2, -1*speed )
        else:
            self.set_motor_speed(1, speed)
            self.set_motor_speed(2, -1*speed)                  

    def stop(self):
        self.set_motor_speed(1, 0)
        self.set_motor_speed(2, 0)

    def cleanup(self):
        self.stop()

    @logdecorator.log_on_end( logging.DEBUG," the car successfully calibrated its steering")
    def calibrate_steering(self):
        calibration_angle_error = -5
        self.set_dir_servo_angle(calibration_angle_error)
        time.sleep(1)
        #picar.forward(30)
        #time.sleep(5)

        self.cali_angle = calibration_angle_error
        
    def forward_improved(self, speed):
        # assuming car base = .6m
        # constant angular velocity
        # left wheel velocity
        # right wheel velocity
        turn_radius = .15
        base_radius = .06
        car_w = speed/((base_radius/2) + turn_radius)
        current_angle = self.dir_current_angle

        if current_angle != self.cali_angle:
            # move left/right
            abs_current_angle = abs(current_angle)
            if (current_angle / abs_current_angle) < 0:
                speed_left = car_w * turn_radius
                speed_right = car_w * (turn_radius + base_radius)
                #print(str(speed_right)+ " "+str(speed_left))
                self.set_motor_speed(1, speed_left)
                self.set_motor_speed(2, -speed_right)
            elif (current_angle / abs_current_angle) > 0:
                speed_right = car_w * turn_radius
                speed_left = car_w * (turn_radius + base_radius)
                #print(str(speed_right)+ " "+str(speed_left))
                self.set_motor_speed(1, speed_left)
                self.set_motor_speed(2, -speed_right)
        else:
            # go straight
            self.set_motor_speed(1, speed)
            self.set_motor_speed(2, -speed)                  

class Sensors(object):
    def __init__(self):
        self.camera_servo_pin1 = Servo(PWM('P0'))
        self.camera_servo_pin2 = Servo(PWM('P1'))
        self.config_flie = fileDB('/home/pi/.config')
        self.cam_cal_value_1 = int(self.config_flie.get("picarx_cam1_servo", default_value=0))
        self.cam_cal_value_2 = int(self.config_flie.get("picarx_cam2_servo", default_value=0))
        self.camera_servo_pin1.angle(self.cam_cal_value_1)
        self.camera_servo_pin2.angle(self.cam_cal_value_2)
        
        self.S0 = ADC('A0')
        self.S1 = ADC('A1')
        self.S2 = ADC('A2')

    def camera_servo1_angle_calibration(self,value):
        # global cam_cal_value_1
        self.cam_cal_value_1 = value
        self.config_flie.set("picarx_cam1_servo", "%s"%value)
        print("cam_cal_value_1:",self.cam_cal_value_1)
        self.camera_servo_pin1.angle(value)

    def camera_servo2_angle_calibration(self,value):
        # global cam_cal_value_2
        self.cam_cal_value_2 = value
        self.config_flie.set("picarx_cam2_servo", "%s"%value)
        print("picarx_cam2_servo:",self.cam_cal_value_2)
        self.camera_servo_pin2.angle(value)

    def set_camera_servo1_angle(self,value):
        # global cam_cal_value_1
        self.camera_servo_pin1.angle(-1*(value + -1*self.cam_cal_value_1))
        # print("self.cam_cal_value_1:",self.cam_cal_value_1)
        print((value + self.cam_cal_value_1))

    def set_camera_servo2_angle(self,value):
        # global cam_cal_value_2
        self.camera_servo_pin2.angle(-1*(value + -1*self.cam_cal_value_2))
        # print("self.cam_cal_value_2:",self.cam_cal_value_2)
        print((value + self.cam_cal_value_2))

    def get_adc_value(self):
        adc_value_list = []
        adc_value_list.append(self.S0.read())
        adc_value_list.append(self.S1.read())
        adc_value_list.append(self.S2.read())
        return adc_value_list

color_dict = {'red':[0,4],'orange':[5,18],'yellow':[22,37],'green':[42,85],'blue':[92,110],'purple':[115,165],'red_2':[165,180]}  #Here is the range of H in the HSV color space represented by the color

kernel_5 = np.ones((5,5),np.uint8) #Define a 5×5 convolution kernel with element values of all 1.

class Interpreter(object):
    # dark = 1, light = 0
    # polarity: line the system follows - higher sensitivity - polarity 0
    def __init__(self, polarity = 1, sensitivity = 200):
        self.polarity = polarity
        self.sensitivity = sensitivity

    def color_detect(img,color_name):

    # The blue range will be different under different lighting conditions and can be adjusted flexibly.  H: chroma, S: saturation v: lightness
    resize_img = cv2.resize(img, (160,120), interpolation=cv2.INTER_LINEAR)  # In order to reduce the amount of calculation, the size of the picture is reduced to (160,120)
    hsv = cv2.cvtColor(resize_img, cv2.COLOR_BGR2HSV)              # Convert from BGR to HSV
    color_type = color_name
    
    mask = cv2.inRange(hsv,np.array([min(color_dict[color_type]), 60, 60]), np.array([max(color_dict[color_type]), 255, 255]) )           # inRange()：Make the ones between lower/upper white, and the rest black
    if color_type == 'red':
            mask_2 = cv2.inRange(hsv, (color_dict['red_2'][0],0,0), (color_dict['red_2'][1],255,255)) 
            mask = cv2.bitwise_or(mask, mask_2)

    morphologyEx_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_5,iterations=1)              # Perform an open operation on the image 

    contours, hierarchy = cv2.findContours(morphologyEx_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)          # Find the contour in morphologyEx_img, and the contours are arranged according to the area from small to large

    color_area_num = len(contours) # Count the number of contours

    if color_area_num > 0: 
        for i in contours:    # Traverse all contours
            x,y,w,h = cv2.boundingRect(i)      # Decompose the contour into the coordinates of the upper left corner and the width and height of the recognition object

            # Draw a rectangle on the image (picture, upper left corner coordinate, lower right corner coordinate, color, line width)
            if w >= 8 and h >= 8: # Because the picture is reduced to a quarter of the original size, if you want to draw a rectangle on the original picture to circle the target, you have to multiply x, y, w, h by 4.
                x = x * 4
                y = y * 4 
                w = w * 4
                h = h * 4
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)  # Draw a rectangular frame
                cv2.putText(img,color_type,(x,y), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),2)# Add character description

    return img,mask,morphologyEx_img
     
        # robust to lighting conditions
        # [-1, 1] with respect to a edge detected
        # +1 = line left to the robot

    # def Lane_following(self):
    # example/color_detect.py
    # https://towardsdatascience.com/deeppicar-part-4-lane-following-via-opencv-737dd9e47c96 


class Controller(object):
    # and the angle by which to steer
    def __init__(self, picar, scaling_fac = 0.01):
        self.scaling_fac = scaling_fac
        self.picar = picar
        self.velocity = 60

    
    def controller(self, gm_status):
        # use the scaling factor and command a steer
        # the scaling factor between the interpreted offset from the line and the angle by which to steer
        if gm_status['str'] == 'forward':
            print("Moving Forward")
            self.picar.forward_improved(self.velocity) 
        elif gm_status['str'] == 'right':
            steer_angle = self.scaling_fac * abs(gm_status['diff'])
            self.picar.set_dir_servo_angle(steer_angle)
            print("Moving Right")
            self.picar.forward_improved(self.velocity) 
        elif gm_status['str'] == 'left':
            steer_angle = - self.scaling_fac * abs(gm_status['diff'])
            self.picar.set_dir_servo_angle(steer_angle)
            print("Moving Left")
            self.picar.forward_improved(self.velocity) 
        else:
            self.picar.set_dir_servo_angle(0)
            print("Stopping the car")
            self.picar.stop()

if __name__ == "__main__":
    px = Picarx()
    px.calibrate_steering()
    message = "Begin automatic steering"
    logging.debug( message )

    sm = Sensors()
    im = Interpreter(200)
    px = Picarx()
    cx = Controller(px)

    #init camera
    print("start color detect")
    camera = PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 24
    rawCapture = PiRGBArray(camera, size=camera.resolution)  


    for frame in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):# use_video_port=True
        img = frame.array
        img,img_2,img_3 =  color_detect(img,'red')  # Color detection function
        cv2.imshow("video", img)    # OpenCV image show
        cv2.imshow("mask", img_2)    # OpenCV image show
        cv2.imshow("morphologyEx_img", img_3)    # OpenCV image show
        rawCapture.truncate(0)   # Release cache
    
        k = cv2.waitKey(1) & 0xFF
        # 27 is the ESC key, which means that if you press the ESC key to exit
        if k == 27:
            camera.close()
            break

    while True:
        time.sleep(1)
        sm_val_list = sm.get_adc_value()
        print("sm_val_list:",sm_val_list)
        im_status = im.get_line_status(sm_val_list)
        print("im_status:",im_status)
        cx.controller(im_status)
        print("Steered")

        