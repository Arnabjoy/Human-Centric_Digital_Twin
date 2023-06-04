import hashlib
import tkinter as tk
import matplotlib
import threading
import time
import psutil
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from time import sleep
from functions import *
from main_interface_functions import *
from PIL import Image, ImageTk
from mir_client import APIClient

# Reference : https://www.youtube.com/watch?v=5qOnzF7RsNA&ab_channel=PythonSimplified
# Reference : https://www.youtube.com/watch?v=0V-6pu1Gyp8&ab_channel=Dr.SachinSharma
# Reference : https://stackoverflow.com/questions/63233656/how-to-create-indicator-lights-danger-warning-safe-using-python-gui
# Reference : https://stackoverflow.com/questions/13212300/how-to-reconfigure-tkinter-canvas-items

root = tk.Tk()
root.title("Main Control Interface")
root.eval("tk::PlaceWindow . center")
# Disable window resizing for convenience
root.resizable(width=False, height=False)

print(
    "Please keep your display resolution 1920x1080 and size of text,apps to 100% for the gui to not look distorted from display settings!")

frame1 = tk.Frame(root, width=1100, height=600)
frame1.grid(row=0, column=0)

label1 = tk.Label(root, text="Aalto factory of Future", font=("Times", 18, "bold italic"))

# add the label to the top of the frame using grid method
# label1.grid(row=0, column=0, padx=10, pady=10, sticky="n")
label1.place(relx=0.5, rely=0, anchor="n")

# Draw a real-time plot for heart-rate monitor
fig = Figure()
# gen_hr_period = 1  # Amount of seconds between generating heart rate
# gen_hr_min = 50  # Minimum heart rate
# gen_hr_max = 140  # Maximum heart rate
# gen_hr_current = 70  # Current value of heart rate
#
# # Create a global variable to hold the generator object
# gen_hr = generate_heart_rate(gen_hr_period, gen_hr_min, gen_hr_max)

# start the heart rate generation function in a separate thread
# t = threading.Thread(target=generate_heart_rate, args=(gen_hr_period, gen_hr_min, gen_hr_max))
# t.daemon = True
# t.start()

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().place(x=230, y=50, width=570, height=220)
canvas.draw()
my_canvas1 = tk.Canvas(root, width=700, height=490)
my_canvas2 = tk.Canvas(root, width=400, height=490)
my_canvas3 = tk.Canvas(root, width=500, height=220)
my_canvas4 = tk.Canvas(root, width=115, height=290)
my_canvas1.place(x=40, y=300)
my_canvas2.place(x=850, y=300)
my_canvas3.place(x=800, y=50)
my_canvas4.place(x=0, y=0)

# Fetch the hrm values in a separate thread
t = threading.Thread(target=fetch_hrm_values, args=())
t.daemon = True
t.start()

# start the graphing function in a separate thread
t2 = threading.Thread(target=graphing, args=(fig, my_canvas3))
t2.daemon = True
t2.start()

# creating a rectangle around my_canvas1
my_canvas1.create_rectangle(10, 20, 700, 240, outline='black', fill='#f2f2f2', width=2)
my_canvas1.create_rectangle(10, 40, 180, 240, outline='black', fill='#f2f2f2', width=2)  # for using it as divider
my_canvas1.create_rectangle(430, 40, 180, 240, outline='black', fill='#f2f2f2', width=2)  # for using it as divider
my_canvas1.create_rectangle(430, 40, 700, 240, outline='black', fill='#f2f2f2', width=2)  # for using it as divider
# Load image
image = Image.open("output-onlinepngtools.png")
image = image.resize((150, 150), resample=Image.LANCZOS)  # Resize image
photo = ImageTk.PhotoImage(image)

my_canvas4.create_image(5, 5, anchor="nw", image=photo)
# creating a rectangle around my_canvas1
my_canvas1.create_text(320, 30, text='Status Menu', font=('Arial', 12, 'bold'), anchor='center')

