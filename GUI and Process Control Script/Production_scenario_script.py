import threading
import paho.mqtt.client as mqtt
from statistics import mean
import time
import hashlib
import json
import inquirer
from opcua import ua, Server
from random import randint
import sys
import os


sys.path.insert(0, "..")
from mir_client import APIClient

EnASReady = "Not"
human_conf = "Pending"
human_status = "Optimal"


def on_message(client, userdata, message):
    if message.topic == topic_EnAS_ready:
        global EnASReady
        EnASReady = str(message.payload.decode("utf-8"))
    if message.topic == topic_human_conf:
        global human_conf
        human_conf = str(message.payload.decode("utf-8"))
    if message.topic == topic_human_status:
        global human_status
        human_status = str(message.payload.decode("utf-8"))

def on_publish(client, userdata, result):
    pass

broker_address = "192.168.1.105"
broker_port = 1883

# Different topics for executing the production

topic_from_storage_to_EnAs = "mqtt/mir/mission1"
topic_from_storage_to_EnAs2 = "mqtt/mir/mission12"
topic_from_EnAS_to_storage = "mqtt/mir/mission21"
topic_from_EnAS_to_Hworkbench = "mqtt/mir/mission22"
topic_from_EnAS_to_Rworkbench = "mqtt/mir/mission23"
topic_mission_idle = "mqtt/mir/idle"
topic_schedule = "mqtt/schedule"

topic_start_EnAS = "mqtt/EnAS/start"
topic_EnAS_ready = "mqtt/EnAS"

topic_human_status = "mqtt/sensor/hrm/decision"
topic_notify_human = "mqtt/human"
topic_human_conf = "mqtt/human/conf"
topic_human_mission = "mqtt/human/mission"
topic_pid = "mqtt/pid"
topic_EnAs_state = "mqtt/state/EnAs/status"

# Creating a MQTT client instance
client = mqtt.Client("Decision-maker")

# set the username and password for the MQTT broker
client.username_pw_set("Afof2023", "Afof2023")
client.on_message = on_message
# connect to the MQTT broker
client.connect(broker_address, broker_port)
# subscribe to the topics

client.subscribe(topic_human_status)

client.subscribe(topic_from_storage_to_EnAs)
client.subscribe(topic_from_storage_to_EnAs2)
client.subscribe(topic_from_EnAS_to_storage)
client.subscribe(topic_from_EnAS_to_Rworkbench)
client.subscribe(topic_from_EnAS_to_Hworkbench)
#client.subscribe(topic_mission_idle)
#client.subscribe(topic_schedule)

client.subscribe(topic_human_conf)
client.subscribe(topic_start_EnAS)
client.subscribe(topic_EnAS_ready)
client.subscribe(topic_notify_human)
client.subscribe(topic_human_mission)
client.subscribe(topic_EnAs_state)
client.on_publish = on_publish
# getting the pid(process id) of the script
client.subscribe(topic_pid)
pid = os.getpid()
message406 = "{}".format(pid)
client.publish(topic_pid, message406)

# Connect to MiR

base_url = "http://192.168.1.125/api/v2.0.0"
username = "Distributor"
password_digest = hashlib.sha256(
    "distributor".encode("latin1")).hexdigest()

mir = APIClient(base_url, username, password_digest)

# IDs for different MiR missions
mircharge = "1002fa3b-4cbe-11ea-8c90-0001299877fe"
mirmission1 = "17482572-e044-11ed-b8dc-0001299877fe"
mirmission12 = "bc9d6ce6-f4a9-11ed-9c68-0001299877fe"
mirmission21 = "15a4617a-e99f-11ed-b354-0001299877fe"
mirmission22 = "5218325c-e9b0-11ed-b354-0001299877fe"
mirmission23 = "de080016-ef52-11ed-8f21-0001299877fe"


# Countdown used for notifying the operator
def countdown(t):
    if t > 0:
        time.sleep(1)
        t -= 1
        return t
    else:
        return t


def post_mission(mission_id):
    mir.post_mission_queue(mission_id)
    time.sleep(2)
    mir.put_status(3)


# At the start we want to pick up a piece from the storage
# and move it to the production line

