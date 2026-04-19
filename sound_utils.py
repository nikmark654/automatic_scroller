import queue
import threading
import numpy as np
import sounddevice as sd

# Single audio worker — all playback goes through this queue to avoid
# concurrent sd.play() calls which cause PortAudio double-free crashes.
_audio_queue = queue.Queue()


def _audio_worker():
    while True:
        wave, sample_rate = _audio_queue.get()
        sd.play(wave, sample_rate)
        sd.wait()


threading.Thread(target=_audio_worker, daemon=True).start()


def _enqueue(wave, sample_rate=44100):
    _audio_queue.put((wave.astype(np.float32), sample_rate))


def _sine(frequency, duration, volume=0.4, fade_ms=10, sample_rate=44100):
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)
    wave = volume * np.sin(2 * np.pi * frequency * t)
    fade = int(sample_rate * fade_ms / 1000)
    ramp = np.linspace(0, 1, fade)
    wave[:fade] *= ramp
    wave[-fade:] *= ramp[::-1]
    return wave


def sound_start():
    """Two rising tones — scrolling has started."""
    wave = np.concatenate([_sine(660, 0.07), _sine(880, 0.07)])
    _enqueue(wave)


def sound_tick():
    """Short high tick — a click was applied."""
    _enqueue(_sine(1000, 0.05))


def sound_clock_tick():
    """Mechanical clock tick — fires every second while timer runs.
    Skipped if audio is already busy so ticks never pile up."""
    if not _audio_queue.empty():
        return
    sample_rate = 44100
    duration = 0.08
    samples = int(sample_rate * duration)
    rng = np.random.default_rng()
    noise = rng.uniform(-1, 1, samples)
    decay = np.exp(-np.linspace(0, 40, samples))
    tick = 0.002 * noise * decay
    t = np.linspace(0, duration, samples, False)
    thump = 0.01 * np.sin(2 * np.pi * 180 * t) * np.exp(-np.linspace(0, 30, samples))
    wave = np.clip(tick + thump, -1.0, 1.0)
    _enqueue(wave, sample_rate)


def sound_stop():
    """Three descending tones — scrolling has stopped due to timer limit."""
    wave = np.concatenate([_sine(440, 1.2), _sine(330, 1.0), _sine(220, 1.4)])
    _enqueue(wave)