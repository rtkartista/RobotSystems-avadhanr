
from picarxy_new import *

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
