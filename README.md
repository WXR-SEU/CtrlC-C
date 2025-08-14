
运行库：conda install pyinstaller keyboard pystray pillow pywin32 -y

打包exe：pyinstaller --onefile --noconsole --name CtrlC-C --icon ctrlcc.ico --add-data "ctrlcc.ico;." ctrlcc.py

## 更新日志
* 2025-08-14：优化性能，只兼容Windows
