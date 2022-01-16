import picarxy_improved
import atexit
import time
import logging

logging_format = "%(asctime) s:%(message) s "
logging.basicConfig( format = logging_format , level = logging.INFO ,datefmt ="%H:%M:%S")

logging.getLogger().setLevel( logging.DEBUG )

def calibrate_steering(picar):
    calibration_angle_error = -10
    picar.set_dir_servo_angle(calibration_angle_error)
    time.sleep(2)
    #picar.forward(30)
    #time.sleep(5)

    picar.cali_angle = calibrated_ang_error

"""def move_pp(picar, dir):
    # move forward, make your steering parallel vehicle
    # dir - left - steering right
    # move backward 50%
    # right - steering left
    # move - backward 50%
    # steer 0 
    # forward
    #==================================================
    # dir - right - steering left
    # move backward 50%
    # dir - left - steering right
    # move - backward 50%
    # steer 0 
    # forward

def three_point_turning(picar, dir):
    # dir - left
    # steer -90deg, forward
    # go backward
    # go forward for 180deg turn 
    #==============================
    # dir - right
    # steer +90deg, forward
    # go backward
    # go forward for 180deg turn 

def move_basic(picar, dir):
    # with steer (f/b)
    # without steer (f/b)"""
    
"""def move(picar):
    #move front
    #move back
    #parallel parking
    #three point turning

def user_input(picar):
    print("Enter the following commands to move the vehicle.")
    print("-------------------------------------------------")
    print("Left - 'L', Right - 'R', Front - 'F', Back - 'B'")
    print("Steer+Left - 'SL', Steer+Right - 'SR', Parallel parking - 'PPL' / 'PPR'")
    print("Three-point turning - '3L'/'3R'")
    while(1):
        val = input("Type in here-> ")
        if val == "L":
            picar.set_dir_servo_angle(90)
            picar.forward(30)
            time.sleep(5)
        elif val == "R":
            picar.set_dir_servo_angle(-90)
            picar.forward(30)
            time.sleep(5)
        elif val == "F":
            picar.forward(30)
            time.sleep(5)
        elif val == "B":
            picar.backward(30)
            time.sleep(5)"""

def forward_improved(picar, speed):
    # assuming car base = .6m
    # constant angular velocity
    # left wheel velocity
    # right wheel velocity
    turn_radius = .25
    base_radius = .6
    car_w = speed/((base_radius/2) + turn_radius)
    current_angle = picar.dir_current_angle

    if current_angle != picar.cali_angle:
        # move left/right
        abs_current_angle = abs(current_angle)
        # if abs_current_angle >= 0:
        if abs_current_angle > 40:
            abs_current_angle = 40
        
        if (current_angle / abs_current_angle) > 0:
            speed_left = car_w * turn_radius
            speed_right = -car_w * (turn_radius + base_radius)
            picar.set_motor_speed(1, speed_left)
            picar.set_motor_speed(2, speed_right)
        elif (current_angle / abs_current_angle) < 0:
            speed_right = car_w * turn_radius
            speed_left = -car_w * (turn_radius + base_radius)
            picar.set_motor_speed(1, speed_left)
            picar.set_motor_speed(2, speed_right)
    else:
        # go straight
        picar.set_motor_speed(1, speed)
        picar.set_motor_speed(2, -1*speed)                  
            
if __name__ == "__main__":
    px = picarxy_improved.Picarx()
    calibrate_steering(px)
    print("Use "+px.cali_angle+" to modify steering commands.")
    # calibrate everytime the car boots.
    forward_improved(px, 30)
    time.sleep(3)
    px.set_dir_servo_angle(30)
    forward_improved(px, 30)
    time.sleep(3)
    """px.set_dir_servo_angle(-30)
    forward_improved(px,30)
    time.sleep(3)"""
    #user_input(px)
    #move(px)
    # shows a command saying KeyboardInterrupt, and calls the func stop
    atexit.register(px.stop)
    message = "Calibrated the steering"
    logging.debug(message)