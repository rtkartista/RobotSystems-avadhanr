from readerwriterlock import rwlock
import concurrent.futures

class Concurrency(object):
    def __init__(self):
        self.message = "store message to transfer"
        self.lock = rwlock.RWLockWriteD()


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