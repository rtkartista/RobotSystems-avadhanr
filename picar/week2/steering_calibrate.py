import picarxy_improved
import atexit
import time
import logging

# logging the message with the at a respective timestamp
logging_format = "%(asctime) s:%(message) s "
logging.basicConfig( format = logging_format , level = logging.INFO ,datefmt ="%H:%M:%S")

logging.getLogger().setLevel( logging.DEBUG )

# The function is called at the begining of the code to calinrate the zero of the steering
# Due to the installation error, the steer servo is installed at a -5deg from the centerline 
def calibrate_steering(picar):
    calibration_angle_error = -5
    picar.set_dir_servo_angle(calibration_angle_error)
    time.sleep(2)
    #picar.forward(30)
    #time.sleep(5)
    picar.cali_angle = calibration_angle_error

# Using a fixed turn radius, the motors speeds are calulated for the car
# these motor speeds move the vehicle on the function call
def forward_improved(picar, speed):
    # assuming car base = .06m
    # constant angular velocity
    # calculate
    #### left wheel velocity
    #### right wheel velocity
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

# this function helps the vehicle to perform parallel parking
# this function utilizes the new forward_improved function to move the car
def move_pp(picar, dir):
    if dir == -1:
        # start at the current location
        # steer right, move back
        # steer left, move back
        # steer0 forward
        picar.set_dir_servo_angle(-31)
        forward_improved(picar, -70)
        time.sleep(.45)
        picar.set_dir_servo_angle(28)
        forward_improved(picar, -70)
        time.sleep(.4)
        picar.set_dir_servo_angle(0)
        forward_improved(picar, 30)
        time.sleep(1)
        picar.stop()
    else:
        # start at the current location
        # steer left, move back
        # steer right, move back
        # steer0 forward
        picar.set_dir_servo_angle(40)
        forward_improved(picar, -70)
        time.sleep(.45)
        picar.set_dir_servo_angle(-30)
        forward_improved(picar, -70)
        time.sleep(.41)
        picar.set_dir_servo_angle(0)
        forward_improved(picar, 30)
        time.sleep(1)
        picar.stop()

# this function helps the vehicle to perform three point turn
# this function utilizes the new forward_improved function to move the car
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
        # steer -90deg, forward
        # go backward
        # go forward for 180deg turn 
        picar.set_dir_servo_angle(35)
        forward_improved(picar, 70)
        time.sleep(1.2)
        picar.set_dir_servo_angle(-35)
        forward_improved(picar, -90)
        time.sleep(.9)
        picar.set_dir_servo_angle(18)
        forward_improved(picar, 70)
        time.sleep(.9)
        picar.set_dir_servo_angle(0)

# this function helps the vehicle to perform various maneuvers
# this function utilizes the new forward_improved function to perform basic moves with and without the steer
def move(picar, command):
    if command == "L":
        picar.set_dir_servo_angle(-40)
        forward_improved(picar, 70)
        time.sleep(1)
        picar.stop()
    elif command == "R":
        picar.set_dir_servo_angle(40)
        forward_improved(picar, 70)
        time.sleep(1)
        picar.stop()
    if command == "F":
        picar.set_dir_servo_angle(0)
        forward_improved(picar, 30)
        time.sleep(3)
        picar.stop()
    elif command == "B":
        picar.set_dir_servo_angle(0)
        forward_improved(picar, -30)
        time.sleep(3)
        picar.stop()
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

# this funtion imforms the user about all the available vehicle maneuvers
# type in an input to see the vehicle perform the respective maneuvers
def user_input(picar):
    print("Enter the following commands to move the vehicle.")
    print("-------------------------------------------------")
    print("Left - 'L', Right - 'R', Front - 'F', Back - 'B'")
    print("Parallel parking - 'PPL' / 'PPR'")
    print("Three-point turning - '3PL'/'3PR'")
    while(1):
        val = input("Type in here-> ")
        move(picar, val)

if __name__ == "__main__":
    px = picarxy_improved.Picarx()

    # calibrate everytime the car boots.
    calibrate_steering(px)
    message = "Calibrated the steering"
    logging.debug(message)
    print("Using "+str(px.cali_angle)+" to modify steering commands.")
    
    # move the vehicle
    user_input(px)

    