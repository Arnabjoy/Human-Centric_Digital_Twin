from opcua import ua, Server
from pymongo import MongoClient
from random import randint
from statistics import mean
import sys
import threading
sys.path.insert(0, "..")
import paho.mqtt.client as mqtt
import time
global_hr = 0
worker_cond = "Optimal"
human_miss = "pending"
mir_miss1 = "pending"
mir_miss21 = "pending"
mir_miss22 = "pending"
mir_miss23 = "pending"
mir_missIdle = "pending"
prod_ready = "No"

def on_message(client, userdata, message):
    if message.topic == hr_topic:
        global global_hr
        global_hr = int(message.payload)
    if message.topic == worker_topic:
        global worker_cond
        worker_cond = str(message.payload.decode("utf-8"))
    if message.topic == mission1:
        global mir_miss1
        mir_miss1 = str(message.payload.decode("utf-8"))
    if message.topic == mission21:
        global mir_miss21
        mir_miss21 = str(message.payload.decode("utf-8"))
    if message.topic == mission22:
        global mir_miss22
        mir_miss22 = str(message.payload.decode("utf-8"))
    if message.topic == mission23:
        global mir_miss23
        mir_miss23 = str(message.payload.decode("utf-8"))
    if message.topic == mission_idle:
        global mir_missIdle
        mir_missIdle = str(message.payload.decode("utf-8"))
    if message.topic == human_mission:
        global human_miss
        human_miss = str(message.payload.decode("utf-8"))
    if message.topic == Enas_ready:
        global prod_ready
        prod_ready = str(message.payload.decode("utf-8"))
    
    #print(global_hr)
    #return str(message.payload.decode("utf-8"))
                    
if __name__ == "__main__":
    
    broker_address = "192.168.1.105"
    broker_port = 1883
    hr_topic = "mqtt/sensor/hrm/hrmvalue"
    worker_topic = "mqtt/sensor/hrm/decision"
    mission1 = "mqtt/mir/mission1"
    mission21 = "mqtt/mir/mission21"
    mission22 = "mqtt/mir/mission22"
    mission23 = "mqtt/mir/mission23"
    mission_idle = "mqtt/mir/idle"
    music = "mqtt/human/music"
    
    Enas_ready = "mqtt/EnAS"
    
    human_mission = "mqtt/human/mission"
    
    client = mqtt.Client("OPC_UA_SERVER")
    
    client.username_pw_set("Afof2023", "Afof2023")
    client.on_message = on_message

    
    client.connect(broker_address, broker_port)
    print("subbing")
    client.subscribe(hr_topic)
    client.subscribe(worker_topic)
    client.subscribe(mission1)
    client.subscribe(mission21)
    client.subscribe(mission22)
    client.subscribe(mission23)
    client.subscribe(Enas_ready)
    client.subscribe(music)
    client.subscribe(mission_idle)
    client.subscribe(human_mission)

    # setup our server
    server = Server()
    server.set_endpoint("opc.tcp://192.168.1.105:4840/freeopcua/server/")

    # setup our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    idx = server.register_namespace(uri)
    name = "TestForCRAS13"
    addspace = server.register_namespace(name)
    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()

    # populating our address space
    human = objects.add_object(idx, "Human")
    enas = objects.add_object(idx, "EnAS")
    ready = enas.add_variable(idx, "Production Ready", "No")
    heartrate = human.add_variable(idx, "HeartRate", 70)
    condition = human.add_variable(idx, "Condition", "normal")
    h_miss = human.add_variable(idx, "Mission", "pending")
    h_music = human.add_variable(idx, "Play Music", False)
    

    #MiR
    mir = objects.add_object(idx, "MiR100")
    on_mission1 = mir.add_variable(idx, "Mission1", "pending")
    on_mission21 = mir.add_variable(idx, "Mission21", "pending")
    on_mission22 = mir.add_variable(idx, "Mission22", "pending")
    on_mission23 = mir.add_variable(idx, "Mission23", "pending")
    on_mission_idle = mir.add_variable(idx, "MissionIdle", "pending")
    heartrate.set_writable()    # Set MyVariable to be writable by clients
    condition.set_writable()
    h_miss.set_writable()
    h_music.set_writable()
    on_mission1.set_writable()
    on_mission21.set_writable()
    on_mission22.set_writable()
    on_mission23.set_writable()
    ready.set_writable()

    on_mission_idle.set_writable()
    # starting!
    server.start()
    #client.subscribe(hr_topic)
    
    try:
        count = 0
        while True:
            client.loop_start()
            time.sleep(1)
            client.loop_stop()
            #print(global_hr)
            heartrate.set_value(global_hr)
            condition.set_value(worker_cond)
            h_miss.set_value(human_miss)
            on_mission1.set_value(mir_miss1)
            on_mission21.set_value(mir_miss21)
            on_mission22.set_value(mir_miss22)
            on_mission23.set_value(mir_miss23)
            on_mission_idle.set_value(mir_missIdle)
            val = h_music.get_value()
            if val == True:
                ebin = 'Playing'
            else:
                ebin = 'No'
            client.publish(music, val)
            ready.set_value(prod_ready)
            
            #hr = analyze_hr()
            #print(hr)
            #heartrate.set_value(hr)
            #print(client.subscribe(hr_topic))
            #print(hr[0])
            #heartrate.set_value(hr[0])
    finally:
        #close connection, remove subscriptions, etc
        server.stop()