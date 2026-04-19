import csv
import os
import time
from pynput import mouse, keyboard

CSV_FILE = "mouse_movements.csv"

recording = False
csv_file = None
csv_writer = None


def _open_csv():
    file_exists = os.path.exists(CSV_FILE)
    f = open(CSV_FILE, "a", newline="", encoding="utf-8")
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(["pos_x", "pos_y", "click", "pkey"])
    return f, writer


def _append_row(pos_x, pos_y, is_click):
    if csv_writer is None:
        return
    pkey = time.time_ns()
    csv_writer.writerow([pos_x, pos_y, is_click, pkey])
    csv_file.flush()


def on_move(x, y):
    if recording:
        _append_row(x, y, False)


def on_click(x, y, button, pressed):
    if recording and button == mouse.Button.left and pressed:
        _append_row(x, y, True)


def on_key_press(key):
    global recording, csv_file, csv_writer
    try:
        if key.char != "k":
            return
    except AttributeError:
        return

    if not recording:
        recording = True
        csv_file, csv_writer = _open_csv()
        print("Recording started.")
    else:
        recording = False
        if csv_file:
            csv_file.flush()
            csv_file.close()
            csv_file = None
            csv_writer = None
        print("Recording stopped.")


mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_key_press)

mouse_listener.start()
keyboard_listener.start()

print("Press 'k' to start / stop recording mouse movements.")
print("Press Ctrl+C to quit.")

try:
    keyboard_listener.join()
except KeyboardInterrupt:
    recording = False
    if csv_file:
        csv_file.flush()
        csv_file.close()
    mouse_listener.stop()
    keyboard_listener.stop()
    print("Exited.")