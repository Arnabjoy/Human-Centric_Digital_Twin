import threading
import time
import datetime as dt
import types
import socket
import subprocess
import easygui
import pymsgbox
import pyautogui
import pygame
import os
import psutil
import random
import tkinter as tk
from PIL import Image, ImageDraw
import matplotlib
import paho.mqtt.client as mqtt
import keyboard
from pymongo import MongoClient
import datetime
from matplotlib import ticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import hashlib
import requests
from requests.auth import HTTPBasicAuth
from time import sleep
from functions import *
from mir_client import APIClient
from subprocess import call

# Parameters for mir_client
base_url = "http://192.168.1.125/api/v2.0.0"
username = "Distributor"  # admin
password_digest = hashlib.sha256(
    "distributor".encode("latin1")).hexdigest()  # admin

mir = APIClient(base_url, username, password_digest)

# Mqtt init
broker_address = "192.168.1.105"
broker_port = 1883
# subscribed topics
topic_to_subscribe = "mqtt/sensor/hrm"
topic_to_subscribe2 = "mqtt/sensor/hrm/decision"
topic_to_subscribe3 = "mqtt/sensor/hrm/hrmvalue"  # Average value
topic_to_subscribe4 = "mqtt/sensor/status"  # sensor status
topic_to_subscribe5 = "mqtt/human"  # Notifying Human
topic_human_conf = "mqtt/human/conf"  # Asking Human for confirmation
topic_schedule = "mqtt/schedule"
topic_to_subscribe6 = "mqtt/mir/mission1"  # mir mission 1.1
topic_to_subscribe6_1 = "mqtt/mir/mission12"  # mir mission 1.2
topic_to_subscribe7 = "mqtt/mir/mission21"  # mir mission 2.1
topic_to_subscribe8 = "mqtt/mir/mission22"  # mir mission 2.2
topic_to_subscribe9 = "mqtt/mir/mission23"  # mir mission 2.3
topic_to_subscribe10 = "mqtt/EnAS"  # Piece ready
topic_to_subscribe11 = "mqtt/state/EnAs/status"  # EnAs ready for production
topic_to_subscribe12 = "mqtt/human/music"  # Human music
topic_pid = "mqtt/pid"  # getting the pid(process id) of the main control script

# Initialize connection with MQTT broker and subscribe to hrm topic
client = mqtt.Client("Control_Graph")
client.username_pw_set("Afof2023", "Afof2023")
try:
    client.connect(broker_address, broker_port)
    client.loop_start()  # start loop to process received messages
    client.on_message = on_message
    # subscribe
    client.subscribe(topic_to_subscribe)
    client.subscribe(topic_to_subscribe2)
    client.subscribe(topic_to_subscribe3)
    client.subscribe(topic_to_subscribe4)
    client.subscribe(topic_to_subscribe5)
    client.subscribe(topic_human_conf)
    client.subscribe(topic_schedule)
    client.subscribe(topic_to_subscribe6)
    client.subscribe(topic_to_subscribe6_1)
    client.subscribe(topic_to_subscribe7)
    client.subscribe(topic_to_subscribe8)
    client.subscribe(topic_to_subscribe9)
    client.subscribe(topic_to_subscribe10)
    client.subscribe(topic_to_subscribe11)
    client.subscribe(topic_to_subscribe12)
    client.subscribe(topic_pid)
    print("Connected to Mqtt Broker!")
except:
    print("Could not connect to Mqtt Broker!")

# def generate_heart_rate(gen_hr_period, gen_hr_min, gen_hr_max):
#     gen_hr_current = gen_hr_min
#     while True:
#         # Generating new value
#         gen_new_hr_diff = random.randrange(-1, 2)
#         if (gen_hr_current + gen_new_hr_diff >= gen_hr_min and gen_hr_current + gen_new_hr_diff <= gen_hr_max):
#             gen_hr_current += gen_new_hr_diff
#         yield gen_hr_current
#         time.sleep(0.1)


# Global variables
hrm_values = 0
hrm_avg = 0
decision = "No Message"
sensor_status = "No status"
ssid_connect = None
schedule = "No pieces"
human_notification = "No message"
human_confirmation = "No message"
mission_status_1 = "No state"
mission_status_12 = "No state"
mission_status_21 = "No state"
mission_status_22 = "No state"
mission_status_23 = "No state"
piece_ready = "Not ready"
EnAs_state = "idle"
Simulation_Music = ""
pid = ""

flag_esp32 = 0

