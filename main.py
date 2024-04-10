import PySimpleGUI as sg
import pyautogui
import time
import threading
import keyboard
import json

cycle = 0

def move_cursor(interval, unit):
    multiplier = 1
    if unit == 'Minutes':
        multiplier = 60
    elif unit == 'Hours':
        multiplier = 3600
    while mouse_afk_active:
        pyautogui.move(1, 0, duration=0.1)
        time.sleep(interval * multiplier)
        pyautogui.move(-1, 0, duration=0.1)
        time.sleep(interval * multiplier)

def press_key(interval, key):
    while keyboard_afk_active:
        keyboard.press(key)
        keyboard.release(key)
        time.sleep(interval)

def toggle_afk():
    global afk_active
    if afk_active:
        stop_afk()
    else:
        start_afk()

def start_afk():
    global afk_active, mouse_afk_active, keyboard_afk_active
    interval_text = window['-INTERVAL-'].get()
    if not is_number(interval_text):
        # Change the highlight color of the text input border to red if it's not a number
        window['-INTERVAL-'].Widget.configure(highlightcolor='red', highlightbackground='red', insertbackground='white', highlightthickness=1)
        return  # Don't proceed with the action if the interval is not a valid number

    else:
        # Restore the text input border color if it's a valid number
        window['-INTERVAL-'].Widget.configure(highlightcolor="White", highlightbackground='#373737', insertbackground='white', highlightthickness=1)
    interval = int(interval_text)
    unit = values['-UNIT-']
    if values['-MOUSE_AFK-']:
        mouse_afk_active = True
        thread = threading.Thread(target=move_cursor, args=(interval, unit))
        thread.daemon = True
        thread.start()
    if values['-KEYBOARD_AFK-'] and assigned_key is not None:
        keyboard_afk_active = True
        thread = threading.Thread(target=press_key, args=(interval, assigned_key))
        thread.daemon = True
        thread.start()
    afk_active = True
    window['-START_STOP-'].update('Stop')

def stop_afk():
    global afk_active, mouse_afk_active, keyboard_afk_active
    afk_active = False
    mouse_afk_active = False
    keyboard_afk_active = False
    window['-START_STOP-'].update('Start')

def define_key():
    layout = [
        [sg.Text('Press any key')],
    ]
    window = sg.Window('Define Key', layout, finalize=True)
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        window.close()
        return None
    window.close()
    return event

def is_number(text):
    try:
        float(text)
        return True
    except ValueError:
        return False

def display_help():
    sg.popup("Instructions:",
             "1. Interval for cursor movement: Specify how much time should pass before the cursor moves automatically.",
             "2. Mouse AFK: Activate automatic cursor movement.",
             "3. Keyboard AFK: Activate automatic pressing of the specified key.",
             "4. Key to press: Show the assigned key for the Keyboard AFK function.",
             "5. Start/Stop: Start or stop the Mouse AFK and/or Keyboard AFK function.",
             "* The cursor will move 1 pixel to the left and 1 pixel to the right.", )

# Add custom theme
sg.theme_add_new('CustomDarkTheme', {'BACKGROUND': '#373737',
                                    'TEXT': '#FFFFFF',
                                    'INPUT': '#474747',
                                    'TEXT_INPUT': '#FFFFFF',
                                    'SCROLL': '#515151',
                                    'BUTTON': ('white', '#474747'),
                                    'PROGRESS': ('#01826B', '#D0D0D0'),
                                    'BORDER': 0, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0})

# Apply custom theme
sg.theme("CustomDarkTheme")

# Load the assigned key from a file if available
try:
    with open('assigned_key.txt', 'r') as file:
        assigned_key = file.read().strip()
except FileNotFoundError:
    assigned_key = 'alt'

mouse_afk_active = False
keyboard_afk_active = False
afk_active = False

# Define font for the entire window
font_style = ('Arial', 13)

layout = [
    [sg.Text('Interval for cursor movement:', size=(30, 1), justification='center', font=font_style)],
    [sg.InputText('5', key='-INTERVAL-', size=(10, 1), justification='center'), 
     sg.InputOptionMenu(['Seconds', 'Minutes', 'Hours'], default_value='Minutes', key='-UNIT-', size=(10, 1))],
    [sg.Checkbox('Mouse AFK', default=True, key='-MOUSE_AFK-'), 
     sg.Checkbox('Keyboard AFK', default=False, key='-KEYBOARD_AFK-')],
    [sg.Text('Key to press:', size=(30, 1), justification='center', font=font_style)],
    [sg.Text(assigned_key.upper(), key='-ASSIGNED_KEY-', size=(10, 1), justification='center')],
    [sg.Button('Help', size=(10, 1), font=font_style),
     sg.Button('Start', size=(10, 1), key='-START_STOP-', font=(font_style[0], font_style[1], 'bold')),
     sg.Button('Define Key', size=(10, 1), font=font_style)]
]

window = sg.Window('Anti AFK', layout, element_justification='c', icon="ico.ico", size=(340, 183))



while True:

    event, values = window.read(timeout=cycle * 100000)
    try:
        window['-INTERVAL-'].Widget.configure(highlightcolor="White", highlightbackground='White', insertbackground='white', highlightthickness=1)
    except:
        pass

    if event == sg.WINDOW_CLOSED:
        break
    if event == 'Define Key':
        window.hide()
        sg.popup_quick_message('Press any key', auto_close_duration=3)
        assigned_key = keyboard.read_event().name
        window['-ASSIGNED_KEY-'].update(assigned_key.upper())
        window.un_hide()
        # Save the assigned key to a file
        with open('assigned_key.txt', 'w') as file:
            file.write(assigned_key)
    if event == '-START_STOP-':
        toggle_afk()
    elif event == 'Help':
        display_help()

    cycle = cycle + 1

    if cycle > 100000:
        cycle = 100000


window.close()
