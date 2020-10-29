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


def main():
    pid = int(open('data/listener_pid', 'r').read())
    os.system('echo 13 > a.txt')

    with open('data/ntf_pid', 'w') as f:
        f.write(str(os.getpid()))

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


if __name__ == '__main__':
    main()