# publish initial human confirmation message as no message
message404 = "{}".format(human_confirmation)
client.publish(topic_human_conf, message404)


def get_connected_ssid(my_canvas1, my_oval17, text17_1):
    global ssid_connect
    while True:
        try:
            output = subprocess.check_output(['netsh', 'wlan', 'show', 'interface'])
            output_str = output.decode('utf-8')
            ssid = output_str.split("SSID                   : ")[1].split("\n")[0].strip()
            ssid_connect = ssid
            my_canvas1.itemconfig(my_oval17, fill="green")
            my_canvas1.itemconfigure(text17_1, text=ssid_connect)
        except:
            ssid_connect = None
            not_connected = "None"
            my_canvas1.itemconfig(my_oval17, fill="red")
            my_canvas1.itemconfigure(text17_1, text=str(not_connected))
        time.sleep(0.1)


def is_mqtt_broker_running(host, port, my_canvas1, my_oval6, my_oval1, my_oval16, text_16_1):
    while True:
        try:
            # create a socket object
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # set timeout to 1 second
            s.settimeout(1)
            # attempt to connect to the host and port
            s.connect((host, port))
            # close the socket
            s.close()
            my_canvas1.itemconfig(my_oval6, fill="green")
            my_canvas1.itemconfig(my_oval1, fill="green")
            my_canvas1.itemconfig(my_oval16, fill="green")
            my_canvas1.itemconfigure(text_16_1, text=str(host))
        except:
            my_canvas1.itemconfig(my_oval6, fill="red")
            my_canvas1.itemconfig(my_oval1, fill="red")
            my_canvas1.itemconfig(my_oval16, fill="red")
        time.sleep(0.1)


# Reference: https://mntolia.com/mqtt-python-with-paho-mqtt-client/

def on_message_from_hrm(client, userdata, message):
    global hrm_values
    hrm_values = int(message.payload.decode("utf-8"))


def on_message_from_decision(client, userdata, message):
    global decision
    decision = str(message.payload.decode("utf-8"))


def on_message_from_hrm_avg(client, userdata, message):
    global hrm_avg
    hrm_avg = int(message.payload.decode("utf-8"))


def on_message_from_sensor_status(client, userdata, message):
    global sensor_status
    sensor_status = str(message.payload.decode("utf-8"))


def on_message_from_human_or_mir(client, userdata, message):
    global human_notification
    human_notification = str(message.payload.decode("utf-8"))


def on_message_from_schedule(client, userdata, message):
    global schedule
    schedule = str(message.payload.decode("utf-8"))


def on_message_from_mission1(client, userdata, message):
    global mission_status_1
    mission_status_1 = str(message.payload.decode("utf-8"))


def on_message_from_mission12(client, userdata, message):
    global mission_status_12
    mission_status_12 = str(message.payload.decode("utf-8"))


def on_message_from_mission21(client, userdata, message):
    global mission_status_21
    mission_status_21 = str(message.payload.decode("utf-8"))


def on_message_from_mission22(client, userdata, message):
    global mission_status_22
    mission_status_22 = str(message.payload.decode("utf-8"))


def on_message_from_mission23(client, userdata, message):
    global mission_status_23
    mission_status_23 = str(message.payload.decode("utf-8"))


def on_message_from_EnAs_piece(client, userdata, message):
    global piece_ready
    piece_ready = str(message.payload.decode("utf-8"))


def on_message_from_EnAs(client, userdata, message):
    global EnAs_state
    EnAs_state = str(message.payload.decode("utf-8"))


def on_message_from_control_script(client, userdata, message):
    global pid
    pid = str(message.payload.decode("utf-8"))


def on_message_from_simulation(client, userdata, message):
    global Simulation_Music
    Simulation_Music = str(message.payload.decode("utf-8"))


def fetch_hrm_values():
    client.message_callback_add(topic_to_subscribe, on_message_from_hrm)
    client.message_callback_add(topic_to_subscribe2, on_message_from_decision)
    client.message_callback_add(topic_to_subscribe3, on_message_from_hrm_avg)
    client.message_callback_add(topic_to_subscribe4, on_message_from_sensor_status)
    client.message_callback_add(topic_to_subscribe5, on_message_from_human_or_mir)
    client.message_callback_add(topic_schedule, on_message_from_schedule)
    client.message_callback_add(topic_to_subscribe6, on_message_from_mission1)
    client.message_callback_add(topic_to_subscribe6_1, on_message_from_mission12)
    client.message_callback_add(topic_to_subscribe7, on_message_from_mission21)
    client.message_callback_add(topic_to_subscribe8, on_message_from_mission22)
    client.message_callback_add(topic_to_subscribe9, on_message_from_mission23)
    client.message_callback_add(topic_to_subscribe10, on_message_from_EnAs_piece)
    client.message_callback_add(topic_to_subscribe11, on_message_from_EnAs)
    client.message_callback_add(topic_to_subscribe12, on_message_from_simulation)
    client.message_callback_add(topic_pid, on_message_from_control_script)

    # while True:
    #     time.sleep(0.1)


