from turtle import left
from picarxy_new import *
import numpy as np
class Interpreter(object):
    def __init__(self, polarity = 0, sensitivity = 0.25):
        self.sensitivity = sensitivity # brightness adjustment
        self.polarity = polarity # follow the light line by default
        self.threshold = .25

    def get_line_status_old(self,fl_list):
        # follow dark
        if self.polarity == 0:
            # 000
            if fl_list[0] > self.sensitivity  and fl_list[1] > self.sensitivity and fl_list[2] > self.sensitivity:
                print("stop")
                return 'stop'
            # 111
            # 110
            # 011 
            # 010
            elif fl_list[1] <= self.sensitivity:
                print("forward")
                return 'forward'
            # 001
            # 101
            elif fl_list[1] > self.sensitivity and fl_list[2] <= self.sensitivity:
                print("right")
                return 'right'
            # 100
            elif fl_list[0] <= self.sensitivity  and fl_list[1] > self.sensitivity:
                print("left")
                return 'left'

        # follow light
        else:
            # 000
            # 001
            # 100
            # 101
            if fl_list[0] > self.sensitivity  and fl_list[1] > self.sensitivity and fl_list[2] > self.sensitivity:
                return 'forward'
            # 111
            elif fl_list[1] <= self.sensitivity:
                print("stop")
                return 'stop'
            # 110
            # 010
            elif fl_list[1] <= self.sensitivity and fl_list[2] > self.sensitivity:
                print("right")
                return 'right'
            # 011
            elif fl_list[0] > self.sensitivity  and fl_list[1] <= self.sensitivity:
                print("left")
                return 'left'

    def get_line_status(self,fl_list):
        # send out an differential direction
        # nomalizing sensor reading between 0 and 1
        normalize = [float(i)/max(fl_list) for i in fl_list]
        max_diff = max(normalize)-min(normalize)

        # if difference exceeds brightness diff threshold
        if max_diff > self.threshold:
            left_diff = normalize[1] - normalize[0]
            right_diff = normalize[1] - normalize[2]
            # follow light
            if self.polarity == 1:
                # 000
                if normalize[0] > self.sensitivity and normalize[1] > self.sensitivity and normalize[2] > self.sensitivity:
                    print("stop")
                    return 1
                # 001
                # 101
                elif normalize[1] > self.sensitivity and normalize[2] <= self.sensitivity:
                    print("right")
                    return right_diff
                # 100
                elif normalize[0] <= self.sensitivity and normalize[1] > self.sensitivity:
                    print("left")
                    return -left_diff

            # follow dark
            else:
                # 111
                if normalize[1] <= self.sensitivity:
                    print("stop")
                    return 1
                # 110
                # 010
                elif normalize[1] <= self.sensitivity and normalize[2] > self.sensitivity:
                    print("right")
                    return right_diff
                # 011
                elif normalize[0] > self.sensitivity and normalize[1] <= self.sensitivity:
                    print("left")
                    return left_diff

        else:
            rel_dir = 0
        return rel_dir
        
    def interpreter_con_pro(self, bus_class1, bus_class2, delay_time):
        while(1):
            print("interpreter_con_pro")
            msg = bus_class1.read_message()
            msg2 = self.get_line_status(msg)
            bus_class2.write_message(msg2)
            print(msg, msg2)
            time.sleep(delay_time)
