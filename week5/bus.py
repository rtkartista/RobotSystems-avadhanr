from readerwriterlock import rwlock
class Bus(object):
    def __init__(self):
        self.message = None
        self.lock = rwlock.RWLockWriteD()

    def read_message(self):
        with self.lock.gen_rlock():
            # print("read_message")
            message = self.message
        return message

    def write_message(self, message):
        with self.lock.gen_wlock():
            # print("write_message")
            self.message = message
