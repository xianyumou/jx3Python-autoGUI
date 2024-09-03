# 2.py
# -*- coding: utf-8 -*-
import sys
import io

# 设置标准输入输出的编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import cv2
import numpy as np
import os
import time
import pyautogui
import re
from pygetwindow import getWindowsWithTitle
import random
import configparser
import sys

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# 解析配置文件中的延迟范围
delay_range = config.get('Settings', 'delay_range').split(',')
min_delay = int(delay_range[0])
max_delay = int(delay_range[1])

# 设置等待时间和超时时间
pyautogui.PAUSE = 1
pyautogui.FAILSAFE = True
timeout = int(config.get('Settings', 'timeout'))

# 定义函数，用于激活包含“剑网3”的窗口
def activate_jx3_window():
    pattern = re.compile(r'.*剑网3.*')
    matching_windows = [w for w in getWindowsWithTitle('') if pattern.search(w.title)]
    if matching_windows:
        matching_windows[0].activate()
        print(f"已激活窗口：{matching_windows[0].title}", flush=True)
    else:
        print("未找到与模式匹配的窗口", flush=True)

# 定义函数，用于查找和点击指定的图像
def click_image_in_window(window_title_pattern, image_path, timeout, button='left'):
    print(f"开始搜索图像: {image_path}", flush=True)
    if not os.path.exists(image_path):
        print(f"警告：图像文件 '{image_path}' 不存在！", flush=True)
        return
    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"警告：无法加载图像 '{image_path}'！", flush=True)
        return
    pattern = re.compile(window_title_pattern)
    matching_windows = [w for w in getWindowsWithTitle('') if pattern.search(w.title)]
    if not matching_windows:
        print(f"警告：未找到与模式 '{window_title_pattern}' 匹配的窗口！", flush=True)
        return
    activate_jx3_window()
    window = matching_windows[0]
    window_x, window_y, window_w, window_h = window.left, window.top, window.width, window.height
    screenshot = pyautogui.screenshot(region=(window_x, window_y, window_w, window_h))
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.7
    loc = np.where(res >= threshold)
    found_match = False
    for pt in zip(*loc[::-1]):
        x, y = pt
        x += window_x
        y += window_y
        print(f"找到了图像 '{image_path}' 在 ({x}, {y})", flush=True)
        click_x = x + template.shape[1] // 2
        click_y = y + template.shape[0] // 2
        pyautogui.moveTo(click_x, click_y, duration=0.5)
        time.sleep(0.5)
        pyautogui.click(click_x, click_y, button=button)  # 支持左键或右键点击
        print(f"点击了图像 '{image_path}'", flush=True)
        found_match = True
        time.sleep(1)
        safe_y = click_y - 500
        if safe_y < 0:
            safe_y = 0
        pyautogui.moveTo(click_x, safe_y, duration=0.5)
        break
    if found_match:
        print(f"完成搜索图像: {image_path}", flush=True)
        return
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            print(f"超时：未能在 {timeout} 秒内找到图像 '{image_path}'", flush=True)
            break
    print(f"完成搜索图像: {image_path}", flush=True)

# 主流程
def main():
    for i in range(99):
        activate_jx3_window()

        # 左键点击 yrkq.png
        click_image_in_window('剑网3.*', 'images/yrkq.png', timeout, button='left')

        # 随机等待 min_delay 到 max_delay 秒
        wait_time = random.randint(min_delay, max_delay)
        print(f"正在随机等待{wait_time}秒", flush=True)
        for j in range(wait_time):
            print(f"正在随机等待{wait_time - j}秒", flush=True)
            time.sleep(1)

        # 左键点击 yrgb.png
        click_image_in_window('剑网3.*', 'images/yrgb.png', timeout, button='left')

        print(f'通用艺人工作中当前循环次数：{i}', flush=True)
        print("等待5秒后再进行下一次循环", flush=True)
        time.sleep(5)

if __name__ == "__main__":
    main()