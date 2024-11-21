import pyautogui
import time
import keyboard
import threading
import tkinter as tk
from tkinter import *
from tkinter import ttk
import pickle
from pynput import mouse
import numpy as np
import concurrent.futures

paused = False
running = False
displaying_mouse_position = False
mouse_position_thread = None
click_count = 0
mouse_listener = None

# Function to load settings from file
def load_settings():
    try:
        with open("settings.pkl", "rb") as f:
            settings = pickle.load(f)
            entry_x_start.insert(0, settings.get("x_start", ""))
            entry_y_start.insert(0, settings.get("y_start", ""))
            entry_width.insert(0, settings.get("width", ""))
            entry_height.insert(0, settings.get("height", ""))
            width_step_scale.set(settings.get("width_step", 1))
            height_step_scale.set(settings.get("height_step", 1))
            width_step_label.config(text=str(settings.get("width_step", 1)))
            height_step_label.config(text=str(settings.get("height_step", 1)))
    except FileNotFoundError:
        pass

# Function to save settings to file
def save_settings():
    settings = {
        "x_start": entry_x_start.get(),
        "y_start": entry_y_start.get(),
        "width": entry_width.get(),
        "height": entry_height.get(),
        "width_step": width_step_scale.get(),
        "height_step": height_step_scale.get()
    }
    with open("settings.pkl", "wb") as f:
        pickle.dump(settings, f)

def toggle_pause():
    global paused
    paused = not paused
    if paused:
        pause_button.config(text="Resume")
    else:
        pause_button.config(text="Pause")
    update_status()

def start_script():
    global running
    running = True
    update_status()
    x_start = int(entry_x_start.get())
    y_start = int(entry_y_start.get())
    width = int(entry_width.get())
    height = int(entry_height.get())
    width_step = int(width_step_scale.get())
    height_step = int(height_step_scale.get())

def detect_color_region(pic_np):
    green_mask = np.logical_and(pic_np[:, :, 1] >= 180, pic_np[:, :, 1] <= 188)
    red_mask = np.logical_and(pic_np[:, :, 0] >= 50, pic_np[:, :, 0] <= 58)
    blue_mask = np.logical_and(pic_np[:, :, 2] >= 110, pic_np[:, :, 2] <= 118)
    combined_mask = np.logical_and(green_mask, np.logical_and(red_mask, blue_mask))
    return np.any(combined_mask)

def script():
    global running
    while running:
        if not paused:
            pic = pyautogui.screenshot(region=(x_start, y_start, width, height))
            pic_np = np.array(pic)
            if detect_color_region(pic_np):
                keyboard.press('e')
                time.sleep(0.01)
                keyboard.release('e')
                time.sleep(0.05)
        else:
            time.sleep(0.1)
    update_status()


    threading.Thread(target=script).start()

def stop_script():
    global running
    running = False
    update_status()
    save_settings()
    root.quit()

def toggle_display_mouse_position():
    global displaying_mouse_position, mouse_position_thread, mouse_listener
    if displaying_mouse_position:
        displaying_mouse_position = False
        mouse_position_button.config(text="Show Position")
        if mouse_position_thread:
            mouse_position_thread.do_run = False
        if mouse_listener:
            mouse_listener.stop()
            mouse_listener = None
    else:
        displaying_mouse_position = True
        mouse_position_button.config(text="Hide Position")
        mouse_position_thread = threading.Thread(target=display_mouse_position)
        mouse_position_thread.start()
        mouse_listener = mouse.Listener(on_click=on_mouse_click)
        mouse_listener.start()

def display_mouse_position():
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        x, y = pyautogui.position()
        mouse_position_label.config(text=f"X: {x}, Y: {y}")
        time.sleep(0.1)

