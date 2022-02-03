from readerwriterlock import rwlock
import concurrent.futures as cf
import time
import bus
import sensors
import interpretor
import control

# below three functions are run in a loop with a delay
def sensor_producer(bus_class, delay_time):
    sx = sensors.Sensors()
    while(1):
        msg = sx.get_adc_value()
        bus_class.write_message(msg)
        time.sleep(delay_time)

def interpreter_con_pro(bus_class1, bus_class2, delay_time):
    ip = interpretor.Interpreter()
    while(1):
        msg = bus_class1.read_message()
        msg2 = ip.get_line_status(msg)
        bus_class2.write_message(msg2)
        time.sleep(delay_time)

def control_producer(bus_class, delay_time):
    con = control.Controller()
    while(1):
        msg = bus_class.read_message()
        con.controller(msg)
        time.sleep(delay_time)


if __name__ == "__main__":
    # sensor output
    bus_obj1 = bus.Bus()
    # interpreter output
    bus_obj2 = bus.Bus()
    delay_time = 0.5
    with cf.ThreadPoolExecutor(max_workers = 3) as executor :
        eSensor = executor.submit(sensor_producer, bus_obj1, delay_time)
        eInterpreter = executor.submit(interpreter_con_pro, bus_obj1, bus_obj2, delay_time)
        eController = executor.submit(control_producer, bus_obj2, delay_time)