# creating a rectangle around my_canvas2
my_canvas2.create_rectangle(5, 20, 240, 290, outline='black', fill='#f2f2f2', width=2)
# my_canvas2.create_rectangle(5, 40, 230, 240, outline='black', fill='#f2f2f2', width=2)  # for using it as divider

my_canvas2.create_text(120, 30, text='Manual Commands', font=('Arial', 12, 'bold'), anchor='center')

my_oval1 = my_canvas1.create_oval(50, 50, 60, 60, fill="red")
my_oval2 = my_canvas1.create_oval(50, 80, 60, 90, fill="red")
my_oval3 = my_canvas1.create_oval(50, 110, 60, 120, fill="red")
my_oval4 = my_canvas1.create_oval(50, 140, 60, 150, fill="red")
my_oval5 = my_canvas1.create_oval(50, 170, 60, 180, fill="red")
my_oval6 = my_canvas1.create_oval(50, 200, 60, 210, fill="red")

my_oval7 = my_canvas1.create_oval(225, 50, 235, 60, fill="red")  # mir mission 1.1
my_oval72 = my_canvas1.create_oval(225, 80, 235, 90, fill="red")  # mir mission 1.2
my_oval8 = my_canvas1.create_oval(225, 110, 235, 120, fill="red")  # mir mission 2.1
my_oval9 = my_canvas1.create_oval(225, 140, 235, 150, fill="red")  # mir mission 2.2
my_oval10 = my_canvas1.create_oval(225, 200, 235, 210, fill="red")  # mir proceeds on no response
my_oval11 = my_canvas3.create_oval(8, 120, 18, 130, fill="red")  # asking human
my_oval11_2 = my_canvas3.create_oval(8, 137, 18, 147, fill="red")  # scheduling pieces
my_oval12 = my_canvas1.create_oval(225, 170, 235, 180, fill="red")  # mir mission 2.3

my_oval13 = my_canvas1.create_oval(450, 50, 460, 60, fill="red")
my_oval14 = my_canvas1.create_oval(450, 80, 460, 90, fill="red")
my_oval15 = my_canvas1.create_oval(450, 110, 460, 120, fill="red")
my_oval16 = my_canvas1.create_oval(450, 140, 460, 150, fill="red")
my_oval17 = my_canvas1.create_oval(450, 170, 460, 180, fill="red")
my_oval18 = my_canvas1.create_oval(450, 200, 460, 210, fill="red")

text1 = my_canvas1.create_text(100, 55, text="MQTT Broker")
text2 = my_canvas1.create_text(115, 85, text="Sensor Connected")
text3 = my_canvas1.create_text(80, 115, text="EnAs")
text4 = my_canvas1.create_text(76, 145, text="Mir")
text5 = my_canvas1.create_text(83, 175, text="Esp32")
text6 = my_canvas1.create_text(83, 205, text="Raspi")

text7 = my_canvas1.create_text(280, 55, text="Mir Mission-1.1")  # Storage2 to EnAs
text72 = my_canvas1.create_text(280, 85, text="Mir Mission-1.2")
text8 = my_canvas1.create_text(280, 115, text="Mir Mission-2.1")  # Charging dock to EnAs to Storage1
text9 = my_canvas1.create_text(280, 145, text="Mir Mission-2.2")  # Charging dock to EnAs to Human Workstation
text10 = my_canvas1.create_text(280, 175, text="Mir Mission-2.3")  # Charging dock to EnAs to Robot Workstation
text11 = my_canvas3.create_text(62, 125, text="Asking Human")  # Asking Human if he wants to pick up the piece or not
text11_2 = my_canvas3.create_text(69, 142,
                                  text="Scheduled pieces:")
text_11_3 = my_canvas3.create_text(190, 142, text="")
text12 = my_canvas1.create_text(315, 205, text="Mir proceeds on no response")  # if not, Mir proceeds

text13 = my_canvas1.create_text(495, 55, text="Piece Ready")
text14 = my_canvas1.create_text(508, 85, text="Human Stressed")
text15 = my_canvas1.create_text(505, 115,
                                text="Mir Charge(%):")
text15_1 = my_canvas1.create_text(555, 115,
                                  text="")
