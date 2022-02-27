
from picarxy_new import *

class Controller(object):
    # and the angle by which to steer
    def __init__(self, picar, scaling_fac = 5):
        self.scaling_fac = scaling_fac
        self.picar = picar
        self.velocity = 60
    
    def controller_old(self, gm_status):
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

    def controller(self, direction):
        # controller with finer interpreter
        if direction == 1:
            self.picar.set_dir_servo_angle(0)
            print("Stopping the car")
            self.picar.stop()
        else:
            self.picar.set_dir_servo_angle(self.scaling_fac * direction)
            print("Moving")
            self.picar.forward_improved(self.velocity)
    
    def controller_new(self, direction, controller_u_status = 0):
        # controller with finer interpreter
        if direction == 1 or controller_u_status == 1:
            self.picar.set_dir_servo_angle(0)
            print("Stopping the car")
            self.picar.stop()
        else:
            self.picar.set_dir_servo_angle(self.scaling_fac * direction)
            print("Moving")
            self.picar.forward_improved(self.velocity)
    

    def controller_u(self,command,direction):
        if command == 1:
            print('STOPPING')
            self.picar.stop()
            return 1
        elif command == 0:
            print('GOING')
            speed = -40*abs(direction) + 50
            self.picar.forward_improved(speed)
            return 0 

    def control_producer(self, bus_class, delay_time):
        while(1):
            print("control_producer")
            msg = bus_class.read_message()
            self.controller(msg)
            time.sleep(delay_time)
