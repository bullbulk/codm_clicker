import re
import subprocess
import sys
import traceback
from subprocess import Popen

import classes.errors
from clicker import *


class Clicker:
    run_key_events = 0
    proc = None
    listener = None
    notificator = None
    device_name = ''
    home_path = ''

    def connect(self):
        adb('disconnect')
        adb('kill-server')
        adb('start-server > data/server')

        if 'error: no devices/emulators found' in open('data/server').readlines():
            raise classes.errors.DevicesNotFound('Устройства не найдены')

        adb('devices > data/server')
        self.device_name = re.search(r'emulator-\d+', open('data/server').read())
        if not self.device_name:
            raise classes.errors.DevicesNotFound('Устройства не найдены')
        self.device_name = self.device_name.group()

        Popen('adb shell ls sdcard', stdout=open('data/ls', 'w'))

        adb('shell mkdir -p /sdcard/codm_clicker', self.device_name)

    def main(self):
        self.connect()
        self.start_listener()

        print('Кликер готов к запуску\nНажмите кнопку уменьшения громкости 2 раза, чтобы запустить/остановить')

        while True:
            events = self.get_new_events()

            if len(events) - self.run_key_events == 2:
                times = list(map(lambda x: float(re.search(r'\d+.\d+', x).group()), events))
                diff = times[-1] - times[-2]
                if diff <= 0.500:
                    if not self.proc:
                        self.start_clicker()
                    else:
                        self.stop_clicker()

                self.run_key_events = len(events)

    def vibrate(self, ms):
        os.system(f'termux-vibrate -f -d {ms}')

    def download_event(self):
        subprocess.run(
            f'adb -s {self.device_name} pull /sdcard/codm_clicker/events.txt data/events.txt > data/null',
            shell=True
        )

    def start_listener(self):
        self.listener = Popen(
            ['adb', '-s', self.device_name, 'shell', 'getevent', '-q', '-t',
             '/dev/input/event1', '> '
                                  f'/sdcard/codm_clicker/events.txt']
        )

    def get_new_events(self):
        self.download_event()
        return list(filter(lambda x: '0001 0072 00000001' in x, open('data/events.txt', 'r').readlines()))

    def start_clicker(self):
        self.vibrate(100)
        self.proc = Popen([sys.executable, 'clicker.py', '--device-name', self.device_name],
                          stdout=open('out.log', 'a'), stderr=open('err.log', 'a'))

    def stop_clicker(self):
        self.vibrate(100)
        self.proc.kill()
        self.proc = None


c = Clicker()
try:
    c.main()
except:
    traceback.print_exc()
    c.proc.kill() if c.proc else ''
    c.listener.kill() if c.listener else ''
