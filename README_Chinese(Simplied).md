# Apple Music To MP3 ![](https://camo.githubusercontent.com/78f47a09877ba9d28da1887a93e5c3bc2efb309c1e910eb21135becd2998238a/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c6963656e73652d4d49542d79656c6c6f772e737667)
一个开源的下载工具，能够帮助您将Apple Music 播放列表中的音乐文件以MP3格式下载。通常拥有高达95%的准确率.
# 依赖
需要安装`youtube-dl`库。如果您的电脑支持pip包管理器，您可以使用`pip install youtube-dl`进行安装。

有时需要使用`ffmpeg`
# 使用步骤  

1.将您的Apple Music 播放列表导出为`xml`文件，步骤如下：

    打开iTunes/Apple Music ，前往 文件->资料库->导出资料库，将导出的`xml`文件保存在该项目文件夹下
2.运行`main.py`