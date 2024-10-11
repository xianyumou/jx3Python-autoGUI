# jx3_automation3.py
#无界种花脚本
# -*- coding: utf-8 -*-
import sys
import io
import cv2
import numpy as np
import os
import time
import pyautogui
import re
from pygetwindow import getWindowsWithTitle
import random
import configparser

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

def activate_jx3_window(output_callback, stop_event):
    """
    激活包含“剑网3”的窗口。
    """
    if stop_event and stop_event.is_set():
        return
    pattern = re.compile(r'.*剑网3.*')
    matching_windows = [w for w in getWindowsWithTitle('') if pattern.search(w.title)]
    if matching_windows:
        matching_windows[0].activate()
        output_callback(f"已激活窗口：{matching_windows[0].title}")
    else:
        output_callback("未找到与模式匹配的窗口")

def click_image_in_window(window_title_pattern, image_path, timeout, button='left', output_callback=print, stop_event=None):
    """
    在指定窗口中查找并点击指定的图像。

    参数:
        window_title_pattern (str): 窗口标题的正则表达式模式。
        image_path (str): 图像文件路径。
        timeout (int): 查找图像的超时时间（秒）。
        button (str): 点击的鼠标按钮（默认为'left'）。
        output_callback (function): 输出回调函数，默认为 print
        stop_event (QThread): 停止事件，默认为 None
    """
    output_callback(f"开始搜索图像: {image_path}")
    if not os.path.exists(image_path):
        output_callback(f"警告：图像文件 '{image_path}' 不存在！")
        return
    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        output_callback(f"警告：无法加载图像 '{image_path}'！")
        return
    pattern = re.compile(window_title_pattern)
    matching_windows = [w for w in getWindowsWithTitle('') if pattern.search(w.title)]
    if not matching_windows:
        output_callback(f"警告：未找到与模式 '{window_title_pattern}' 匹配的窗口！")
        return
    activate_jx3_window(output_callback, stop_event)
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
        if stop_event and stop_event.is_set():
            return
        x, y = pt
        x += window_x
        y += window_y
        output_callback(f"找到了图像 '{image_path}' 在 ({x}, {y})")
        click_x = x + template.shape[1] // 2
        click_y = y + template.shape[0] // 2
        pyautogui.moveTo(click_x, click_y, duration=0.5)
        time.sleep(0.5)
        pyautogui.click(click_x, click_y, button=button)  # 支持左键或右键点击
        output_callback(f"点击了图像 '{image_path}'")
        found_match = True
        time.sleep(1)
        safe_y = click_y - 500
        if safe_y < 0:
            safe_y = 0
        pyautogui.moveTo(click_x, safe_y, duration=0.5)
        break
    if found_match:
        output_callback(f"完成搜索图像: {image_path}")
        return
    start_time = time.time()
    while True:
        if stop_event and stop_event.is_set():
            return
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            output_callback(f"超时：未能在 {timeout} 秒内找到图像 '{image_path}'")
            break
    output_callback(f"完成搜索图像: {image_path}")

def press_key(key, duration=0.1, output_callback=print, stop_event=None):
    """
    模拟按键操作。

    参数:
        key (str): 按键名称。
        duration (float): 按键持续时间（秒）。
        output_callback (function): 输出回调函数，默认为 print
        stop_event (QThread): 停止事件，默认为 None
    """
    if stop_event and stop_event.is_set():
        return
    output_callback(f"按下键 '{key}'")
    pyautogui.keyDown(key)
    time.sleep(duration)
    pyautogui.keyUp(key)
    output_callback(f"释放键 '{key}'")

def perform_automation(output_callback=print, stop_event=None):
    """
    执行自动化流程。
    """
    for i in range(99):
        if stop_event and stop_event.is_set():
            output_callback("Automation stopped.")
            return
        activate_jx3_window(output_callback, stop_event)

        # 左键点击 gb.png
        click_image_in_window('剑网3.*', 'images/gb.png', timeout, button='left', output_callback=output_callback, stop_event=stop_event)

        # 按 F 键
        press_key('f', output_callback=output_callback, stop_event=stop_event)

        # 左键点击 plbz.png
        click_image_in_window('剑网3.*', 'images/plbz.png', timeout, button='left', output_callback=output_callback, stop_event=stop_event)

        # 随机等待 min_delay 到 max_delay 秒
        wait_time = random.randint(min_delay, max_delay)
        output_callback(f"正在随机等待{wait_time}秒")
        for j in range(wait_time):
            if stop_event and stop_event.is_set():
                output_callback("Automation stopped.")
                return
            output_callback(f"正在随机等待{wait_time - j}秒")
            time.sleep(1)

        # 左键点击 gb.png
        click_image_in_window('剑网3.*', 'images/gb.png', timeout, button='left', output_callback=output_callback, stop_event=stop_event)

        # 按 F 键
        press_key('f', output_callback=output_callback, stop_event=stop_event)

        # 左键点击 plsh.png
        click_image_in_window('剑网3.*', 'images/plsh.png', timeout, button='left', output_callback=output_callback, stop_event=stop_event)

        output_callback(f'通用艺人工作中当前循环次数：{i}')
        output_callback("等待5秒后再进行下一次循环")
        time.sleep(5)

if __name__ == "__main__":
    perform_automation()