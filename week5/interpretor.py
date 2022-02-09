from picarxy_new import *
import numpy as np
class Interpreter(object):
    def __init__(self,ref = 1000, msg_calib = [10, 500]):
        self.ref = ref
        self.min = msg_calib[0]
        self.max = msg_calib[1]
        self.polarity = 0 # follow the light line
    
    def get_line_status(self,fl_list, calib_msg):
        #threshold for value robustness = 5
        threshold = 3
        # light
        if self.polarity == 0:
            if fl_list[0] > self.ref  and fl_list[1] > self.ref and fl_list[2] > self.ref:
                return 'stop'
            elif (fl_list[1]-self.ref) <= threshold:
                print("forward")
                return 'forward'
            
            elif (fl_list[0]-self.ref) <= threshold:
                print("right")
                return 'right'

            elif (fl_list[2]-self.ref) <=threshold :
                print("left")
                return 'left'
        # dark
        else:
            if fl_list[0] > self.ref  and fl_list[1] > self.ref and fl_list[2] > self.ref:
                return 'stop'
            elif (fl_list[1]-self.ref) <= threshold:
                print("forward")
                return 'forward'
            
            elif (fl_list[0]-self.ref) <= threshold:
                print("right")
                return 'right'

            elif (fl_list[2]-self.ref) <=threshold :
                print("left")
                return 'left'