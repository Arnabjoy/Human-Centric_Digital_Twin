import paho.mqtt.client as mqtt
import keyboard
from pymongo import MongoClient
import datetime

broker_address = "192.168.1.105"
broker_port = 1883
topic_to_subscribe = "mqtt/sensor/hrm"
mongoClient = MongoClient(
    'mongodb+srv://sems:sems@cluster0.bu3s7.mongodb.net/sensor-database?retryWrites=true&w=majority', 27017)
mongoDb = mongoClient['sensor-database']
mongoCollection = mongoDb['hrm-collection']


# define callback
def on_message(client, userdata, message):
    print("received message =", str(message.payload.decode("utf-8")))

    mongoPost = {"timestamp": datetime.datetime.now(),
                 "payload": str(message.payload.decode("utf-8"))}
    # mongoPosts = mongoDb.posts
    mongoCollection.insert_one(mongoPost)


# Initialize connection with MQTT broker and subscribe to hrm topic


client = mqtt.Client("Data-Collector")
client.username_pw_set("Afof2023", "Afof2023")
print("connecting to broker.... ", broker_address)
client.connect(broker_address, broker_port)  # connect
print("connected to broker ", broker_address)
client.loop_start()  # start loop to process received messages
client.on_message = on_message
print("subscribing.... ")
client.subscribe(topic_to_subscribe)  # subscribe
# Keyboard process termintaion
# Required to disconnect safely from the mongoDB
while True:
    try:
        if keyboard.is_pressed('q'):  # if key 'q' is pressed
            client.disconnect()  # disconnect
            client.loop_stop()  # stop loop
            break
    except:
        break
