#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import traceback

import pytesseract as pt
from PIL import Image
import os
import config

graphic_boxes = {
    1080: (0, 1030, 330, 1080)
}

geometries = {
    2340: {
        'screens': [
            (2000, 960, 2300, 1030),
            (1000, 50, 1350, 150),
            (1800, 980, 2200, 1080)
        ],
        'points': [
            (2100, 970),
            (2230, 60),
            (2100, 1000)
        ],
        'swipe': (2340 // 2 + 50, 1080 // 4, 2340 // 2 + 50, 1080 // 3 * 2)
    },
    2160: {
        'screens': [
            (1820, 960, 2320, 1030),
            (820, 50, 1260, 150),
            (1920, 980, 2020, 1050)
        ],
        'points': [
            (1920, 970),
            (2060, 50),
            (2000, 1000)
        ],
        'swipe': (2160 // 2 + 50, 1080 // 4, 2160 // 2 + 50, 1080 // 3 * 2)
    },
    2246: {
        'screens': [
            (1800, 960, 2100, 1030),
            (950, 30, 1300, 150),
            (1850, 980, 2020, 1050)
        ],
        'points': [
            (1800, 1000),
            (2060, 60),
            (1900, 1000)
        ],
        'swipe': (2246 // 2 + 50, 1080 // 4, 2246 // 2 + 50, 1080 // 3 * 2)
    }
}

flag = False


def diff(s1, s2):
    a, b, c = len(s1), len(s2), 0.0

    for sym in s1:
        if sym in s2:
            c += 1

    return c / (a + b - c) * 100


def adb(q):
    os.system('adb ' + q)


def get_screenshot() -> Image.Image:
    adb('shell screencap -p sdcard/scr.png')
    adb('pull sdcard/scr.png scr.png')
    adb('shell rm sdcard/scr.png')
    return Image.open('scr.png')


def lobby_screen(im):
    global flag
    if not flag:
        print('resolution:', im.size)
        flag = True

    im.crop(geometries[max(im.size)]['screens'][0]).save('cropped.png')
    res = pt.image_to_string('cropped.png').lower().strip()
    if res:
        print('lobby: ' + res)

    for i in ['start', 'next', 'ready']:
        if diff(i, res) > 60 or i in res.split():
            return True

    return False


def battle(im):
    im.crop(graphic_boxes[min(im.size)]).save('cropped.png')
    res = pt.image_to_string('cropped.png').lower().strip()
    if res:
        print('battle_left_bottom_corner: ' + res)

    for i in ['graphic quality']:
        if diff(i, res) > 30 or i in res.split():
            return True

    return False


def first_exit_screen(im):
    im.crop(geometries[max(im.size)]['screens'][1]).save('cropped.png')
    res = pt.image_to_string('cropped.png').lower().strip()
    if res:
        print('first_exit: ' + res)

    for i in ['victory', 'defeat']:
        if diff(i, res) > 70 or i in res.split():
            return True

    return False


def second_exit_screen(im):
    im.crop(geometries[max(im.size)]['screens'][2]).save('cropped.png')
    res = pt.image_to_string('cropped.png').lower().strip()
    if res:
        print('second_exit: ' + res)

    for i in ['exit', 'next']:
        if diff(i, res) > 50 or i in res.split():
            return True

    return False


def main():
    adb(f"connect {config.ip}")
    while True:
        time.sleep(config.repeat_interval)

        image = get_screenshot()
        p = None
        in_battle = False

        if lobby_screen(image):
            p = geometries[max(image.size)]['points'][0]

        if battle(image):
            in_battle = True
            if config.suicide:
                p = geometries[max(image.size)]['swipe']
                p = ' '.join(list(map(str, p)))
                c = ' '.join(map(str, [image.size[0] - 80, 80]))
                adb(f'shell input tap {c}')
                adb(f'shell input swipe 50 50 50 50 5500')

        if config.with_first_exit_screen:
            if first_exit_screen(image):
                p = geometries[max(image.size)]['points'][1]

        if second_exit_screen(image):
            p = geometries[max(image.size)]['points'][2]

        if p:
            p = ' '.join(list(map(str, p)))
            adb(f'shell input tap {p}')

        if in_battle:
            adb('shell input swipe 50 50 50 50 2000')


def debug(name, box):
    Image.open(name).crop(box).save('0.png')
    print(pt.image_to_string('0.png'))


if __name__ == '__main__':
    try:
        main()
    except:
        traceback.print_exc()
    input()