def is_esp32_running(my_canvas1, my_oval5):
    global flag_esp32
    # Reference: https://stackoverflow.com/questions/29952676/simple-ping-function-returns-access-denied-option-c-requires-administrative-p
    ip = "192.168.1.184"  # static ip of esp32
    while True:
        try:
            cmd = "ping -n 1 " + ip
            status = subprocess.getstatusoutput(cmd)
            # print(status)
            # if status[0] == 0: print("ok")
            # response = os.system('ping -n 1 ' + ip)  # if response == 0: print("ok")
            if "Destination host unreachable." in status[1] or status[0] == 1:
                my_canvas1.itemconfig(my_oval5, fill="red")
                # print("Esp32 " + str(ip) + " is DOWN !")
            else:
                my_canvas1.itemconfig(my_oval5, fill="green")
                # print("Esp32 " + str(ip) + " is UP !")
        except:
            my_canvas1.itemconfig(my_oval5, fill="red")
            flag_esp32 = 1
        time.sleep(1)


if flag_esp32 == 1:
    print("Check if hard coded static ip of esp32 was able to be assigned or not!")


def timeout_callback():
    global human_confirmation
    human_confirmation = "no"
    no_button_pos = pyautogui.locateOnScreen('no_button.png')
    if no_button_pos is not None:
        pyautogui.click(no_button_pos)
    # pyautogui.click(x=1058, y=599)  # Automatically clicks the message box when no response
    pymsgbox.alert("Timeout reached! Mir will proceed instead", "Title")
    message2 = "{}".format(human_confirmation)
    client.publish(topic_human_conf, message2)


def timeout_callback2():
    global human_confirmation
    human_confirmation = "no"
    no_button_pos = pyautogui.locateOnScreen('no_ididnt.png')
    if no_button_pos is not None:
        pyautogui.click(no_button_pos)
    # pyautogui.click(x=1058, y=599)  # Automatically clicks the message box when no response
    pymsgbox.alert("You did not respond! Mir will proceed instead", "Title")
    message3 = "{}".format(human_confirmation)
    client.publish(topic_human_conf, message3)


def asking_human(my_canvas3, my_oval11):
    global human_confirmation
    my_canvas3.itemconfig(my_oval11, fill="green")
    # Start the timer thread
    timer_thread = threading.Timer(10.0, timeout_callback)
    timer_thread.start()

    # Show the prompt
    response = easygui.buttonbox(msg='Do you want to pick up the piece?', title='Human Worker Confirmation',
                                 choices=['Yes', 'No'])

    # Stop the timer thread
    timer_thread.cancel()

    # Handle the user's response
    if response == 'Yes':
        human_confirmation = "yes"
        message1 = "{}".format(human_confirmation)
        client.publish(topic_human_conf, message1)
        timer_thread2 = threading.Timer(10000, timeout_callback2)
        timer_thread2.start()
        response2 = easygui.buttonbox(msg='Did you pick up the piece?', title='Human Worker Confirmation',
                                      choices=['Yes, I did', 'No, I did not'])
        timer_thread2.cancel()
        if response2 == 'Yes, I did':
            human_confirmation = "picked up"
            message4 = "{}".format(human_confirmation)
            client.publish(topic_human_conf, message4)
        else:
            human_confirmation = "no"
            message5 = "{}".format(human_confirmation)
            client.publish(topic_human_conf, message5)
    else:
        human_confirmation = "no"
        message6 = "{}".format(human_confirmation)
        client.publish(topic_human_conf, message6)


def update_indicator_color(my_canvas3, Indicator):
    my_canvas3.itemconfigure(Indicator, fill='white')
    my_canvas3.after(100, lambda: my_canvas3.itemconfigure(Indicator, fill='red'))
    my_canvas3.after(280, lambda: my_canvas3.itemconfigure(Indicator, fill='white'))
    my_canvas3.after(380, lambda: my_canvas3.itemconfigure(Indicator, fill='red'))


