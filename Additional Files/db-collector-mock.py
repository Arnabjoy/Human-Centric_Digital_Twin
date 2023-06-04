import paho.mqtt.client as mqtt
from pymongo import MongoClient
import datetime
import threading
from statistics import mean
import random

mongoClient = MongoClient(
    'mongodb+srv://sems:sems@cluster0.bu3s7.mongodb.net/sensor-database?retryWrites=true&w=majority', 27017)
mongoDb = mongoClient['sensor-database']
mongoCollection = mongoDb['hrm-collection-mock']
mongoCollectionResults = mongoDb['hrm-collection-conditions-mock']

gen_hr_period = 1  # Amount of seconds between generating heart rate
# gen_hr_min = 50  # Minimum heart rate
gen_hr_min = 90  # Minimum heart rate for testing
gen_hr_max = 140  # Maximum heart rate
# gen_hr_current = 70  # Current value of heart rate
gen_hr_current = 91  # Current value of heart rate

hr_period = 30  # Amount of heart rate values and seconds between checking condition
list_hr = []  # List of the last hrm values
current_state = "None"  # Current laborer condition

# Program algorithm
# 1 Connect to MongoDB
# 2 Generate data each second and send it to MongoDB
# 3 Grab data from MongoDB and analyze it periodically
# 4 Send that analyzed message to MQTT Broker under mqtt/sensor/hrm topic

# define MQTT Broker address and topic to be subscribed
broker_address = "192.168.1.105"
broker_port = 1883
topic_to_subscribe1 = "mqtt/sensor/hrm/decision"
topic_to_subscribe2 = "mqtt/sensor/hrm/hrmvalue"
topic_to_subscribe3 = "mqtt/sensor/hrm"
topic_to_subscribe4 = "mqtt/sensor/status"
topic_to_subscribe5 = "mqtt/human"  # Asking Human for confirmation
# topic_to_subscribe12 = "mqtt/human/music"  # Human music
# Creating a MQTT client instance
client = mqtt.Client()

# set the username and password for the MQTT broker
client.username_pw_set("Afof2023", "Afof2023")

# connect to the MQTT broker
client.connect(broker_address, broker_port)

# subscribe to the topic
client.subscribe(topic_to_subscribe1)
client.subscribe(topic_to_subscribe2)
client.subscribe(topic_to_subscribe3)
client.subscribe(topic_to_subscribe4)


# client.subscribe(topic_to_subscribe12)


# client.subscribe(topic_to_subscribe5)


def generate_hr():
    threading.Timer(gen_hr_period, generate_hr).start()  # Running the method in a loop

    # Generating new value
    global gen_hr_current
    gen_new_hr_diff = random.randrange(-1, 2)
    if (gen_hr_current + gen_new_hr_diff >= gen_hr_min and gen_hr_current + gen_new_hr_diff <= gen_hr_max):
        gen_hr_current = gen_hr_current + gen_new_hr_diff

    # Posting new value to MongoDB
    print("New generated value =", str(gen_hr_current))
    sensor_status = "connected"  # for testing purpose
    # sensor_status2 = "disconnected"  # for testing purpose
    sensor_status_msg = "{}".format(sensor_status)
    client.publish(topic_to_subscribe4, sensor_status_msg)  # subscribe4
    client.publish(topic_to_subscribe3, gen_hr_current)  # subscribe3
    mongoPost = {"timestamp": datetime.datetime.now(),
                 "payload": str(gen_hr_current)}
    mongoCollection.insert_one(mongoPost)


# Calculation of the mean value of the heart rate for the last "hr_period" documents from MongoDB
def analyze_hr():
    threading.Timer(hr_period, analyze_hr).start()
    # Calculate mean value for recent heart rate values
    list_hr.clear()
    for obj in mongoCollection.find().sort("_id", -1).limit(hr_period):
        list_hr.append(int(obj["payload"]))

    hrm_value = mean(list_hr)
    hrm_int = int(hrm_value)  # converting to integer for opca server
    print("Average is:")
    print(hrm_int)

    state = calculate_state(hrm_int)  # Check condition
    message = "{}".format(state)
    print(message)
    # boolean = "False"
    # message2 = "{}".format(boolean)
    # human_notification = "Pick Up the piece from EnAS?"
    # message404 = "{}".format(human_notification)
    # client.publish(topic_to_subscribe5, message404)
    # publish a message to the topic
    client.publish(topic_to_subscribe1, message)
    client.publish(topic_to_subscribe2, hrm_int)
    # client.publish(topic_to_subscribe12, message2)


# Check current worker condition
def calculate_state(hr):
    global current_state

    if (0 < hr <= 70):
        current_state = "Relaxed"
    elif (hr > 70 and hr <= 90):
        current_state = "Optimal"
    elif (hr > 90):
        current_state = "Stressed"

    print("Current state is:")
    # print(current_state)
    return current_state


generate_hr()
analyze_hr()

# loop forever to receive incoming messages
client.loop_forever()
