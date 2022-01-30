from picarxy_new import *
class Interpreter(object):
    def __init__(self,ref = 1000):
        self.ref = ref


    def get_line_status(self,fl_list):

        if fl_list[0] > self.ref and fl_list[1] > self.ref and fl_list[2] > self.ref:
            return 'stop'
            
        elif fl_list[1] <= self.ref:
            return 'forward'
        
        elif fl_list[0] <= self.ref:
            return 'right'

        elif fl_list[2] <= self.ref:
            return 'left'


if __name__ == "__main__":
    import time
    px = Sensors()
    GM = Interpreter(950)
    cx = Controller()
    while True:
        data = px.get_grayscale_data()
        im_status = GM.get_line_status(data)
        cx.controller(im_status)
        time.sleep(1)