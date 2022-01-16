import picarxy_improved
import atexit
import time
import logging

logging_format = "%(asctime) s:%(message) s "
logging.basicConfig( format = logging_format , level = logging.INFO ,datefmt ="%H:%M:%S")

logging.getLogger().setLevel( logging.DEBUG )

def calibrate_steering(picar):
    picar.set_dir_servo_angle(90)
    
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
    val = input("Type in here-> ")
    while(1):
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
        
        

if __name__ == "__main__":
    px = picarxy_improved.Picarx()
    px.forward(5)
    time.sleep(1)
    calibrate_steering(px)
    px.forward(5)
    # shows a command saying KeyboardInterrupt, and calls the func stop
    atexit.register(px.stop)
    time.sleep(1)
    message = "Calibrated the steering"
    logging.debug(message)

    px.stop()
    