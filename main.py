import sys
import io
import signal
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QLineEdit, QLabel, QScrollArea, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import subprocess
import logging
import configparser

# 设置标准输出流的编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')

class ScriptRunner(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf-8')
        self.initUI()

    def initUI(self):
        self.setWindowTitle("剑网三Auto种花和艺人--by十二段-梦江南 （交流群-摸鱼883225870）")
        self.setGeometry(100, 100, 280, 400)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建垂直布局
        layout = QVBoxLayout(central_widget)

        # 添加延迟时间范围输入框和标签
        self.delay_label = QLabel("输入延迟时间范围 (例如: 600,630):", self)
        layout.addWidget(self.delay_label)
        self.delay_input = QLineEdit(self)
        self.delay_input.setText(self.config.get('Settings', 'delay_range'))
        layout.addWidget(self.delay_input)

        # 添加超时时间输入框和标签
        self.timeout_label = QLabel("输入超时时间 (例如: 10):", self)
        layout.addWidget(self.timeout_label)
        self.timeout_input = QLineEdit(self)
        self.timeout_input.setText(self.config.get('Settings', 'timeout'))
        layout.addWidget(self.timeout_input)

        # 添加保存按钮
        self.save_button = QPushButton("保存设置", self)
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        # 添加脚本选择区域
        self.script_group_box = QWidget(self)
        self.script_group_box_layout = QHBoxLayout(self.script_group_box)
        self.script_group_box.setLayout(self.script_group_box_layout)
        layout.addWidget(self.script_group_box)

        # 脚本名称列表
        self.button_names = [
            "旗舰端艺人和种花",
            "通用艺人挂机",
            "旗舰种花",
            "无界种花"
        ]

        # 脚本名称列表
        self.script_names = ["1.py", "2.py", "3.py", "4.py"]

        # 添加脚本选择按钮
        for index, name in enumerate(self.button_names):
            button = QPushButton(name, self)
            button.clicked.connect(lambda checked, script_name=self.script_names[index]: self.run_script(script_name))
            self.script_group_box_layout.addWidget(button)

        # 添加停止按钮
        self.stop_button = QPushButton("停止脚本", self)
        self.stop_button.clicked.connect(self.stop_script)
        layout.addWidget(self.stop_button)

        # 添加文本编辑器用于显示输出
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.text_edit)
        layout.addWidget(scroll_area)

    def save_settings(self):
        delay_range = self.delay_input.text().strip()
        timeout = self.timeout_input.text().strip()

        if not delay_range or not timeout:
            QMessageBox.critical(self, "Error", "请输入所有设置。")
            return

        try:
            min_delay, max_delay = map(int, delay_range.split(','))
            timeout_value = int(timeout)
            self.config.set('Settings', 'delay_range', delay_range)
            self.config.set('Settings', 'timeout', timeout)
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            QMessageBox.information(self, "Success", "设置已成功保存。")
        except ValueError:
            QMessageBox.critical(self, "Error", "无效的设置格式。请检查输入。")

    def run_script(self, script_name):
        delay_range = self.delay_input.text().strip()
        timeout = self.timeout_input.text().strip()

        if not delay_range or not timeout:
            QMessageBox.critical(self, "Error", "请输入所有设置。")
            return

        try:
            min_delay, max_delay = map(int, delay_range.split(','))
            timeout_value = int(timeout)
        except ValueError:
            QMessageBox.critical(self, "Error", "无效的设置格式。请检查输入。")
            return

        self.thread = ScriptExecutionThread(script_name, self.text_edit, min_delay, max_delay, timeout_value)
        self.thread.output_signal.connect(self.update_text_edit)
        self.thread.finished.connect(self.on_thread_finished)
        self.thread.start()

    def stop_script(self):
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
            self.text_edit.append("脚本已停止。")

    def on_thread_finished(self):
        self.text_edit.append("脚本已结束。")

    def update_text_edit(self, output):
        self.text_edit.append(output)
        self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())

class ScriptExecutionThread(QThread):
    output_signal = pyqtSignal(str)

    def __init__(self, script_name, text_edit, min_delay, max_delay, timeout):
        super().__init__()
        self.script_name = script_name
        self.text_edit = text_edit
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.timeout = timeout
        self.running = True
        self.process = None

    def run(self):
        try:
            logging.debug(f"Running script {self.script_name} with delay range {self.min_delay}-{self.max_delay} and timeout {self.timeout}")
            self.process = subprocess.Popen(
                ['python', self.script_name, str(self.min_delay), str(self.max_delay), str(self.timeout)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            while self.running and self.process.poll() is None:
                line = self.process.stdout.readline()
                if line:
                    logging.debug(f"Script output: {line.strip()}")
                    self.output_signal.emit(line.strip())
            self.process.stdout.close()
            self.process.wait()
        except Exception as e:
            logging.error(str(e))
            self.output_signal.emit(f"Error: {str(e)}")

    def stop(self):
        self.running = False
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScriptRunner()
    window.show()
    sys.exit(app.exec())