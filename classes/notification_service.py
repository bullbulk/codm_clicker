import os
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

pid = int(open('../data/listener_pid', 'r').read())
pid_using = True

try:
    os.kill(pid, 0)
except OSError:
    pid_using = False
else:
    pid_using = True

while pid_using:
    try:
        os.kill(pid, 0)
    except OSError:
        pid_using = False
    else:
        pid_using = True

else:
    os.system('termux-notification-remove "clicker"')
