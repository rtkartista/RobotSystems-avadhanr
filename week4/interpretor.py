from picarxy_new import *
import numpy as np
class Interpreter(object):
    def __init__(self,ref = 1000):
        self.ref = ref

    def calibrate(self):
        all_vals = []
        for i in range(100): 
            all_vals.append(self.get_grayscale_data())
        all_vals = np.array(all_vals)
        mean = all_vals.mean(axis=0)
        std = all_vals.std(axis=0)
        return (mean, std)
    
    def get_line_status(self,fl_list):
        #threshold for value robustness = 5
        threshold = 3
        

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