# Pieces g=piece 1, r = piece 2, b=piece 3
# will be changed later according to the actual production scenario
def main():
    pieces = ['g', 'r', 'b', 'g', 'b', 'b', 'g', 'r', 'g', 'g']
    global EnASReady
    global human_conf
    global human_status
    client.publish(topic_from_storage_to_EnAs, "pending")
    client.publish(topic_from_EnAS_to_storage, "pending")
    client.publish(topic_from_EnAS_to_Hworkbench, "pending")
    client.publish(topic_from_EnAS_to_Rworkbench, "pending")

    conftest = 0
    var = 0
    try:
        for i in pieces:
            #string.join(pieces[i]+pieces[i+1]+pieces[i+2])
            string = pieces[var]+pieces[var+1]+pieces[var+2]
            var +=1
            client.publish(topic_schedule, string)
            # Production scenario for green pieces
            # Straight to storage from production line
            if conftest == 0:
                client.publish(topic_from_storage_to_EnAs, "start")
                post_mission(mirmission1)
            else:
                client.publish(topic_from_storage_to_EnAs2, "start")
            conf = 0

            while conf == 0:
                client.loop_start()
                queue = mir.get_mission_queue()
                if queue[-1]["state"] == "Done":
                    client.publish(topic_from_storage_to_EnAs, "pending")
                    client.publish(topic_from_storage_to_EnAs2, "pending")
                    #client.publish(topic_mission_idle, "start")

                    conf = 1
                    conftest = 0
                time.sleep(1)

            client.publish(topic_start_EnAS, "start")
            #client.publish(topic_EnAs_state, "start")
            conf = 0
            while conf == 0:
                #print("tests")
                #queue = mir.get_mission_queue()
                conf1 = 0
                if queue[-1]["state"] == "Done" and conf1 == 0:
                    #client.publish(topic_mission_idle, "pending")
                    conf1 = 1
                if EnASReady == "ProductionReady":

                    client.publish(topic_EnAs_state, "stop")
                    conf = 1
                time.sleep(1)
            EnASReady = "Not"
            client.publish(topic_EnAS_ready, "No")
            client.publish(topic_notify_human, "Pick Up the piece from EnAS?")
            conf3 = 0
            t = 10
            while conf3 == 0:
                t = countdown(t)
                print(t)
                if human_conf == "yes":
                    # First if to ask the operator to pick up the piece
                    # second if to confirm it has been done
                    client.publish(topic_human_mission, "start")
                    client.publish(topic_from_storage_to_EnAs, "start")
                    post_mission(mirmission12)
                    conftest = 1
                    client.publish(topic_notify_human, "The Human has accepted")
                    while human_conf != "picked up":

                        time.sleep(1)
                    client.publish(topic_human_mission, "pending")
                    conf3 = 1
                # If human declines, robot picks up the piece from EnAS
                elif t == 0 or human_conf == "no":
                    conf1 = 0
                    client.publish(topic_notify_human, "The Robot has been sent to pick up the piece")
                    if i == "g":
                        # Green goes straight to storage
                        post_mission(mirmission21)
                        client.publish(topic_from_EnAS_to_storage, "start")
                        while conf1 == 0:
                            queue = mir.get_mission_queue()
                            if queue[-1]["state"] == "Done":
                                client.publish(topic_from_EnAS_to_storage, "pending")
                                conf1 = 1
                                client.publish(topic_notify_human, "Done")
                            time.sleep(1)
                        conf3 = 1
                    elif i == 'r':
                        # red goes to WB, either human or robot works on it
                        if human_status != "Optimal":
                            post_mission(mirmission23)
                            client.publish(topic_from_EnAS_to_Rworkbench, "start")
                            while conf1 == 0:
                                queue = mir.get_mission_queue()
                                if queue[-1]["state"] == "Done":
                                    client.publish(topic_from_EnAS_to_Rworkbench, "pending")
                                    conf1 = 1
                                    client.publish(topic_notify_human, "Done")
                                time.sleep(1)
                            conf3 = 1
                        else:
                            post_mission(mirmission22)
                            client.publish(topic_from_EnAS_to_Hworkbench, "start")

                            while conf1 == 0:
                                queue = mir.get_mission_queue()
                                if queue[-1]["state"] == "Done":
                                    client.publish(topic_from_EnAS_to_Hworkbench, "pending")
                                    conf1 = 1
                                    client.publish(topic_notify_human, "Done")
                                time.sleep(1)
                            client.publish(topic_from_storage_to_EnAs, "start")
                            post_mission(mirmission12)
                            conftest = 1
                            conf3 = 1
                    elif i == 'b':
                        # black goes to WB, human has to work on it
                        post_mission(mirmission22)
                        client.publish(topic_from_EnAS_to_Hworkbench, "start")
                        while conf1 == 0:
                            queue = mir.get_mission_queue()
                            if queue[-1]["state"] == "Done":
                                client.publish(topic_from_EnAS_to_Hworkbench, "pending")
                                conf1 = 1
                                client.publish(topic_notify_human, "Done")
                            time.sleep(1)
                        conf3 = 1
                        client.publish(topic_from_storage_to_EnAs, "start")
                        post_mission(mirmission12)
                        conftest=1
            # mir.post_mission_queue(mircharge)
            client.loop_stop()


    finally:
        # post_mission(mircharge)
        # server.stop()
        pass


main()
