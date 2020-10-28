#!/usr/bin/python
# -*- coding: utf-8 -*-
import concurrent.futures
import os
import sys
import time
from typing import List, Tuple

import pytesseract as pt
from PIL import Image

import config
from props import *
import argparse

try:
    os.listdir('data')
except FileNotFoundError:
    os.mkdir('data')


def diff(s1: str, s2: str) -> float:
    a, b, c = len(s1), len(s2), 0.0

    for sym in s1:
        if sym in s2:
            c += 1

    return c / (a + b - c) * 100


def adb(comm, d_name=None) -> None:
    os.system(f'adb -s {device_name if device_name else d_name} ' + comm)


def text_recognize(im: Image.Image, box: Tuple[int, int, int, int], filename: str) -> str:
    im.crop(box).save(f'data/{filename}.png')
    return pt.image_to_string(f'data/{filename}.png').lower().strip()


def similarity(original: str, choices: List[str], percent: int, blacklist=None) -> bool:
    if blacklist is None:
        blacklist = []

    print(blacklist, choices)

    for j in blacklist:
        if diff(j, original) > percent or j in original.split():
            print(1)
            return False

    for i in choices:
        if diff(i, original) > percent or i in original.split():
            print(2)
            return True

    return False


def get_screenshot() -> Image.Image:
    adb('shell screencap -p sdcard/codm_clicker/scr.png')
    adb('pull sdcard/codm_clicker/scr.png data/scr.png')
    adb('shell rm sdcard/codm_clicker/scr.png')
    return Image.open('data/scr.png')


def run_futures(functions):
    futures = []
    res = []

    with concurrent.futures.ThreadPoolExecutor() as ex:
        for f in functions:
            futures.append(ex.submit(f, 'data/scr.png'))

    for i in futures:
        res.append(i.result())

    return res


def suicide(image):
    swipe = geometries[max(image.size)]['swipe']
    swipe = ' '.join(list(map(str, swipe)))
    change_weapon = ' '.join(map(str, [image.size[0] - 80, 80]))
    adb(f'shell input tap {change_weapon}')
    adb(f'shell input swipe {swipe}')
    adb(f'shell input swipe 50 50 50 50 5500')


class ADBClicker:
    geoms = geometries
    g_box = graphic_boxes
    resolution_printed = False
    repeat_interval = config.repeat_interval

    def __init__(self):
        self.funcs = [self.lobby_and_bp, self.battle, self.first_exit_screen, self.second_exit_screen]

    def lobby_and_bp(self, filename: str) -> bool:
        im = Image.open(filename)
        if not self.resolution_printed:
            print('resolution:', im.size)
            self.resolution_printed = True

        res = text_recognize(im, geometries[max(im.size)]['screens'][0], 'lobby')

        if res:
            print('lobby: ' + res)

        return similarity(res, ['start', 'next', 'ready'], 60, ['cancel'])

    def battle(self, filename: str) -> bool:
        im = Image.open(filename)
        res = text_recognize(im, graphic_boxes[min(im.size)], 'battle')

        if res:
            print('battle_left_bottom_corner: ' + res)

        return similarity(res, ['graphic quality'], 30)

    def first_exit_screen(self, filename: str) -> bool:
        im = Image.open(filename)
        res = text_recognize(im, geometries[max(im.size)]['screens'][1], 'first_exit_screen')

        if res:
            print('first_exit: ' + res)

        return similarity(res, ['victory', 'defeat'], 70)

    def second_exit_screen(self, filename: str) -> bool:
        im = Image.open(filename)
        res = text_recognize(im, geometries[max(im.size)]['screens'][2], 'second_exit_screen')

        if res:
            print('second_exit: ' + res)

        return similarity(res, ['exit', 'next'], 70, blacklist=['cancel'])

    def press(self):
        adb(f'shell input tap {self.press_point}')

    def main_loop(self):
        while True:
            press_point = None
            in_battle = False

            image = get_screenshot()

            time.sleep(self.repeat_interval)
            t = time.time()
            res = run_futures(self.funcs)

            if res[0]:
                """result of "lobby_and_br" function"""
                press_point = geometries[max(image.size)]['points'][0]

            if res[1]:
                """result of "battle" function"""
                in_battle = True
                if config.suicide:
                    suicide(image)

            if config.with_first_exit_screen:
                if res[2]:
                    """result of "first_exit_screen" function"""
                    press_point = geometries[max(image.size)]['points'][1]

            if res[3]:
                """result of "second_exit_screen" function"""
                press_point = geometries[max(image.size)]['points'][2]

            if press_point:
                self.press_point = ' '.join(list(map(str, press_point)))
                self.press()

            if in_battle:
                """tap fire button"""
                adb('shell input swipe 50 50 50 50 2000')

            estimated = time.time() - t
            if estimated > config.repeat_interval:
                self.repeat_interval = 0
            else:
                self.repeat_interval = config.repeat_interval - estimated


p = argparse.ArgumentParser()
p.add_argument('--device-name')
device_name = p.parse_args().device_name

if __name__ == '__main__':
    ADBClicker().main_loop()
