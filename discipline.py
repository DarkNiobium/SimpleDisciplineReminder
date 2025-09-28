"""
Простое фоновое приложение для Windows 10 на Python.
Показывает toast-уведомление "ЗАКРУГЛЯЙСЯ!" каждые 25 минут и живёт в системном трее.

Требования:
  pip install pystray pillow win10toast

Запуск без консоли (рекомендуется):
  pythonw.exe "C:\путь\к\Приложение_ЗАКРУГЛЯЙСЯ.py"

Чтобы приложение появилось при входе в Windows — создайте ярлык запуска в папке автозагрузки.
"""

import threading
import time
import sys
from win10toast import ToastNotifier
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

INTERVAL_SECONDS = 25 * 60  # 25 минут
TOAST_DURATION = 8  # длительность показа уведомления в секундах
TOAST_TITLE = ""
TOAST_MESSAGE = "ЗАКРУГЛЯЙСЯ!"

_stop_event = threading.Event()


def _create_image(size=64, color1=(0, 120, 215), color2=(255, 255, 255)):
    # создаёт простую иконку для трея (кружок с буквой Z)
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # фон
    d.ellipse([(0, 0), (size - 1, size - 1)], fill=color1)
    # буква Z
    w = size * 0.58
    h = size * 0.5
    x = (size - w) / 2
    y = (size - h) / 2
    # рисуем Z как линию
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
        # отправляем первое уведомление сразу при старте
        try:
            while not _stop_event.is_set():
                # показать уведомление (threaded=True чтобы не блокировать)
                try:
                    self.notifier.show_toast(self.title, self.message, duration=self.duration, threaded=True)
                except Exception:
                    # в редких случаях win10toast может выбросить ошибку — игнорируем и продолжаем
                    pass
                # ждать интервал по кусочкам чтобы реагировать на остановку
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
    # при закрытии трея pystray вызовет on_exit
    icon.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        _stop_event.set()
        sys.exit(0)
