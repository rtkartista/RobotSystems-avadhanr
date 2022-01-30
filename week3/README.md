## Sensors and Control
### Tasks
* In the `picarxy_new.py` just created a separate class to handle camera controlling sensors to increase modularity
* Grayscale module - `grayscale.py`
    1. Creted a new class to handle the grayscale sensor
    2. added a method to populate it with sensor values based on the picar-x lib
    3. created a method to interpret the sensor data and send in the high level control commands to the picar-x
    4. Controller class created in the `picar_new.py` which takes in the status from the interpretors and move the vehicle.
* Camera lane detection `camera_w3.py`
    1. Followed the tutorials from `https://towardsdatascience.com/deeppicar-part-4-lane-following-via-opencv-737dd9e47c96` to detect lanes and move the vehicle.
    2. Created a navigate class in the `camera_w3.py` file to read and interpret the camera data
    3. Based on the steering angle calculated, the picar object is called in a loop to steer and move forward as long as the car sees lanes.

- Installed the following raspi-cam libraries
`$ sudo apt-get install python3-picamera`
`$ sudo apt-get install python3-pip`

* Due to difficulties running the camera with the raspberry pi 3+ board, I was not able to test out the code properly to calibrate it with my robot car.

* A simple command to capture an image form raspi-cam
`$ raspistill -o output.jpg`
