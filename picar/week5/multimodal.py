import sys
sys.path.insert(1, '../../picar-x/lib')
from rossros import *
import rossros as rs 
from picarx_improved import Picarx
from controller import Controller
from interpreter import Interpreter
from sensor import Sensor
from ultrasonic import Ultrasonic
from interpret_ultrasonic import InterpretUltrasonic
from control_ultrasonic import ControlUltrasonic

import logging

logging.basicConfig(level=logging.DEBUG)

#### Multitasking
if __name__=="__main__":

    default_termination_bus = Bus(False)
    car = Picarx()

    sensor_input_bus = Bus()
    interpret_output_bus = Bus()

    sensor = Sensor()
    interpret = Interpreter(sensor.polarity, sensor.sensitivity)
    control_car = Controller(car, 20.0)

    ultrasonic_input_bus = Bus()
    ultrasonic_interpret_output_bus = Bus()

    ultrasonic_sensor = Ultrasonic()
    ultrasonic_interpret = InterpretUltrasonic()
    ultrasonic_control = ControlUltrasonic(car)


    consumer_producer = ConsumerProducer(interpret.output, 
                                        input_busses=sensor_input_bus, 
                                        output_busses=interpret_output_bus,
                                        delay=1.0,
                                        termination_busses=default_termination_bus,
                                        name="interpret_sensor_cp")
    producer = Producer(sensor.read,
                 sensor_input_bus,
                 delay=1.0,
                 termination_busses=default_termination_bus,
                 name="sensor_p")
    
    consumer = Consumer(control_car.control,
                 interpret_output_bus,
                 delay=1.0,
                 termination_busses=default_termination_bus,
                 name="control_c")
    
    consumer_producer_ultrasonic = ConsumerProducer(ultrasonic_interpret.output, 
                                        input_busses=ultrasonic_input_bus, 
                                        output_busses=ultrasonic_interpret_output_bus,
                                        delay=1.0,
                                        termination_busses=default_termination_bus,
                                        name="ultrasonic_interpret_sensor_cp")
    producer_ultrasonic = Producer(ultrasonic_sensor.read,
                 ultrasonic_input_bus,
                 delay=1.0,
                 termination_busses=default_termination_bus,
                 name="ultrasonic_p")
    
    consumer_ultrasonic = Consumer(ultrasonic_control.control,
                 ultrasonic_interpret_output_bus,
                 delay=1.0,
                 termination_busses=default_termination_bus,
                 name="ultrasonic_control_c")

    timer_producer = Timer(default_termination_bus,  # busses that should be set to true when timer triggers
                 duration=10.0,  # how many seconds the timer should run for (0 is forever)
                 delay=0,  # how many seconds to sleep for between checking time
                 termination_busses=default_termination_bus,
                 name="timer_p")

    producer_consumer_list = [producer, consumer_producer, consumer, producer_ultrasonic, consumer_producer_ultrasonic, consumer_ultrasonic, timer_producer]
    # producer_consumer_list = [producer, consumer_producer, consumer, timer_producer]
    # producer_consumer_list = [producer_ultrasonic, consumer_producer_ultrasonic, consumer_ultrasonic, timer_producer]


    rs.runConcurrently(producer_consumer_list)