import cv2
import numpy as np
import os
import time
import pyautogui
import re
from pygetwindow import getWindowsWithTitle
import random
import tkinter as tk

# 创建一个Tkinter窗口
root = tk.Tk()
root.title("艺人挂机状态")
root.geometry("300x200")  # 设置窗口大小
root.wm_attributes("-topmost", True)  # 设置窗口始终置顶
root.wm_attributes("-alpha", 0.5)  # 设置窗口透明度
root.configure(bg='white')  # 设置背景颜色

# 创建一个Label用于显示状态信息
status_label = tk.Label(root, text="", bg='white')
status_label.pack(pady=10)


# 更新状态函数
def update_status(text):
    status_label.config(text=text)
    root.update()


# 设置等待时间
pyautogui.PAUSE = 1
pyautogui.FAILSAFE = True


# 定义函数，用于激活包含“剑网3”的窗口
def activate_jx3_window():
    # 使用正则表达式匹配包含“剑网3”的窗口标题
    pattern = re.compile(r'.*剑网3.*')

    # 获取所有窗口列表，并筛选出与模式匹配的窗口
    matching_windows = [w for w in getWindowsWithTitle('') if pattern.search(w.title)]

    if matching_windows:
        # 激活第一个匹配的窗口
        matching_windows[0].activate()
        print(f"已激活窗口：{matching_windows[0].title}")
        update_status(f"已激活窗口：{matching_windows[0].title}")
    else:
        print("未找到与模式匹配的窗口")
        update_status("未找到与模式匹配的窗口")


# 定义函数，用于查找和点击指定的图像
def click_image_in_window(window_title_pattern, image_path, timeout=5, button='left'):
    print(f"开始搜索图像: {image_path}")
    update_status(f"开始搜索图像: {image_path}")

    # 确保图像文件存在
    if not os.path.exists(image_path):
        print(f"警告：图像文件 '{image_path}' 不存在！")
        update_status(f"警告：图像文件 '{image_path}' 不存在！")
        return

    # 加载目标图像
    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if template is None:
        print(f"警告：无法加载图像 '{image_path}'！")
        update_status(f"警告：无法加载图像 '{image_path}'！")
        return

    # 使用正则表达式匹配窗口标题
    pattern = re.compile(window_title_pattern)
    matching_windows = [w for w in getWindowsWithTitle('') if pattern.search(w.title)]

    if not matching_windows:
        print(f"警告：未找到与模式 '{window_title_pattern}' 匹配的窗口！")
        update_status(f"警告：未找到与模式 '{window_title_pattern}' 匹配的窗口！")
        return

    # 激活窗口
    activate_jx3_window()

    # 获取指定窗口的位置和尺寸
    window = matching_windows[0]
    window_x, window_y, window_w, window_h = window.left, window.top, window.width, window.height

    # 获取屏幕截图
    screenshot = pyautogui.screenshot(region=(window_x, window_y, window_w, window_h))
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    # 转换为灰度图像
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    # 使用模板匹配
    res = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.7  # 降低阈值以更容易匹配到图像
    loc = np.where(res >= threshold)

    found_match = False  # 添加一个标志来标记是否找到了匹配项

    # 如果找到了匹配项
    for pt in zip(*loc[::-1]):
        x, y = pt
        # 将坐标转换回全局坐标系
        x += window_x
        y += window_y
        print(f"找到了图像 '{image_path}' 在 ({x}, {y})")
        update_status(f"找到了图像 '{image_path}' 在 ({x}, {y})")

        # 计算点击位置
        click_x = x + template.shape[1] // 2
        click_y = y + template.shape[0] // 2

        # 立即移动到目标位置
        pyautogui.moveTo(click_x, click_y, duration=0.5)  # 添加 duration 参数来控制移动速度

        # 添加额外的延迟
        time.sleep(0.5)

        # 点击匹配到的位置
        pyautogui.click(click_x, click_y, button='left')  # 明确指定左键点击
        print(f"点击了图像 '{image_path}'")
        update_status(f"点击了图像 '{image_path}'")
        found_match = True  # 标记找到了匹配项

        # 再次添加额外的延迟
        time.sleep(1)

        # 立即移动到安全位置
        safe_y = click_y - 500
        if safe_y < 0:
            safe_y = 0
        pyautogui.moveTo(click_x, safe_y, duration=0.5)  # 添加 duration 参数来控制移动速度
        break

    # 如果找到了匹配项，跳出循环
    if found_match:
        print(f"完成搜索图像: {image_path}")
        update_status(f"完成搜索图像: {image_path}")
        return

    # 如果未找到匹配项，检查是否超过了超时时间
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            print(f"超时：未能在 {timeout} 秒内找到图像 '{image_path}'")
            update_status(f"超时：未能在 {timeout} 秒内找到图像 '{image_path}'")
            break

    print(f"完成搜索图像: {image_path}")
    update_status(f"完成搜索图像: {image_path}")


# 主流程
for i in range(37):
    # 激活窗口
    activate_jx3_window()

    # 点击艺人开启按钮
    click_image_in_window('剑网3.*', 'images/yrkq.png', timeout=5)

    # 右键点击 gdc.png
    click_image_in_window('剑网3.*', 'images/gdc.png', timeout=5, button='right')

    # 左键点击 plbz.png
    click_image_in_window('剑网3.*', 'images/plbz.png', timeout=5)

    # 随机等待600-630秒
    wait_time = random.randint(600, 630)
    print(f"正在随机等待{wait_time}秒")
    update_status(f"正在随机等待{wait_time}秒")
    for j in range(wait_time):
        update_status(f"正在随机等待{wait_time - j}秒")
        time.sleep(1)

    # 点击艺人关闭按钮
    click_image_in_window('剑网3.*', 'images/yrgb.png', timeout=5)

    # 右键点击 gdc.png
    click_image_in_window('剑网3.*', 'images/gdc.png', timeout=5, button='right')

    # 左键点击 plsh.png
    click_image_in_window('剑网3.*', 'images/plsh.png', timeout=5)

    # 添加2-3秒的随机延迟
    random_delay = random.uniform(2, 3)
    print(f"随机等待{random_delay:.2f}秒")
    update_status(f"随机等待{random_delay:.2f}秒")
    time.sleep(random_delay)

    # 打印日志
    print(f'艺人挂机工作中当前循环次数：{i}')
    update_status(f'艺人挂机工作中当前循环次数：{i}')

    # 等待5秒后再进行下一次循环
    print("等待5秒后再进行下一次循环")
    update_status("等待5秒后再进行下一次循环")
    time.sleep(5)

# 运行或打开
pyautogui.hotkey('win', 'r')
pyautogui.typewrite('shutdown -s -t 60')
pyautogui.press('enter')

# 进入事件循环
root.mainloop()