def check_status(my_canvas1, my_canvas3, my_oval1, my_oval2, my_oval3, my_oval4, my_oval6, my_oval7, my_oval11,
                 my_oval72,
                 my_oval14,
                 my_oval16,
                 text_16_1,
                 my_oval17,
                 text17_1, my_oval8, my_oval9, my_oval10, my_oval12, my_oval13, my_oval15, text15_1, my_oval11_2,
                 text_11_3):
    global decision, hrm_values, hrm_avg, human_notification, mission_status_1, mission_status_12, mission_status_21, mission_status_22, mission_status_23, piece_ready, EnAs_state, schedule
    while True:
        if decision == "Stressed":
            my_canvas1.itemconfig(my_oval14, fill="green")
        else:
            my_canvas1.itemconfig(my_oval14, fill="red")
        # if is_mqtt_broker_running("192.168.1.105", 1883):
        #     static_ip = "192.168.1.105"
        #     my_canvas1.itemconfig(my_oval6, fill="green")
        #     my_canvas1.itemconfig(my_oval1, fill="green")
        #     my_canvas1.itemconfig(my_oval16, fill="green")
        #     my_canvas1.itemconfigure(text_16_1, text=str(static_ip))
        # else:
        #     my_canvas1.itemconfig(my_oval6, fill="red")
        #     my_canvas1.itemconfig(my_oval1, fill="red")
        #     my_canvas1.itemconfig(my_oval16, fill="red")

        if sensor_status == "connected":
            my_canvas1.itemconfig(my_oval2, fill="green")
            """If esp32 suddenly disconnects, then it shows the last status of the sensor.
               To avoid that one way could be to also check if esp32 is live or not through pinging."""
        else:
            my_canvas1.itemconfig(my_oval2, fill="red")
            hrm_values = 0
            hrm_avg = 0
            decision = "No Message"
        # if ssid_connect is not None:
        #     my_canvas1.itemconfig(my_oval17, fill="green")
        #     my_canvas1.itemconfigure(text17_1, text=ssid_connect)
        # else:
        #     not_connected = "None"
        #     my_canvas1.itemconfig(my_oval17, fill="red")
        #     my_canvas1.itemconfigure(text17_1, text=str(not_connected))
        if human_notification == "Pick Up the piece from EnAS?":
            asking_human(my_canvas3, my_oval11)
        else:
            my_canvas3.itemconfig(my_oval11, fill="red")

        # if schedule == 'grb':  # displaying the pieces that being manufactured currently (grb,rbg,bgb,gbb,bbg,bgr,grg,rgg) # Pieces g=piece 1, r = piece 2, b=piece 3
        #     my_canvas3.itemconfig(my_oval11_2, fill="green")
        #     my_canvas3.itemconfigure(text_11_3, text="Piece-01,Piece-02,Piece-03")
        # elif schedule == 'rbg':
        #     my_canvas3.itemconfig(my_oval11_2, fill="green")
        #     my_canvas3.itemconfigure(text_11_3, text="Piece-02,Piece-03,Piece-01")
        # elif schedule == 'bgb':
        #     my_canvas3.itemconfig(my_oval11_2, fill="green")
        #     my_canvas3.itemconfigure(text_11_3, text="Piece-03,Piece-01,Piece-03")
        # elif schedule == 'gbb':
        #     my_canvas3.itemconfig(my_oval11_2, fill="green")
        #     my_canvas3.itemconfigure(text_11_3, text="Piece-01,Piece-03,Piece-03")
        # elif schedule == 'bbg':
        #     my_canvas3.itemconfig(my_oval11_2, fill="green")
        #     my_canvas3.itemconfigure(text_11_3, text="Piece-03,Piece-03,Piece-01")
        # elif schedule == 'bgr':
        #     my_canvas3.itemconfig(my_oval11_2, fill="green")
        #     my_canvas3.itemconfigure(text_11_3, text="Piece-03,Piece-01,Piece-02")
        # elif schedule == 'grg':
        #     my_canvas3.itemconfig(my_oval11_2, fill="green")
        #     my_canvas3.itemconfigure(text_11_3, text="Piece-01,Piece-02,Piece-01")
        # elif schedule == 'rgg':
        #     my_canvas3.itemconfig(my_oval11_2, fill="green")
        #     my_canvas3.itemconfigure(text_11_3, text="Piece-02,Piece-01,Piece-01")
        # else:
        #     my_canvas3.itemconfig(my_oval11_2, fill="red")
        def set_canvas_item_red():
            global mission_status_12
            my_canvas1.itemconfig(my_oval72, fill="red")
            mission_status_12 = "No state"

        if mission_status_1 == "start":
            my_canvas1.itemconfig(my_oval7, fill="green")
        elif mission_status_1 == "pending":
            my_canvas1.itemconfig(my_oval7, fill="red")
        else:
            my_canvas1.itemconfig(my_oval7, fill="red")

        if mission_status_12 == "start":
            my_canvas1.itemconfig(my_oval72, fill="green")
            my_canvas1.after(40000, set_canvas_item_red)
        elif mission_status_12 == "pending":
            my_canvas1.itemconfig(my_oval72, fill="red")
        else:
            my_canvas1.itemconfig(my_oval72, fill="red")

        if mission_status_21 == "start":
            my_canvas1.itemconfig(my_oval8, fill="green")
        elif mission_status_21 == "pending":
            my_canvas1.itemconfig(my_oval8, fill="red")
        else:
            my_canvas1.itemconfig(my_oval8, fill="red")

        if mission_status_22 == "start":
            my_canvas1.itemconfig(my_oval9, fill="green")
        elif mission_status_22 == "pending":
            my_canvas1.itemconfig(my_oval9, fill="red")
        else:
            my_canvas1.itemconfig(my_oval9, fill="red")

        if mission_status_23 == "start":
            my_canvas1.itemconfig(my_oval12, fill="green")
        elif mission_status_23 == "pending":
            my_canvas1.itemconfig(my_oval12, fill="red")
        else:
            my_canvas1.itemconfig(my_oval12, fill="red")

        if human_notification == "The Robot has been sent to pick up the piece":
            my_canvas1.itemconfig(my_oval10, fill="green")
        else:
            my_canvas1.itemconfig(my_oval10, fill="red")

        if piece_ready == "ProductionReady":
            my_canvas1.itemconfig(my_oval13, fill="green")
        else:
            my_canvas1.itemconfig(my_oval13, fill="red")
        if EnAs_state == "start":
            my_canvas1.itemconfig(my_oval3, fill="green")
        else:
            my_canvas1.itemconfig(my_oval3, fill="red")
        # Scheduling the pieces that being manufactured currently
        piece_mappings = {
            'g': 'Piece-01',
            'r': 'Piece-02',
            'b': 'Piece-03'
        }
        # Check if the schedule string is valid or not
        if all(piece in piece_mappings for piece in schedule):
            my_canvas3.itemconfig(my_oval11_2, fill="green")
            pieces = [piece_mappings[piece] for piece in schedule]
            my_canvas3.itemconfigure(text_11_3, text=",".join(pieces))
        else:
            my_canvas3.itemconfig(my_oval11_2, fill="red")

        status = mir.get_status()
        battery_charge = status['battery_percentage']
        mir_status = status['state_text']
        if mir_status == 'Ready' or mir_status == 'Executing':
            my_canvas1.itemconfig(my_oval4, fill="green")
        else:
            my_canvas1.itemconfig(my_oval4, fill="red")
        charge_text = int(battery_charge)
        my_canvas1.itemconfigure(text15_1, text=charge_text)
        if charge_text > 70:
            my_canvas1.itemconfig(my_oval15, fill="green")
        elif 40 < charge_text < 70:
            my_canvas1.itemconfig(my_oval15, fill="light blue")
        else:
            my_canvas1.itemconfig(my_oval15, fill="yellow")
            my_canvas1.itemconfigure(text15_1, text=charge_text)

        # time.sleep(0.1)


