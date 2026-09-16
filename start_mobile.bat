@echo off
chcp 65001 >nul
title 3000单词手机朗读服务
echo ========================================================
echo   📱 英语 3000 单词朗读 - 手机局域网服务
echo ========================================================
echo.
echo 正在获取局域网 IP 地址并启动服务...
echo.
python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); (s.connect(('8.8.8.8', 80)), print('\n👉 手机浏览器（Safari / Chrome）直接访问网址:\n   http://' + s.getsockname()[0] + ':8000\n'), s.close()) if True else None"
echo.
echo [提示] 手机和电脑需连接在同一个 Wi-Fi 热点或路由器下。
echo [提示] 网页打开后可点击浏览器的【添加到主屏幕】，像 App 一样全屏使用。
echo.
echo 按 Ctrl + C 即可关闭服务。
echo ========================================================
python -m http.server 8000 --bind 0.0.0.0
pause
