import sys
import time
import random
import subprocess
from pynput.mouse import Button, Controller

_mouse = Controller()


class CursorControls:

    def apply_click():
        try:
            cx, cy = _mouse.position
            dx = random.uniform(-2.0, 2.0)
            dy = random.uniform(-2.0, 2.0)
            steps = random.randint(2, 4)
            for i in range(1, steps + 1):
                ease = 1 - (1 - i / steps) ** 2
                _mouse.position = (cx + dx * ease, cy + dy * ease)
                time.sleep(random.uniform(0.001, 0.003))
            _mouse.press(Button.left)
            time.sleep(random.uniform(0.05, 0.12))
            _mouse.release(Button.left)
            print('We report clicking from inside the CursorControls')
            return True
        except:
            return False
        
    def check_device_sound_status():
        try:
            if sys.platform == "win32":
                from pycaw.pycaw import AudioUtilities
                sessions = AudioUtilities.GetAllSessions()
                return any(s.Process is not None for s in sessions)
            elif sys.platform == "darwin":
                result = subprocess.run(
                    ["ioreg", "-r", "-c", "IOAudioEngine", "-d", "3"],
                    capture_output=True, text=True, timeout=2
                )
                return '"IOAudioEngineState" = 1' in result.stdout
            else:
                result = subprocess.run(
                    ["pactl", "list", "sinks"],
                    capture_output=True, text=True, timeout=2
                )
                return "State: RUNNING" in result.stdout
        except:
            return None