# Human Centric Production Operator Digital Twin



## Project Work - CRAS13




## Folders

# GUI and Process Control Script
GUI and Process Control Script folder contains Main_Control.py and main_interface_functions.py which are required for running the GUI. Please also make sure mir_client.py, music.mp3 and the pictures are in the same folder while executing the GUI scripts. mir_client.py makes use of the MIR API, music.mp3 is the relaxing music that will be played by the GUI when the human operator is stressed and the images are for pyautogui which is used to automatically click no in the prompt when the human operator takes too much time or forgets to press yes. In addition to that, the folder also contains process control script which controls the production process and schedules the production scenarios.

# Sensor Codes
Sensor Codes folder contains all the necessary scripts required to connect to the sensor and retrieve the heart-rate values in real-time.  ESP32_BLE_HRM_MQTT.ino code should be uploaded in the esp32 using the Arduino IDE and db-collector.py is used for retrieving the heart-rate values and post in the MongoDB(sensor database). Then, decision-making.py is used for getting those sensor values from the sensor database and make a decision on human worker condition.

# Additional Files
Additional Files folder contains heart-rate generator mock file(db-collector-mock.py) for testing purposes. db-collector-mock.py generates random heart rate values which can be helpful in testing out different production scenarios without the need for wearing the sensor.

## Authors and acknowledgment
Group Members:
(1) Tuomas Laine 
(2) Arnab Chakraborty
(3) Hajiba Legrara 

Official Instructor: 
Mikhail Kolesnikov

Other advisors: 

(1) Tuojian Lyu 
(2) Udayanto Dwi Atmojo 

## License
© Copyright 2023 [Aalto University]

