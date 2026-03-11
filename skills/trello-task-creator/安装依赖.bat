@echo off
echo 正在安装Trello任务创建工具依赖...
pip install requests xmindparser
echo.
echo 依赖安装完成！
echo 请先配置 references/config.json 文件，填写你的Trello密钥信息
echo 配置完成后即可使用
pause