text16 = my_canvas1.create_text(490, 145, text="Broker IP: ")
text_16_1 = my_canvas1.create_text(550, 145, text="")
text17 = my_canvas1.create_text(505, 175, text="Connected Wifi:")
text17_1 = my_canvas1.create_text(570, 175, text="")
text18 = my_canvas1.create_text(500, 205, text="Playing Music")

# start the check status function in a separate thread
t3 = threading.Thread(target=check_status,
                      args=(
                          my_canvas1, my_canvas3, my_oval1, my_oval2, my_oval3, my_oval4, my_oval6, my_oval7, my_oval11,
                          my_oval72,
                          my_oval14,
                          my_oval16,
                          text_16_1,
                          my_oval17,
                          text17_1, my_oval8, my_oval9, my_oval10, my_oval12, my_oval13, my_oval15, text15_1,
                          my_oval11_2, text_11_3))
t3.daemon = True
t3.start()

t4 = threading.Thread(target=play_music, args=(my_canvas1, my_oval18))
t4.daemon = True
t4.start()

# t4_sim = threading.Thread(target=play_music_sim, args=(my_canvas1, my_oval18))
# t4_sim.daemon = True
# t4_sim.start()

# thread for checking Wi-Fi status
t_wifi = threading.Thread(target=get_connected_ssid, args=(my_canvas1, my_oval17, text17_1))
t_wifi.daemon = True
t_wifi.start()

# thread for checking broker status
t_broker = threading.Thread(target=is_mqtt_broker_running,
                            args=(broker_address, broker_port, my_canvas1, my_oval6, my_oval1, my_oval16, text_16_1))
t_broker.daemon = True
t_broker.start()

# # thread for checking mir charging status
# t_mir_charge = threading.Thread(target=get_mir_charge_status,
#                                 args=(my_canvas1, my_oval7))
# t_mir_charge.daemon = True
# t_mir_charge.start()

# # thread for checking mir mission1 status
# t_mir_mission1 = threading.Thread(target=get_mir_mission1_status,
#                                   args=(my_canvas1, my_oval8))
# t_mir_mission1.daemon = True
# t_mir_mission1.start()

# # thread for checking mir mission21 status
# t_mir_mission21 = threading.Thread(target=get_mir_mission21_status,
#                                    args=(my_canvas1, my_oval9))
# t_mir_mission21.daemon = True
# t_mir_mission21.start()

# # thread for checking mir mission22 status
# t_mir_mission22 = threading.Thread(target=get_mir_mission22_status,
#                                    args=(my_canvas1, my_oval10))
# t_mir_mission22.daemon = True
# t_mir_mission22.start()

# thread for checking esp32 status
t_esp32 = threading.Thread(target=is_esp32_running,
                           args=(my_canvas1, my_oval5))
t_esp32.daemon = True
t_esp32.start()

button = tk.Button(root, text="Charge Mir", borderwidth=2, relief="solid", command=lambda: execute_mir_charge(),
                   width=20, bg="#ADD8E6", font=('Arial', 10, 'bold'))
button_window = my_canvas2.create_window(30, 50, anchor="nw", window=button)

# # Graphing
# start_graph_button = tk.Button(root, text="Start", borderwidth=2, relief="solid", command=lambda: start_graphing(),
#                                width=5)
#
# start_graph_window = my_canvas3.create_window(135, 120, anchor="nw", window=start_graph_button)
#
# stop_graph_button = tk.Button(root, text="Stop", borderwidth=2, relief="solid", command=lambda: stop_graphing(),
#                               width=5)
# stop_graph_window = my_canvas3.create_window(135, 140, anchor="nw", window=stop_graph_button)

# Mir Mission-1.1(Manual Commands)
Mir_text1 = my_canvas2.create_text(10, 90, anchor="nw", text="Mir Mission-1.1:", font=("Arial", 10))
start_button1 = tk.Button(root, text="Start", borderwidth=1, relief="solid", command=lambda: execute_mission_1(),
                          width=5)
