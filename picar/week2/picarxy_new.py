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

# added the calibrate_steering and the forward_improved funtions to the picar class
# removed the sensor methods from the class for future week assignments
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
        
        # shows a command saying KeyboardInterrupt, and calls the function cleanup from the picar methods
        atexit.register(self.cleanup)


    # commented out the speed scaling to get remove the friction compensation from the motor speed
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
    
    # creating an variable self.cali_angle that generates an effective steer angle 
    # keeping the installation error in mind
    def set_dir_servo_angle(self,value):
        # global dir_cal_value
        angle_value  = value + self.cali_angle
        
        # checking for maximum angles the vehicle can maechanically move
        # setting 40deg as the maximum angle on both sides from the centerline
        if angle_value >= 0 and angle_value > 40 + self.cali_angle:
            self.dir_current_angle = 40 + self.cali_angle
        elif angle_value < 0 and angle_value < -40 + self.cali_angle:
            self.dir_current_angle = -40 + self.cali_angle
        else:
            self.dir_current_angle = angle_value
        # print("servo angle after calibration:",self.dir_current_angle)
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

    # the below lines log everytime the forward function starts and ends
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

    # The function is called at the begining of the code to calinrate the zero of the steering
    # Due to the installation error, the steer servo is installed at a -5deg from the centerline 
    def calibrate_steering(self):
        calibration_angle_error = -5
        self.set_dir_servo_angle(calibration_angle_error)
        time.sleep(2)
        #picar.forward(30)
        #time.sleep(5)
        self.cali_angle = calibration_angle_error

    # Using a fixed turn radius, the motors speeds are calulated for the car
    # these motor speeds move the vehicle on the function call
    def forward_improved(self, speed):
        # assuming car base = .06m
        # constant angular velocity
        # calculate
        #### left wheel velocity
        #### right wheel velocity
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



if __name__ == "__main__":
    px = Picarx()
    px.forward(5)
    time.sleep(1)
    message = "here goes the message"
    logging.debug( message )