def graphing(fig, my_canvas3):
    global hrm_values, decision, hrm_avg
    i = 0
    x, y = [], []
    ax = fig.add_subplot(111)
    ax.set_title("Heart-rate Monitor", fontsize=12)
    ax.set_ylabel("Heart-rate", fontsize=9)

    def format_time(x1, pos):
        time_str = str(dt.timedelta(seconds=int(x1)))
        return time_str[2:]

    formatter = ticker.FuncFormatter(format_time)
    ax.xaxis.set_major_formatter(formatter)
    my_canvas3.create_text(66, 60, text='Current Heart rate:', font=('Arial', 10, 'bold'), anchor='center')
    heart_rate_text = my_canvas3.create_text(135, 60, text='0', font=('Arial', 10, 'bold'), anchor='w')

    my_canvas3.create_text(74, 80, text='Average Heart rate:   ', font=('Arial', 10, 'bold'), anchor='center')
    avg_text = my_canvas3.create_text(135, 80, text='0 bpm', font=('Arial', 10, 'bold'), anchor='w')

    my_canvas3.create_text(66, 100, text='Current Condition:', font=('Arial', 10, 'bold'), anchor='center')
    condition_text = my_canvas3.create_text(135, 100, text='', font=('Arial', 10, 'bold'), anchor='w')
    # create the Indicator
    Indicator = my_canvas3.create_oval(160, 54, 170, 64, fill="white")

    while True:
        x.append(i)
        heart_rate = hrm_values
        decisions = decision
        average_hrm = hrm_avg
        if heart_rate != 0:
            y.append(heart_rate)
            update_indicator_color(my_canvas3, Indicator)
            if 0 < heart_rate <= 70:
                my_canvas3.itemconfigure(heart_rate_text, fill='orange')
            elif 70 < heart_rate <= 90:
                my_canvas3.itemconfigure(heart_rate_text, fill='green')
            else:
                my_canvas3.itemconfigure(heart_rate_text, fill='red')
        else:
            y.append(0)  # Append 0 value when heart_rate is 0
            Indicator = my_canvas3.create_oval(160, 54, 170, 64, fill="white")
        if decision != "No Message":
            if decision == "Relaxed":
                my_canvas3.itemconfigure(condition_text, fill='orange')
            elif decision == "Optimal":
                my_canvas3.itemconfigure(condition_text, fill='green')
            else:
                my_canvas3.itemconfigure(condition_text, fill='red')

        if average_hrm != 0:
            if average_hrm <= 70:
                my_canvas3.itemconfigure(avg_text, fill='orange')
            elif 70 < average_hrm <= 90:
                my_canvas3.itemconfigure(avg_text, fill='green')
            else:
                my_canvas3.itemconfigure(avg_text, fill='red')

        left_limit = max(0, i - 50)
        right_limit = i + 50
        ax.set_xlim([left_limit, right_limit])
        i += 1
        ax.autoscale(axis='y')
        # y_min = min(y)
        # y_max = max(y)
        # y_range = y_max - y_min
        # y_buffer = 5  # add a buffer of 5 to the y-axis limits
        #
        # if y_range < y_buffer:
        #     y_mid = (y_min + y_max) / 2
        #     y_min = y_mid - y_buffer / 2
        #     y_max = y_mid + y_buffer / 2
        #
        # ax.set_ylim([y_min, y_max])
        ax.plot(x, y, linestyle='-', linewidth=1, color='red')
        ax.set_facecolor('#f2f2f2')
        ax.grid(True)
        fig.canvas.draw()
        my_canvas3.itemconfigure(heart_rate_text, text=heart_rate)
        my_canvas3.itemconfigure(avg_text, text=str(average_hrm) + " bpm")
        my_canvas3.itemconfigure(condition_text, text=decisions)
        time.sleep(0.18)


