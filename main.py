import sys

import config
from clicker import *
from subprocess import Popen
import platform
import classes.errors

if platform.system() == 'Windows':
    NULL = 'NUL'
else:
    NULL = '/dev/null'


class Clicker:
    power_key_events = 0
    proc = None
    listener = None

    def connect(self):
        adb('kill-server')
        adb('start-server > server.txt')
        if 'error: no devices/emulators found' in open('server.txt').readlines():
            raise classes.errors.DevicesNotFound('Устройства не найдены')
        adb('shell mkdir -p /sdcard/codm_clicker')

    def run_clicker(self):
        #self.proc = Popen([sys.executable, 'clicker.py'], stdout=open('out.log', 'a'), stderr=open('err.log', 'a'))
        self.connect()
        os.system('python clicker.py')

    def main(self):
        self.connect()
        self.listener = Popen('adb shell getevent -q /dev/input/event1 > /sdcard/codm_clicker/events.txt')

        while True:
            adb(f'pull /sdcard/codm_clicker/events.txt data/events.txt > {NULL}')
            events = open('data/events.txt', 'r').readlines()
            events = list(filter(lambda x: x == '0001 0074 00000001\n', events))
            if len(events) != self.power_key_events:
                if not self.proc:
                    self.run_clicker()
                    print('Кликер запущен')
                else:
                    self.proc.kill()
                    self.proc = None
                    print('Кликер остановлен')

                self.power_key_events = len(events)


c = Clicker()
try:
    c.run_clicker()
except:
    c.proc.kill() if c.proc else ''
    c.listener.kill() if c.listener else ''