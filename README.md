# jx3Python-autoGUI
非常粗糙且低性能的剑网3基于Python的自动化脚本，纯图像识别点击
新增了面板程序可以在客户端自由修改延迟
![img.png](img.png)
编译exe执行下面命令
pyinstaller --hidden-import=pygetwindow --onefile main.py
生成的exe不含有图像 需要复制一份images
