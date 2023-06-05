# Human Centric Production Operator Digital Twin


## Project Work - CRAS13

### Objective
The objective was to create a digital twin of a human operator working in a functioning production unit in unison with a robot and a production line. This would allow us to monitor the state of the human and the production unit in real time, which would allow us to affect the production in order to improve the operators condition.

### Results

The result of the project is that we have a production line which adapts its execution according to the humans measured heart rate. The human’s condition also affects how much the MiR 100 robot is used in the transportation of the workpieces, for example: if the human is stressed, then the robot is utilized more. This whole process is then visualized in a Visual Components 3D-model in real time, which we can also use to trigger certain actions to try and get the operator to be in an optimal state, for example by triggering sound cues.


## Folders

### GUI and Process Control Script
GUI and Process Control Script folder contains Main_Control.py and main_interface_functions.py which are required for running the GUI. Please also make sure mir_client.py, music.mp3 and the pictures are in the same folder while executing the GUI scripts. mir_client.py makes use of the MIR API, music.mp3 is the relaxing music that will be played by the GUI when the human operator is stressed and the images are for pyautogui which is used to automatically click no in the prompt when the human operator takes too much time or forgets to press yes. In addition to that, the folder also contains process control script which controls the production process and schedules the production scenarios.

### Sensor Codes
Sensor Codes folder contains all the necessary scripts required to connect to the sensor and retrieve the heart-rate values in real-time.  ESP32_BLE_HRM_MQTT.ino code should be uploaded in the esp32 using the Arduino IDE and db-collector.py is used for retrieving the heart-rate values and post in the MongoDB(sensor database). Then, decision-making.py is used for getting those sensor values from the sensor database and make a decision on human worker condition.

### Additional Files
Additional Files folder contains heart-rate generator mock file(db-collector-mock.py) for testing purposes. db-collector-mock.py generates random heart rate values which can be helpful in testing out different production scenarios without the need for wearing the sensor.

## Authors and Acknowledgment

**Group Members:**
- Tuomas Laine
- Arnab Chakraborty
- Hajiba Legrara

**Official Instructor:**
- Mikhail Kolesnikov

**Other Advisors:**
- Tuojian Lyu
- Udayanto Dwi Atmojo

## License
© Copyright 2023 [Aalto University]

