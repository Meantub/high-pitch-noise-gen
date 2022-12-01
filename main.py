import threading

from pystray import MenuItem, Menu
import pystray
import numpy as np
import pyaudio

from PIL import Image


def play(event: threading.Event):
    p = pyaudio.PyAudio()

    print(p.get_default_output_device_info())

    volume = 0.01
    sampling_rate = 44_800
    duration = 1.0
    frequency = 1_000_000.0

    samples = (np.sin(2 * np.pi * np.arange(sampling_rate * duration) * frequency / sampling_rate)).astype(np.float32)

    output_bytes = (volume * samples).tobytes()

    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sampling_rate, output=True)

    while True:
        # If the thread stop event comes in terminate everything
        if event.is_set():
            stream.stop_stream()
            stream.close()

            p.terminate()
            break

        try:
            stream.write(output_bytes)
        except KeyboardInterrupt:
            stream.stop_stream()
            stream.close()

            p.terminate()
            raise SystemExit


def stop(play_thread: threading.Thread, event: threading.Event):
    event.set()
    play_thread.join()


def exit_app(icon: pystray.Icon, play_thread: threading.Thread, event: threading.Event):
    stop(play_thread, event)

    icon.stop()


def main():
    image = Image.open("icon.png")
    image = image.convert("RGBA")

    event = threading.Event()
    play_thread = threading.Thread(target=play, args=(event,))

    sys_icon = pystray.Icon("High Pitch Noise")
    sys_icon.icon = image
    sys_icon.menu = Menu(
        MenuItem('Play', lambda: play_thread.start()),
        MenuItem('Stop', lambda: stop(play_thread, event)),
        MenuItem('Exit', lambda: exit_app(sys_icon, play_thread, event))
    )
    sys_icon.title = "High Pitch Noise Gen"

    sys_icon.run()


if __name__ == '__main__':
    main()
