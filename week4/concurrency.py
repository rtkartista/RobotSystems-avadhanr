from readerwriterlock import rwlock
import concurrent.futures as cf

class Concur(object):
    def __init__(self):
        self.message = "sensor value"
        self.lock = rwlock.RWLockWriteD()
        self.sensor_delay = 1
        self.interpreter_delay = 1
        self.controller_delay = 1


    def read_message(self):
        print("returns message")
        with self.lock.gen_rlock():
            message = self.message
        

    def write_message(self):
        print("writes message")
        with self.lock.gen_wlock():
            self.message = message

    # below three functions are run in a loop with a delay
    def sensor_producer():
        print("")

    def interpreter_con_pro(self, bus_class, delay_time):
        while(1):
            print("")
    
    def control_producer(self):
        print("")

if __name__ == "__main__":
    concur_obj = Concur()
    with cf.ThreadPoolExecutor(max_workers = 3) as executor :
        eSensor = executor.submit(concur_obj.sensor_producer, concur_obj.write_message, concur_obj.sensor_delay)
        eInterpreter = executor.submit(concur_obj.interpreter_con_pro, concur_obj.write_message, concur_obj.read_message, concur_obj.interpreter_delay)
        eController = executor.submit(concur_obj.control_producer, concur_obj.read_message, concur_obj.controller_delay)
    eSensor.result()
