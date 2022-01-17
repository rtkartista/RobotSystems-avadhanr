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

    picar.cali_angle = calibration_angle_error
        
def forward_improved(picar, speed):
    # assuming car base = .6m
    # constant angular velocity
    # left wheel velocity
    # right wheel velocity
    turn_radius = .15
    base_radius = .06
    car_w = speed/((base_radius/2) + turn_radius)
    current_angle = picar.dir_current_angle

    if current_angle != picar.cali_angle:
        # move left/right
        abs_current_angle = abs(current_angle)
        if (current_angle / abs_current_angle) < 0:
            speed_left = car_w * turn_radius
            speed_right = car_w * (turn_radius + base_radius)
            #print(str(speed_right)+ " "+str(speed_left))
            picar.set_motor_speed(1, speed_left)
            picar.set_motor_speed(2, -speed_right)
        elif (current_angle / abs_current_angle) > 0:
            speed_right = car_w * turn_radius
            speed_left = car_w * (turn_radius + base_radius)
            #print(str(speed_right)+ " "+str(speed_left))
            picar.set_motor_speed(1, speed_left)
            picar.set_motor_speed(2, -speed_right)
    else:
        # go straight
        picar.set_motor_speed(1, speed)
        picar.set_motor_speed(2, -speed)                  

def move_pp(picar, dir):
    if dir == -1:
        # start at the current location
        # steer right, move back
        # steer left, move back
        # steer0 forward
        picar.set_dir_servo_angle(40)
        forward_improved(picar, -100)
        time.sleep(3)
        picar.set_dir_servo_angle(-40)
        forward_improved(picar, -100)
        time.sleep(3)
        picar.set_dir_servo_angle(0)
        forward_improved(picar, 100)
        time.sleep(1)
    else:
        # start at the current location
        # steer left, move back
        # steer right, move back
        # steer0 forward
        picar.set_dir_servo_angle(-40)
        forward_improved(picar, -100)
        time.sleep(3)
        picar.set_dir_servo_angle(40)
        forward_improved(picar, -100)
        time.sleep(3)
        picar.set_dir_servo_angle(0)
        forward_improved(picar, 100)
        time.sleep(1)

def move_3pt(picar, dir):
        if dir == -1:
        # steer -90deg, forward
        # go backward
        # go forward for 180deg turn 
        picar.set_dir_servo_angle(-40)
        forward_improved(picar, 70)
        time.sleep(1)
        picar.set_dir_servo_angle(40)
        forward_improved(picar, -90)
        time.sleep(.9)
        picar.set_dir_servo_angle(-22)
        forward_improved(picar, 70)
        time.sleep(.9)
        picar.set_dir_servo_angle(0)

    else:
        # steer +90deg, forward
        # go backward
        # go forward for 180deg turn
        picar.set_dir_servo_angle(-40)
        forward_improved(picar, 100)
        time.sleep(5)
        forward_improved(picar, -100)
        time.sleep(3)
        forward_improved(picar, 100)
        time.sleep(3)
        picar.set_dir_servo_angle(0)
    
def move(picar, command):
    if command == "L":
        picar.set_dir_servo_angle(-40)
        forward_improved(picar, 100)
        time.sleep(3)
    elif command == "R":
        picar.set_dir_servo_angle(40)
        forward_improved(picar, 100)
        time.sleep(3)
    if command == "L":
        picar.set_dir_servo_angle(0)
        forward_improved(picar, 30)
        time.sleep(3)
    elif command == "R":
        picar.set_dir_servo_angle(0)
        forward_improved(picar, -30)
        time.sleep(3)
    #parallel parking
    elif command == "PPR":
        move_pp(picar, 1)
    elif command == "PPL":
        move_pp(picar, -1)
    #three point turning
    elif command == "3PR":
        move_3pt(picar, 1)
    elif command == "3PL":
        move_3pt(picar, -1)

def user_input(picar):
    print("Enter the following commands to move the vehicle.")
    print("-------------------------------------------------")
    print("Left - 'L', Right - 'R', Front - 'F', Back - 'B'")
    print("Steer+Left - 'SL', Steer+Right - 'SR', Parallel parking - 'PPL' / 'PPR'")
    print("Three-point turning - '3L'/'3R'")
    while(1):
        val = input("Type in here-> ")
        move(picar, val)

if __name__ == "__main__":
    px = picarxy_improved.Picarx()
    calibrate_steering(px)
    print("Use "+str(px.cali_angle)+" to modify steering commands.")
    # calibrate everytime the car boots.
    forward_improved(px, 30)
    time.sleep(1)
    px.set_dir_servo_angle(15)
    forward_improved(px, 70)
    time.sleep(3)
    user_input(px)

    # shows a command saying KeyboardInterrupt, and calls the func stop
    atexit.register(px.stop)
    message = "Calibrated the steering"
    logging.debug(message)
