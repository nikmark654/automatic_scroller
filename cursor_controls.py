import sys
import time
import random
import subprocess
from pynput.mouse import Button, Controller

_mouse = Controller()


class CursorControls:

    def get_position():
        return _mouse.position

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

    def restore_position(og_x, og_y):
        """Move cursor back to og_pos ±1px with human-like smooth movement."""
        try:
            target_x = og_x + random.randint(-1, 1)
            target_y = og_y + random.randint(-1, 1)
            cx, cy = _mouse.position
            dx = target_x - cx
            dy = target_y - cy
            distance = (dx ** 2 + dy ** 2) ** 0.5
            steps = max(15, int(distance * 0.4))
            for i in range(1, steps + 1):
                t = i / steps
                # smoothstep easing: slow start, fast middle, slow end
                ease = t * t * (3 - 2 * t)
                jx = random.uniform(-0.5, 0.5) if i < steps else 0
                jy = random.uniform(-0.5, 0.5) if i < steps else 0
                _mouse.position = (cx + dx * ease + jx, cy + dy * ease + jy)
                time.sleep(random.uniform(0.008, 0.018))
            
            _mouse.press(Button.left)
            time.sleep(random.uniform(0.05, 0.12))
            _mouse.release(Button.left)

            print(f'Restored cursor to ({target_x}, {target_y})')
            return True
        except:
            return False

    def handle_action(og_pos=None):
        """Dispatch: restore cursor if out of bounds, otherwise apply click."""
        if og_pos is not None:
            og_x, og_y = og_pos
            cx, cy = _mouse.position
            if abs(cx - og_x) > 10 or abs(cy - og_y) > 5:
                click_status = CursorControls.restore_position(og_x, og_y)
                return click_status
        click_status = CursorControls.apply_click()
        return click_status