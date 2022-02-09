from picarxy_new import *
import numpy as np
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
        
    def sensor_producer(bus_class, delay_time):
        while(1):
            print("sensor_producer")
            msg = self.get_adc_value()
            bus_class.write_message(msg)
            print(msg)
            time.sleep(delay_time)

