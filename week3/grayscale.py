from picarxy_new import *
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

        #assume gaussian noise and accept values within 1 std of the mean as that sensor value. 
        return (mean, std)
    
    #main sensing loop
    def get_line_status(self,fl_list):
        # roboustness check(can we rely on the data recieved), is the car slightly away from the mean or largely away 
        # take the 95% confidence interval calculate z-score
        polarity = fl_list[2]
        z = (self.ref-fl_list[0])/fl_list[1]
        if(z>2.0): 
            print("please keep the car aligned to the tape")
            return "stop"
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

if __name__ == "__main__":
    import time
    px = Sensors()
    GM = Interpreter(950)
    (m, sdev)=GM.calibrate()
    polarity = 1
    cx = Controller()
    while True:
        data = px.get_grayscale_data()
        im_status = GM.get_line_status(m[1], sdev[1], data)
        cx.controller(im_status)
        time.sleep(1)