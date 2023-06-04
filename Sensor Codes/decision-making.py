from pymongo import MongoClient
import threading
import paho.mqtt.client as mqtt
from statistics import mean

mongoClient = MongoClient(
    'mongodb+srv://sems:sems@cluster0.bu3s7.mongodb.net/sensor-database?retryWrites=true&w=majority', 27017)
mongoDb = mongoClient['sensor-database']
mongoCollection = mongoDb['hrm-collection']

hr_period = 30  # Amount of heart rate values and seconds between checking condition (change to 60s for bpm)
list_hr = []  # List of the last hrm values
current_hr = 0  # Current value of the heart rate
current_state = "None"  # Current worker condition

broker_address = "192.168.1.105"
broker_port = 1883
topic_to_subscribe1 = "mqtt/sensor/hrm/decision"
topic_to_subscribe2 = "mqtt/sensor/hrm/hrmvalue"
# Creating a MQTT client instance
client = mqtt.Client("Decision-maker")

# set the username and password for the MQTT broker
client.username_pw_set("Afof2023", "Afof2023")

# connect to the MQTT broker
client.connect(broker_address, broker_port)
print("subscribing.... ")

# subscribe to the topic
client.subscribe(topic_to_subscribe1)
client.subscribe(topic_to_subscribe2)


# Calculation of the mean value of the heart rate for the last "hr_period" documents from MongoDB
def analyze_hr():
    threading.Timer(hr_period, analyze_hr).start()
    list_hr.clear()
    for obj in mongoCollection.find().sort("_id", -1).limit(hr_period):
        list_hr.append(int(obj["payload"]))

    hrm_value = mean(list_hr)
    # print("Average is:")
    # print(hrm_value)
    hrm_int = int(hrm_value)  # converting to integer for opca server
    state = calculate_state(hrm_int)  # Check condition
    message = "{}".format(state)
    # print(message)
    # publish a message to the topic
    client.publish(topic_to_subscribe1, message)
    client.publish(topic_to_subscribe2, hrm_int)


# Calculate current laborer condition
def calculate_state(hr):
    global current_state

    if (hr <= 70):
        current_state = "Relaxed"
    elif (hr > 70 and hr <= 90):
        current_state = "Optimal"
    elif (hr > 90):
        current_state = "Stressed"

    # print("Current state is:")
    # print(current_state)
    return current_state


# Initialization of the algorithm
analyze_hr()
# loop forever to receive incoming messages
client.loop_forever()
