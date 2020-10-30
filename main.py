import re
import subprocess
import sys
import traceback
from subprocess import Popen

import classes.errors
from clicker import *


class Clicker:
    run_key_events = 0
    close_key_events = 0
    proc = None
    listener = None
    notificator = None
    device_name = ''
    home_path = ''

    def connect(self):
        adb('disconnect')
        adb('kill-server')
        adb('start-server > data/server')

        if 'error: no devices/emulators found' in open('data/server', 'r').readlines():
            raise classes.errors.DevicesNotFound('Устройства не найдены')

        adb('devices > data/server')
        s = open('data/server', 'r').read()
        if 'unauthorized' in s:
            raise classes.errors.DevicesNotFound('Устройство не авторизовано. '
                                                 'Отключите телефон от устройства и нажмите кнопку "Разрешить" '
                                                 'во всплывающем окне')

        self.device_name = re.search(r'emulator-\d+', s)
        if not self.device_name:
            raise classes.errors.DevicesNotFound('Устройства не найдены')
        self.device_name = self.device_name.group()

        adb(f'shell mkdir -p /sdcard/codm_clicker', self.device_name)

    def main(self):
        self.connect()
        self.start_listener()

        print('\nКликер готов к запуску\nНажмите кнопку уменьшения громкости 2 раза, чтобы запустить/остановить')

        while True:
            up, down = self.get_new_events()

            if len(down) - self.run_key_events == 2:
                diff = down[-1] - down[-2]
                self.run_key_events = len(down)
                if diff <= 0.500:
                    if not self.proc:
                        self.start_clicker()
                    else:
                        self.stop_clicker()

            if len(up) - self.close_key_events == 2:
                diff = up[-1] - up[-2]
                self.close_key_events = len(up)
                if diff <= 0.500:
                    exit()
                    sys.exit()

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
        up, down = [], []
        for i in open('data/events.txt', 'r').readlines():
            if re.findall('0001 0073 00000001', i):
                up.append(float(re.search(r'\d+.\d+', i).group()))
            if re.findall('0001 0072 00000001', i):
                down.append(float(re.search(r'\d+.\d+', i).group()))
        return up, down

    def start_clicker(self):
        self.vibrate(100)
        self.proc = Popen([sys.executable, 'clicker.py', '--device-name', self.device_name],
                          stdout=open('data/clicker_out.log', 'a'), stderr=open('data/clicker_err.log', 'a'))
        print('Кликер запущен')

    def stop_clicker(self):
        self.vibrate(100)
        self.proc.kill()
        self.proc = None
        print('Кликер остановлен')


c = Clicker()


def exit():
    c.proc.kill() if c.proc else ''
    c.listener.kill() if c.listener else ''


try:
    c.main()
except SystemExit:
    pass
except:
    traceback.print_exc()
    exit()
