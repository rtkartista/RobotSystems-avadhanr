import concurrent.futures as cf
import time
import sensors
import interpretor
import control
import picarxy_new as pcx
from rossros import *

if __name__ == "__main__":
    # termination, sensor and interpreter busses
    sensor_bus = Bus([1, 1, 1], 'Sensor Bus')
    interpreter_bus = Bus(0, 'Interpreter Bus')
    termination_bus = Bus(0, 'Termination Bus')
    
    # objects
    px = pcx.Picarx()
    sx = sensors.Sensors()
    ip = interpretor.Interpreter()
    cx = control.Controller(px)
    
    # thread delay time
    delay_time = 1

    wrapped_sensor = Producer(sx.sensor_producer, sensor_bus, delay_time, termination_bus,'sensor')
    wrapped_interpreter = ConsumerProducer(ip.interpreter_con_pro, sensor_bus, interpreter_bus, delay_time, termination_bus,'interpreter')
    wrapped_controller = Consumer(cx.control_producer, interpreter_bus, delay_time, termination_bus,'controller')
    wrapped_timer = Timer(termination_bus, 5, delay_time, termination_bus, 'termination timer')
    
     
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        eSensor = executor.submit(wrapped_sensor)
        eInterpreter = executor.submit(wrapped_interpreter)
        eController = executor.submit(wrapped_controller)
        eTimer = executor.submit(wrapped_timer)

    eSensor.result()
    eInterpreter.result()
    eController.result()
    eTimer.result()