# Picar - Intro to Robotics 2
## Motor Commands
### Media
1. Car moving front and back 
* <img src="FB.gif" width="779" height="414" />
2. Steering + moving left and right 
- <img src="Steer.gif" width="779" height="414" />

3. Parallel Parking + left 
- <img src="ppl_Trim.gif" width="779" height="414" />
4. Parallel Parking + right 
- <img src="ppr.gif" width="779" height="414" />

5. Three point turning + left 
- <img src="3ptl.gif" width="779" height="414" />
6. Three point turning + right 
- <img src="3ptr.gif" width="779" height="414" />

### Gather code pieces
- created a file *sim_ezblock.py* and added the classes used in the picarxy.py example.
- modified the usage of smbus in file since *import smbus* command is used rather than *import smbus as SMBus*. Also added RPi.GPIO module to the file
- Copied the *picarxy.py* code to *picarxy_improved.py*. Tested the robot using the *Picar* class's *forward* method
- added these filed to the git RobotSystems_avadhanr repository which can be cloned using the below command
`git clone https://github.com/rtkartista/RobotSystems-avadhanr.git`
- the *picarxy_improved.py* checks for the ezblock lib to import, if the system doesnt have it installed, it imports the modules from the *sim_ezblock.py*.

### Logging
- imported logging and logdecorator modules.
- defined the basic format for logging.
- used *log_on_start , log_on_end* before the Picar.forward function and print out the speed the vehicle moves with and when the code jumps out of the function.

### Improving Picar code in *picarxy_imporved.py* & *steering_calibrate.py*
- added atexit funtions in the class *__init__* function
- due to placement error while installing the servo, the caliration angle for the servo is -5deg. At the start of the motion, the vehicle is calibrated. This angle is also saved as a class variable and used in the function *set_dir_servo_angle* to give out correct steering results 
- The friction contibution from the *set_motor_speed* method is also removed and it was obseved that my vehicle moved at 30m/s after overcoming static friction.
- a forward_imporved function is written to account for variation of motor speeds in both the directions when the vehicle has a sterr angle. 
    * Base width is assumed to be 12cm
    * Turn angle is assumed to be 25cm
    * Based on the formule *V_car = w_car \* turn_radius*, *V_left* and *V_right* are calulated by first calcuating the *w_car* and later by substituting different effective *turn_radius* for each wheel.

### Maneuvering
#### Disclaimer: since the friction influence is removed from the motor commands, trimming of velocities is needed to exactly perform the below maneuvers on new surfaces. The videos shown above were performed on carpeted floors. Another factor affecting the motor speeds is the battery charge. 
A *user_input* function was written in the *sterring_calibrate.py* script which asks the user for a input and executes the following motion:
1. Moving forward/backwards with or without sterring - using the forward_improved function, based on the user input the vehicle moves front or back
2. Parallel parking - using the move_pp function, based on the user input, the vehicle performs this action.
3. Three point turn - using the move_3pt funtion, based on the user input, the vehicle performs this action.

### Organizing the code *picarxy_new.py*
- Added a cleanup function to the picar class, it calls the stop function which makes the motor velocities zero when called. This cleanup function is called when the code is terminated giving the robot a smooth exit instead of moving with a constant velocity continously even after the code is terminated.
- Creating a new code *picarxy_new.py* with only motor commands to add future sensor funtions in it later. Also added init method of the class with respective class variables.