def on_mouse_click(x, y, button, pressed):
    global click_count
    if displaying_mouse_position and button == mouse.Button.right and pressed:
        if click_count == 0:
            entry_x_start.delete(0, END)
            entry_x_start.insert(0, str(x))
            entry_y_start.delete(0, END)
            entry_y_start.insert(0, str(y))
            click_count += 1
        elif click_count == 1:
            x_start = int(entry_x_start.get())
            y_start = int(entry_y_start.get())
            width = x - x_start
            height = y - y_start
            entry_width.delete(0, END)
            entry_width.insert(0, str(width))
            entry_height.delete(0, END)
            entry_height.insert(0, str(height))
            click_count = 0

def update_status():
    if running:
        status = "Running" if not paused else "Paused"
    else:
        status = "Stopped"
    status_label.config(text=f"Status: {status}")

def update_width_step_label(val):
    width_step_label.config(text=str(int(float(val))))

def update_height_step_label(val):
    height_step_label.config(text=str(int(float(val))))

def on_closing():
    stop_script()
    root.destroy()

# Tkinter GUI setup
root = tk.Tk()
root.title("Fishing Automation")
root.geometry("400x300")
root.attributes('-topmost', 1)  # Keep the window on top
# root.iconbitmap('Fish.ico')  # Set your icon here

# Create main frame
main_frame = ttk.Frame(root, padding="10 10 10 10")
main_frame.grid(row=0, column=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Add widgets to the main frame
ttk.Label(main_frame, text="X Start:").grid(row=0, column=0, sticky=W, pady=5)
entry_x_start = ttk.Entry(main_frame, width=10)
entry_x_start.grid(row=0, column=1, pady=5)

ttk.Label(main_frame, text="Y Start:").grid(row=1, column=0, sticky=W, pady=5)
entry_y_start = ttk.Entry(main_frame, width=10)
entry_y_start.grid(row=1, column=1, pady=5)

ttk.Label(main_frame, text="Width:").grid(row=2, column=0, sticky=W, pady=5)
entry_width = ttk.Entry(main_frame, width=10)
entry_width.grid(row=2, column=1, pady=5)

ttk.Label(main_frame, text="Height:").grid(row=3, column=0, sticky=W, pady=5)
entry_height = ttk.Entry(main_frame, width=10)
entry_height.grid(row=3, column=1, pady=5)

ttk.Label(main_frame, text="Width Step:").grid(row=4, column=0, sticky=W, pady=5)
width_step_scale = ttk.Scale(main_frame, from_=1, to=10, orient=HORIZONTAL, command=update_width_step_label)
width_step_scale.grid(row=4, column=1, pady=5)
width_step_label = ttk.Label(main_frame, text="5")
width_step_label.grid(row=4, column=2, sticky=W, pady=5)

ttk.Label(main_frame, text="Height Step:").grid(row=5, column=0, sticky=W, pady=5)
height_step_scale = ttk.Scale(main_frame, from_=1, to=10, orient=HORIZONTAL, command=update_height_step_label)
height_step_scale.grid(row=5, column=1, pady=5)
height_step_label = ttk.Label(main_frame, text="5")
height_step_label.grid(row=5, column=2, sticky=W, pady=5)

start_button = ttk.Button(main_frame, text="Start", command=start_script)
start_button.grid(row=6, column=0, pady=5)

pause_button = ttk.Button(main_frame, text="Pause", command=toggle_pause)
pause_button.grid(row=6, column=1, pady=5)

mouse_position_button = ttk.Button(main_frame, text="Show Position", command=toggle_display_mouse_position)
mouse_position_button.grid(row=6, column=2, pady=5)

close_button = ttk.Button(main_frame, text="Close", command=stop_script)
close_button.grid(row=6, column=3, pady=5)

status_label = ttk.Label(main_frame, text="Status: Stopped")
status_label.grid(row=7, column=0, columnspan=2, sticky=W)

mouse_position_label = ttk.Label(main_frame, text="X: , Y: ")
mouse_position_label.grid(row=7, column=2, columnspan=2, sticky=W)

# Load settings at start
load_settings()

# Handle window close event
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start Tkinter main loop
root.mainloop()
