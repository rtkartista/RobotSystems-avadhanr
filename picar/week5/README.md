## MultiModal Control
### sensing, interpretation, and control run independently and in parallel for two sensors
- Run the command `python3 ross_ultrasonic.py` on raspi to see a working system.

### Tasks
- Defined functions in `ross_ultrasonic.py` which has a variable takes in busses to read, interpret and utilize data from both sensors in between threads using rossros.
- Defined functions in `ross_linefollower.py` which has a variable takes in busses to read, interpret and utilize data from grayscale module and uses rossros to run the car.