def play_music(my_canvas1, my_oval18):
    global decision, Simulation_Music
    # creating different channels for sounds for practical application and simulation separately
    pygame.init()
    pygame.mixer.init()
    channel1 = pygame.mixer.Channel(0)  # Create channel 0
    channel2 = pygame.mixer.Channel(1)  # Create channel 1

    while True:
        # playing music for simulation
        if Simulation_Music == "True" and not channel2.get_busy():
            # print("Loading music...")
            sound1 = pygame.mixer.Sound("music.mp3")  # Load the sound for channel 0
            # print("Music loaded!")
            channel1.play(sound1)  # Play the sound on channel 0
            while channel1.get_busy():
                my_canvas1.itemconfig(my_oval18, fill="green")
                pygame.time.Clock().tick(10)
                if Simulation_Music == "False":
                    channel1.stop()
                    my_canvas1.itemconfig(my_oval18, fill="red")
                    break
        # playing music for real-life production scenario
        elif decision == "Stressed" and not channel1.get_busy():
            # print("Loading music...")
            sound2 = pygame.mixer.Sound("music.mp3")  # Load the sound for channel 1
            # print("Music loaded!")
            channel2.play(sound2)  # Play the sound on channel 1
            while channel2.get_busy():
                my_canvas1.itemconfig(my_oval18, fill="green")
                pygame.time.Clock().tick(10)
                if decision != "Stressed":
                    channel2.stop()
                    my_canvas1.itemconfig(my_oval18, fill="red")
                    break
        else:
            my_canvas1.itemconfig(my_oval18, fill="red")


