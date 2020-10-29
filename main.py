import platform
import re
import signal
import subprocess
import sys
import traceback
from subprocess import Popen

import classes.errors
from clicker import *

if platform.system() == 'Windows':
    NULL = 'NUL'
else:
    NULL = 'data/null'

notification = 'termux-notification -c "Кликер запущен" --priority max --id "clicker" --vibrate 100 --ongoing'
remove_notification = 'termux-notification-remove "codm"'


class Clicker:
    run_key_events = 0
    proc = None
    listener = None
    notificator = None
    device_name = ''

    def connect(self):
        adb('disconnect')
        adb('kill-server')
        adb('start-server > server.txt')

        if 'error: no devices/emulators found' in open('server.txt').readlines():
            raise classes.errors.DevicesNotFound('Устройства не найдены')

        adb('devices > server.txt')
        self.device_name = re.search(r'emulator-\d+', open('server.txt').read())
        if not self.device_name:
            raise classes.errors.DevicesNotFound('Устройства не найдены')
        self.device_name = self.device_name.group()

        adb('shell mkdir -p /sdcard/codm_clicker', self.device_name)

    def run_clicker(self):
        self.proc = Popen([sys.executable, 'clicker.py', '--device-name', self.device_name],
                          stdout=open('out.log', 'a'), stderr=open('err.log', 'a'))

    def main(self):
        self.connect()
        self.listener = Popen(['adb', '-s', self.device_name, 'shell', 'getevent', '-q', '-t',
                               '/dev/input/event1', '> '
                                                    f'/sdcard/codm_clicker/events.txt'])

        with open('classes/data/listener_pid', 'w') as f:
            f.write(str(self.listener.pid))

        self.notificator = Popen([sys.executable, 'classes/notification_service.py'])
        os.kill(self.notificator.pid, signal.SIGUSR1)

        print('Кликер готов к запуску\nНажмите кнопку уменьшения громкости 2 раза, чтобы запустить/остановить')

        while True:
            subprocess.run(
                f'adb -s {self.device_name} pull /sdcard/codm_clicker/events.txt data/events.txt > data/null',
                shell=True)

            events = open('data/events.txt', 'r').readlines()
            events = list(filter(lambda x: '0001 0072 00000001' in x, events))

            if len(events) - self.run_key_events == 2:
                times = list(map(lambda x: float(re.search(r'\d+.\d+', x).group()), events))
                diff = times[-1] - times[-2]
                if diff <= 0.500:
                    if not self.proc:
                        os.kill(self.notificator.pid, signal.SIGUSR1)
                        self.run_clicker()
                    else:
                        os.kill(self.notificator.pid, signal.SIGUSR1)
                        self.proc.kill()
                        self.proc = None

                self.run_key_events = len(events)


c = Clicker()
try:
    c.main()
except:
    traceback.print_exc()
    c.proc.kill() if c.proc else ''
    c.listener.kill() if c.listener else ''