start_window1 = my_canvas2.create_window(105, 85, anchor="nw", window=start_button1)
stop_button1 = tk.Button(root, text="Stop", borderwidth=1, relief="solid", command=lambda: execute_stop_mission_1(),
                         width=5)
stop_window1 = my_canvas2.create_window(155, 85, anchor="nw", window=stop_button1)

# Mir Mission-1.2(Manual Commands)
Mir_text12 = my_canvas2.create_text(10, 125, anchor="nw", text="Mir Mission-1.2:", font=("Arial", 10))
start_button12 = tk.Button(root, text="Start", borderwidth=1, relief="solid", command=lambda: execute_mission_12(),
                           width=5)
start_window12 = my_canvas2.create_window(105, 120, anchor="nw", window=start_button12)
stop_button12 = tk.Button(root, text="Stop", borderwidth=1, relief="solid", command=lambda: execute_stop_mission_12(),
                          width=5)
stop_window12 = my_canvas2.create_window(155, 120, anchor="nw", window=stop_button12)

# Mir Mission-2.1(Manual Commands)
Mir_text2 = my_canvas2.create_text(10, 160, anchor="nw", text="Mir Mission-2.1:", font=("Arial", 10))
start_button2 = tk.Button(root, text="Start", borderwidth=1, relief="solid", command=lambda: execute_mission_2_1(),
                          width=5)
start_window2 = my_canvas2.create_window(105, 155, anchor="nw", window=start_button2)
stop_button2 = tk.Button(root, text="Stop", borderwidth=1, relief="solid", command=lambda: execute_stop_mission_2_1(),
                         width=5)
stop_window2 = my_canvas2.create_window(155, 155, anchor="nw", window=stop_button2)

# Mir Mission-2.2(Manual Commands)
Mir_text3 = my_canvas2.create_text(10, 195, anchor="nw", text="Mir Mission-2.2:", font=("Arial", 10))
start_button3 = tk.Button(root, text="Start", borderwidth=1, relief="solid", command=lambda: execute_mission_2_2(),
                          width=5)
start_window3 = my_canvas2.create_window(105, 195, anchor="nw", window=start_button3)
stop_button3 = tk.Button(root, text="Stop", borderwidth=1, relief="solid", command=lambda: execute_stop_mission_2_2(),
                         width=5)
stop_window3 = my_canvas2.create_window(155, 195, anchor="nw", window=stop_button3)

# Mir Mission-2.3(Manual Commands)
Mir_text4 = my_canvas2.create_text(10, 230, anchor="nw", text="Mir Mission-2.3:", font=("Arial", 10))
start_button4 = tk.Button(root, text="Start", borderwidth=1, relief="solid", command=lambda: execute_mission_2_3(),
                          width=5)
start_window4 = my_canvas2.create_window(105, 230, anchor="nw", window=start_button4)
stop_button4 = tk.Button(root, text="Stop", borderwidth=1, relief="solid", command=lambda: execute_stop_mission_2_3(),
                         width=5)
stop_window4 = my_canvas2.create_window(155, 230, anchor="nw", window=stop_button4)

# Emergency stop(Terminate all missions in the que)
button4_emer = tk.Button(root, text="Emergency Stop(Mir)", borderwidth=2, relief="solid",
                         command=lambda: execute_emergency_stop(),
                         width=23, bg='red', font=('Arial', 8, 'bold'))
button_window4_emer = my_canvas2.create_window(30, 265, anchor="nw", window=button4_emer)

# Production start and stop buttons
start_button5 = tk.Button(root, text="Start Production", borderwidth=1, relief="solid",
                          command=lambda: start_production_thread(),
                          width=15)
start_window5 = my_canvas4.create_window(50, 150, anchor="nw", window=start_button5)

stop_button5 = tk.Button(root, text="Stop Production", borderwidth=1, relief="solid",
                         command=lambda: stop_production_thread(),
                         width=15)
stop_window5 = my_canvas4.create_window(50, 180, anchor="nw", window=stop_button5)

label_var = tk.StringVar()  # Set the string variable for Label widget
my_label = tk.Label(root, textvariable=label_var)  # Set the Label widget

# run application
root.mainloop()
