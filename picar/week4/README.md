## Simultaneity
### sensing, interpretation, and control run independently and in parallel
- Multitasking, in which a single processor rapidly switches between the different functions it is executing, and
    - cooperative -  the time-sharing of the processor is determined by the functions themselves
    - preemtive - threading -  the time-sharing of the processor is allocated externally by the computer’s operating system
- Multiprocessing, in which the functions are assigned to dedicated processors.

### Tasks
1. Defined functions in `concurrency.py` which has a variable takes in busses to read, interpret and utilize the sensor data in between threads. Defined a producer, consumer-producer, or consumer functions for the sensor, interpretation and control processes from week 3 using only the grayscale module.
3. The three defined functions are called in a loop in the `concurrency.py function`.

### Installations
1. readerwriterlock Python module - `python3 -m pip install -U readerwriterlock`

### Observations
1. in the assignment, `readerwriterlock` was used to set the following three priorities
    - Only one thread is allowed to write the bus message at any given time, and may not start writing while any other thread is reading the message, to avoid in mistakes in updating the messages
    - Any number of threads may read the bus message at any given time, but may not start reading while a thread is writing the message, to avoid reading incorrect data
    - Write operations are given priority over read operations, to allow most uptodate information in use.
