import os
import psutil
import signal

RUNNING = False


def handler(signal, frame):
    global RUNNING
    if RUNNING:
        os.system('termux-notification -t "Кликер остановлен"'
                  ' -c "Нажмите кнопку уменьшения громкости 2 раза, чтобы остановить" '
                  '--priority max --id "clicker" --vibrate 100 --ongoing')
        RUNNING = False
    else:
        os.system('termux-notification -t "Кликер запущен" '
                  '-c "Нажмите кнопку уменьшения громкости 2 раза, чтобы остановить" '
                  '--priority max --id "clicker" --vibrate 100 --ongoing')
        RUNNING = True


signal.signal(signal.SIGUSR1, handler)

p = psutil.Process(int(open('data/listener_pid', 'r').read()))
while p.status() == psutil.STATUS_RUNNING:
    pass

else:
    os.system('termux-notification-remove "clicker"')
