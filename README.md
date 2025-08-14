
运行库：conda install pyinstaller keyboard pystray pillow pywin32 -y

打包exe：pyinstaller --onefile --noconsole --name CtrlC-C --icon ctrlcc.ico --add-data "ctrlcc.ico;." ctrlcc.py

## 更新日志

* 2023-11-08：上传项目。发布 CtrlC-C v2023.11.8 版本。
* 2023-11-09：增加快捷键冲突检测功能；增加开机自启功能；增加程序重复开启检测功能。发布 CtrlC-C v2023.11.9 版本
* 2023-12-10：增加日志记录功能。发布 CtrlC-C v2023.12.10 版本
* 2024-03-16：增加删除空格功能。
* 2025-08-14：优化性能，只兼容Windows
