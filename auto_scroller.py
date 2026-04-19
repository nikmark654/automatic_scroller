import sys
import os
import json
import locale
import threading
import multiprocessing
from pystray import Icon, Menu, MenuItem
from PIL import Image
from platformdirs import user_data_dir
from random import randint, uniform
from language_dict import LANG
from cursor_controls import CursorControls
from sound_utils import sound_start, sound_tick, sound_stop, sound_clock_tick


def bundled_path(relative_path):
    """Resolve path to a bundled resource (works both in dev and as .exe)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


APP_NAME = "auto scroller"
DATA_DIR = user_data_dir(APP_NAME)

cursor_checks_dict = {"use_trigger": None, "max_wait": None, "min_wait": None, "timer_limit": None}
app_status = {
    "running_clicks": False,
    "timer_limit": None,
    "minutes_remaining": None,
}
manual_stop = True

SETTINGS_FILE = os.path.join(DATA_DIR, "auto_scroller_settings.json")
_system_locale = locale.getlocale()[0]
_system_lang = _system_locale.split("_")[0] if _system_locale else "en"
_fallback_lang = _system_lang if _system_lang in LANG else "en"

if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r", encoding="utf-8") as _f:
        _settings = json.load(_f)
    active_lang = _settings.get("language", _fallback_lang)
else:
    active_lang = _fallback_lang
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as _f:
        json.dump({
            "language": active_lang,
            "max_click_timer": None,
            "min_click_timer": None,
            "timer_limit": None
        }, _f, indent=2)

active_lang = active_lang if active_lang in LANG else "en"
_stop_event = threading.Event()


def run_interface(queue, data_dir):
    """Entry point for the interface child process."""
    from as_interface import Interface

    interface = Interface(bundled_path, data_dir)

    def check_queue():
        try:
            msg = queue.get_nowait()
            if msg == "show":
                interface.show()
            elif msg == "reset":
                interface.reset()
            elif msg == "quit":
                interface.root.destroy()
                return
        except Exception:
            pass
        interface.root.after(100, check_queue)

    check_queue()
    interface.root.mainloop()


interface_process = None
queue = None


def ensure_interface_running():
    global interface_process, queue
    if interface_process is None or not interface_process.is_alive():
        queue = multiprocessing.Queue()
        interface_process = multiprocessing.Process(
            target=run_interface, args=(queue, DATA_DIR), daemon=True
        )
        interface_process.start()


def on_open_interface(icon, _):
    ensure_interface_running()
    queue.put("show")


def on_reset_settings(icon, _):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as _f:
            json.dump({
                "language": active_lang,
                "max_click_timer": None,
                "min_click_timer": None,
                "timer_limit": None,
            }, _f, indent=2)
    except OSError:
        icon.notify("Could not reset settings.", translated_variables["app_title"])
        return
    if queue is not None and interface_process is not None and interface_process.is_alive():
        queue.put("reset")


def on_quit(icon, _):
    _stop_event.set()
    if queue is not None:
        queue.put("quit")
    if interface_process is not None:
        interface_process.join(timeout=2)
    icon.stop()


try:
    image = Image.open(bundled_path("happy-face.png"))
except (FileNotFoundError, OSError):
    image = Image.new("RGB", (64, 64), color="#78613B")

translated_variables = LANG[active_lang]

def on_start_scrolling(icon, _):
    global manual_stop
    manual_stop = False
    threading.Thread(target=sound_start, daemon=True).start()
    threading.Thread(target=run_cursor_controls, args=(icon,), daemon=True).start()
    print('Started Cursor Controling!')


def on_stop_scrolling():
    global manual_stop
    manual_stop = True
    app_status["running_clicks"] = False
    print('Stoped cursor controling!')


menu = Menu(
    MenuItem(translated_variables["open_interface"], on_open_interface),
    MenuItem(translated_variables["start_scrolling"], on_start_scrolling),
    MenuItem(translated_variables["stop_scrolling"], on_stop_scrolling),
    MenuItem(translated_variables["reset_settings"], on_reset_settings),
    MenuItem(translated_variables["quit"], on_quit),
)

def settings_watcher(icon):
    global active_lang, translated_variables
    while not _stop_event.wait(0.5):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as _f:
                settings = json.load(_f)
            new_lang = settings.get("language", active_lang)
            if new_lang not in LANG:
                new_lang = "en"
        except (json.JSONDecodeError, OSError):
            continue

        if new_lang != active_lang:
            active_lang = new_lang
            translated_variables = LANG[active_lang]
            icon.menu = Menu(
                MenuItem(translated_variables["open_interface"], on_open_interface),
                MenuItem(translated_variables["start_scrolling"], None),
                MenuItem(translated_variables["stop_scrolling"], None),
                MenuItem(translated_variables["reset_settings"], on_reset_settings),
                MenuItem(translated_variables["quit"], on_quit),
            )
        
        cursor_checks_dict['timer_limit'] = settings.get('timer_limit')
        cursor_checks_dict['max_wait'] = settings.get('max_click_timer')
        cursor_checks_dict['min_wait'] = settings.get('min_click_timer')

        t = LANG[active_lang]
        click_status = t["1"][0] if app_status["running_clicks"] else t["1"][1]
        timer = str(app_status["timer_limit"]) if app_status["timer_limit"] is not None else "?"
        remaining = str(app_status["minutes_remaining"]) if app_status["minutes_remaining"] is not None else "?"
        title = t["app_title"]
        title = title.replace(": 1", f": {click_status}")
        title = title.replace(": 3 ", f": {timer} ")
        title = title.replace(": 4 ", f": {remaining} ")
        icon.title = title


def run_cursor_controls(icon):
    
    global app_status, manual_stop
    random_bound = -1
    bound_updated = False
    iterator = 0
    timer_limit_iterator = 0

    while not _stop_event.wait(1):
        raw_limit = cursor_checks_dict.get('timer_limit')
        timer_limit = int(raw_limit)*60 if raw_limit is not None else None
        app_status['timer_limit'] = raw_limit
        if timer_limit is not None:
            app_status['minutes_remaining'] = max(0, (timer_limit - timer_limit_iterator) // 60)
        else:
            app_status['minutes_remaining'] = None
        print(app_status, "click_time: ", random_bound, "time running clicks: ", timer_limit_iterator)
        if timer_limit is None or timer_limit >= timer_limit_iterator and manual_stop != True:

            app_status["running_clicks"] = True

            if bound_updated == False:
                try:
                    random_bound = randint(int(cursor_checks_dict.get('min_wait')), int(cursor_checks_dict.get('max_wait')))
                    bound_updated = True
                    print('Random_bound updated!')
                except:
                    pass
            if iterator >= random_bound and random_bound != -1:
                print('We clicked!!')
                CursorControls.apply_click()
                threading.Thread(target=sound_tick, daemon=True).start()
                bound_updated = False
                iterator = 0
            iterator += 1
            timer_limit_iterator += 1
            threading.Thread(target=sound_clock_tick, daemon=True).start()
        else:
            on_stop_scrolling()
            threading.Thread(target=sound_stop, daemon=True).start()
            break


def on_start(icon):
    icon.visible = True
    threading.Thread(target=settings_watcher, args=(icon,), daemon=True).start()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    icon = Icon(APP_NAME, image, translated_variables["app_title"], menu)
    icon.run(setup=on_start)