# def play_music_sim(my_canvas1, my_oval18):
#     global Simulation_Music
#     while True:
#         if Simulation_Music == "True" and not channel1.get_busy():
#             # print("Loading music...")
#             sound2 = pygame.mixer.Sound("music.mp3")  # Load the sound for channel 1
#             # print("Music loaded!")
#             channel2.play(sound2)  # Play the sound on channel 1
#             while channel2.get_busy():
#                 my_canvas1.itemconfig(my_oval18, fill="green")
#                 pygame.time.Clock().tick(10)
#                 if Simulation_Music == "False":
#                     break
#         elif Simulation_Music == "False":
#             channel2.stop()
#             my_canvas1.itemconfig(my_oval18, fill="red")
#         else:
#             my_canvas1.itemconfig(my_oval18, fill="red")


# Mir Charging
def mir_charge():
    mission_guid = "1002fa3b-4cbe-11ea-8c90-0001299877fe"
    mir.post_mission_queue(mission_guid)


def execute_mir_charge():
    try:
        t = threading.Thread(target=mir_charge)
        t.daemon = True
        t.start()
    except:
        print("Could not send Mir to charge!")
        return


# Start Missions

def mission_1():
    mission_guid = "17482572-e044-11ed-b8dc-0001299877fe"
    mir.post_mission_queue(mission_guid)


def mission_12():
    mission_guid = "bc9d6ce6-f4a9-11ed-9c68-0001299877fe"
    mir.post_mission_queue(mission_guid)


def mission_2_1():
    mission_guid = "15a4617a-e99f-11ed-b354-0001299877fe"
    mir.post_mission_queue(mission_guid)


def mission_2_2():
    mission_guid = "5218325c-e9b0-11ed-b354-0001299877fe"
    mir.post_mission_queue(mission_guid)


def mission_2_3():
    mission_guid = "de080016-ef52-11ed-8f21-0001299877fe"
    mir.post_mission_queue(mission_guid)


def execute_mission_1():
    try:
        t = threading.Thread(target=mission_1)
        t.daemon = True
        t.start()
    except:
        print("Could not post the mission!")
        return


def execute_mission_12():
    try:
        t = threading.Thread(target=mission_12)
        t.daemon = True
        t.start()
    except:
        print("Could not post the mission!")
        return


def execute_mission_2_1():
    try:
        t = threading.Thread(target=mission_2_1)
        t.daemon = True
        t.start()
    except:
        print("Could not post the mission!")
        return


def execute_mission_2_2():
    try:
        t = threading.Thread(target=mission_2_2)
        t.daemon = True
        t.start()
    except:
        print("Could not post the mission!")
        return


def execute_mission_2_3():
    try:
        t = threading.Thread(target=mission_2_3)
        t.daemon = True
        t.start()
    except:
        print("Could not post the mission!")
        return


# Stop Missions
def stop_mission_1():
    que = mir.get_mission_queue()
    if que[-1]["state"] == "Executing":
        mission_que_id = que[-1]["id"]
        mir.delete_mission_queue_id(mission_que_id)
    else:
        print("Could not find the posted mission queue!")


def execute_stop_mission_1():
    try:
        t = threading.Thread(target=stop_mission_1)
        t.daemon = True
        t.start()
    except:
        print("Could not stop the mission!")
        return


def stop_mission_12():
    que = mir.get_mission_queue()
    if que[-1]["state"] == "Executing":
        mission_que_id = que[-1]["id"]
        mir.delete_mission_queue_id(mission_que_id)
    else:
        print("Could not find the posted mission queue!")


def execute_stop_mission_12():
    try:
        t = threading.Thread(target=stop_mission_12)
        t.daemon = True
        t.start()
    except:
        print("Could not stop the mission!")
        return


def stop_mission_2_1():
    que = mir.get_mission_queue()
    if que[-1]["state"] == "Executing":
        mission_que_id = que[-1]["id"]
        mir.delete_mission_queue_id(mission_que_id)
    else:
        print("Could not find the posted mission queue!")


def execute_stop_mission_2_1():
    try:
        t = threading.Thread(target=stop_mission_2_1)
        t.daemon = True
        t.start()
    except:
        print("Could not stop the mission!")
        return


def stop_mission_2_2():
    que = mir.get_mission_queue()
    if que[-1]["state"] == "Executing":
        mission_que_id = que[-1]["id"]
        mir.delete_mission_queue_id(mission_que_id)
    else:
        print("Could not find the posted mission queue!")


def execute_stop_mission_2_2():
    try:
        t = threading.Thread(target=stop_mission_2_2)
        t.daemon = True
        t.start()
    except:
        print("Could not stop the mission!")
        return


def stop_mission_2_3():
    que = mir.get_mission_queue()
    if que[-1]["state"] == "Executing":
        mission_que_id = que[-1]["id"]
        mir.delete_mission_queue_id(mission_que_id)
    else:
        print("Could not find the posted mission queue!")


