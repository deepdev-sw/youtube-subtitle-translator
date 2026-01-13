# YouTube字幕翻译工具主程序入口

from ui import MainWindow

def main():
    """
    主函数，启动应用程序
    """
    # 创建主窗口实例
    app = MainWindow()
    # 运行主窗口
    app.run()

if __name__ == "__main__":
    main()
