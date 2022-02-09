from readerwriterlock import rwlock
import concurrent.futures as cf
import time
import bus
import sensors
import interpretor
import control

# below three functions are run in a loop with a delay
if __name__ == "__main__":
    # sensor output
    bus_obj1 = bus.Bus()
    # interpreter output
    bus_obj2 = bus.Bus()
    
    # sic objects
    sx = sensors.Sensors()
    ip = interpretor.Interpreter()
    cx = control.Controller(5)
    
    # thread delay time
    delay_time = 1
    with cf.ThreadPoolExecutor(max_workers = 3) as executor :
        print("Begin pooling...")
        eSensor = executor.submit(sx.sensor_producer, bus_obj1, delay_time)
        eInterpreter = executor.submit(ip.interpreter_con_pro, bus_obj1, bus_obj2, delay_time)
        eController = executor.submit(cx.control_producer, bus_obj2, delay_time)

    eSensor.result()
    eInterpreter.result()
    eController.result()
