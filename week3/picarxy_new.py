#from ezblock import Servo,PWM,fileDB,Pin,ADC
import logging
import logdecorator
import atexit

import time
try :
    from ezblock import *
    from ezblock import __reset_mcu__
    __reset_mcu__ ()
    time.sleep (0.01)
except ImportError :
    print (" This computer does not appear to be a PiCar - X system ( ezblock is not present ) . Shadowing hardware calls with substitute functions ")
    from sim_ezblock import *

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

class Interpreter(object):
    # dark = 1, light = 0
    # polarity: line the system follows - higher sensitivity - polarity 0
    def __init__(self, polarity = 0, sensitivity = 200):
        self.polarity = polarity
        self.sensitivity = sensitivity

    def get_line_status(self,fl_list):
        d = dict(); 
        # add code regarding polarity
        # l l l
        if fl_list[0] <= self.sensitivity and fl_list[1] <= self.sensitivity and fl_list[2] <= self.sensitivity:
            diff = fl_list[1] - fl_list[2]
            d['str'] = 'stop'
            d['diff'] = diff
            return d
        # d d d    
        elif fl_list[0] > self.sensitivity and fl_list[1] > self.sensitivity and fl_list[2] > self.sensitivity:
            diff = fl_list[1] - fl_list[2]
            d['str'] = 'forward'
            d['diff'] = diff
            return d
        # l l d
        elif fl_list[0] <= self.sensitivity and fl_list[1] <= self.sensitivity and fl_list[2] > self.sensitivity:
            diff = fl_list[1] - fl_list[2]
            d['str'] = 'right'
            d['diff'] = diff
            return d
        # d d l
        elif fl_list[0] > self.sensitivity and fl_list[1] > self.sensitivity and fl_list[2] <= self.sensitivity:
            diff = fl_list[1] - fl_list[2]
            d['str'] = 'left'
            d['diff'] = diff
            return d
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
        self.velocity = 70

    
    def controller(self, gm_status):
        # use the scaling factor and command a steer
        # the scaling factor between the interpreted offset from the line and the angle by which to steer
        if gm_status['str'] == 'forward':
            print("Moving Forward")
            self.picar.forward_improved(self.velocity) 

        elif gm_status['str'] == 'right':
            steer_angle = self.scaling_fac * gm_status['diff']
            self.picar.set_dir_servo_angle(steer_angle)
            print("Moving Right")
            self.picar.forward_improved(self.velocity) 

        elif gm_status['str'] == 'left':
            steer_angle = self.scaling_fac * gm_status['diff']
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
    while True:
        sm_val_list = sm.get_adc_value()
        print("sm_val_list:",sm_val_list)
        im_status = im.get_line_status(sm_val_list)
        print("im_status:",im_status)
        cx.controller(im_status)
        print("Steered")
        time.sleep(1)

        