def execute_stop_mission_2_3():
    try:
        t = threading.Thread(target=stop_mission_2_3)
        t.daemon = True
        t.start()
    except:
        print("Could not stop the mission!")
        return


# def get_mir_charge_status(my_canvas1, my_oval7):
#     global mission_charge
#     mission1_id = "2691"
#     while True:
#         try:
#             que = mir.get_mission_queue_id(mission1_id)
#             if que:
#                 mission_charge = que["state"]
#                 if mission_charge == "Executing":
#                     my_canvas1.itemconfig(my_oval7, fill="green")
#                 else:
#                     my_canvas1.itemconfig(my_oval7, fill="red")
#             else:
#                 my_canvas1.itemconfig(my_oval7, fill="red")
#         except:
#             my_canvas1.itemconfig(my_oval7, fill="red")
#             mission_charge = "No state"
#         time.sleep(1)


# def get_mir_mission1_status(my_canvas1, my_oval8):
#     global mission_status_1
#     while True:
#         # try:
#         #     mission2_id = "2688"
#         #     que = mir.get_mission_queue_id(mission2_id)
#         #     for mission_id in que:
#         #         if mission_id["id"] == mission2_id:
#         #             mission_status_1 = mission_id["state"]
#         #             if mission_status_1 == "Executing":
#         #                 my_canvas1.itemconfig(my_oval8, fill="green")
#         #             else:
#         #                 my_canvas1.itemconfig(my_oval8, fill="red")
#         #         else:
#         #             my_canvas1.itemconfig(my_oval8, fill="red")
#         #             mission_status_1 = "No state"
#         # except:
#         #     my_canvas1.itemconfig(my_oval8, fill="red")
#         #     mission_status_1 = "No state"
#
#         time.sleep(0.1)


# def get_mir_mission21_status(my_canvas1, my_oval9):
#     global mission_status_21
#     while True:
#         try:
#             que = mir.get_mission_queue()
#             mission3_id = "15a4617a-e99f-11ed-b354-0001299877fe"
#             for mission_id in que:
#                 if mission_id["id"] == mission3_id:
#                     mission_status_21 = mission_id["state"]
#                     if mission_status_21 == "Executing":
#                         my_canvas1.itemconfig(my_oval9, fill="green")
#                     else:
#                         my_canvas1.itemconfig(my_oval9, fill="red")
#                 else:
#                     my_canvas1.itemconfig(my_oval9, fill="red")
#                     mission_status_21 = "No state"
#         except:
#             my_canvas1.itemconfig(my_oval9, fill="red")
#             mission_status_21 = "No state"
#         time.sleep(0.1)


# def get_mir_mission22_status(my_canvas1, my_oval10):
#     global mission_status_22
#     while True:
#         try:
#             que = mir.get_mission_queue()
#             mission4_id = "5218325c-e9b0-11ed-b354-0001299877fe"
#             for mission_id in que:
#                 if mission_id["id"] == mission4_id:
#                     mission_status_22 = mission_id["state"]
#                     if mission_status_22 == "Executing":
#                         my_canvas1.itemconfig(my_oval10, fill="green")
#                     else:
#                         my_canvas1.itemconfig(my_oval10, fill="red")
#                 else:
#                     my_canvas1.itemconfig(my_oval10, fill="red")
#                     mission_status_22 = "No state"
#         except:
#             my_canvas1.itemconfig(my_oval10, fill="red")
#             mission_status_22 = "No state"
#         time.sleep(0.1)


# Emergency stop(Abort all missions in the que)
def emergency_stop():
    mir.abort_all_missions()


def execute_emergency_stop():
    try:
        t = threading.Thread(target=emergency_stop)
        t.daemon = True
        t.start()
    except:
        print("Could not abort the missions!!")
        return


# a global variable to hold the status of production process
process_running = False


def start_production():
    global process_running
    try:
        call(["python", "main_v2.py"])
        process_running = True
        print("Production started!")
    except:
        print("Could not start the production script!")


def stop_production():
    global process_running, pid
    try:
        if process_running:
            call(["taskkill", "/f", "/t", "/pid",
                  pid])
            process_running = False
            print("Production stopped!")
    except:
        print("Could not stop the production script!")


def start_production_thread():
    t = threading.Thread(target=start_production)
    t.daemon = True
    t.start()


def stop_production_thread():
    t = threading.Thread(target=stop_production)
    t.daemon = True
    t.start()
