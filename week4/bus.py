from readerwriterlock import rwlock
class Bus(object):
    def __init__(self):
        self.message = None
        self.lock = rwlock.RWLockWriteD()

    def read_message(self):
        print("returns message")
        with self.lock.gen_rlock():
            message = self.message
        return message

    def write_message(self, message):
        with self.lock.gen_wlock():
            self.message = message