import threading
import time
import sys
from win10toast import ToastNotifier
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

INTERVAL_SECONDS = 25 * 60  # 25 minutes
TOAST_DURATION = 8  # seconds
TOAST_TITLE = ""
TOAST_MESSAGE = "WORK."

_stop_event = threading.Event()

#Z - logo
def _create_image(size=64, color1=(0, 120, 215), color2=(255, 255, 255)):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([(0, 0), (size - 1, size - 1)], fill=color1)
    w = size * 0.58
    h = size * 0.5
    x = (size - w) / 2
    y = (size - h) / 2
    d.line([(x, y), (x + w, y), (x, y + h), (x + w, y + h)], fill=color2, width=int(size * 0.12))
    return img


class NotifierThread(threading.Thread):
    def __init__(self, interval, title, message, duration):
        super().__init__(daemon=True)
        self.interval = interval
        self.title = title
        self.message = message
        self.duration = duration
        self.notifier = ToastNotifier()

    def run(self):
        # first notification
        try:
            while not _stop_event.is_set():
                try:
                    self.notifier.show_toast(self.title, self.message, duration=self.duration, threaded=True)
                except Exception:
                    pass
                waited = 0
                while waited < self.interval and not _stop_event.is_set():
                    time.sleep(1)
                    waited += 1
        finally:
            return


def on_exit(icon, item):
    _stop_event.set()
    icon.stop()


def main():
    notifier_thread = NotifierThread(INTERVAL_SECONDS, TOAST_TITLE, TOAST_MESSAGE, TOAST_DURATION)
    notifier_thread.start()

    icon_image = _create_image(64)
    menu = (item('Exit', on_exit),)
    icon = pystray.Icon('zakruglayasya', icon_image, 'ЗАКРУГЛЯЙСЯ', menu)
    icon.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        _stop_event.set()
        sys.exit(0)


