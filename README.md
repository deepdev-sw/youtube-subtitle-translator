# YouTube字幕翻译工具

YouTube字幕翻译工具是一款功能强大的应用程序，用于批量获取YouTube频道或播放列表中的视频字幕，并使用AI模型进行翻译和摘要生成，最终支持多种格式导出。

## 功能特点

- **支持多种YouTube内容**：可处理单个视频、播放列表或整个频道
- **AI智能翻译**：集成多种AI模型，提供高质量字幕翻译
- **自动摘要生成**：为每个视频生成简洁的内容摘要
- **多格式导出**：支持TXT、PDF、EPUB等多种格式导出
- **直观的用户界面**：现代化的UI设计，易于操作
- **进度实时显示**：清晰的进度条和状态提示
- **支持中断处理**：可随时停止正在进行的处理任务

## 技术架构

### 项目结构

```
youtube_subtitle_translator/
├── export/              # 导出功能模块
│   ├── __init__.py
│   ├── epub_exporter.py  # EPUB格式导出
│   ├── pdf_exporter.py   # PDF格式导出
│   └── text_exporter.py  # 文本格式导出
├── summarization/       # 摘要生成模块
│   ├── __init__.py
│   └── summarizer.py     # AI摘要生成器
├── translation/         # 翻译功能模块
│   ├── __init__.py
│   ├── ai_translator.py  # AI翻译器
│   └── base_translator.py # 翻译基类
├── ui/                  # 用户界面模块
│   ├── __init__.py
│   └── main_window.py    # 主窗口设计
├── youtube_api/         # YouTube API交互模块
│   ├── __init__.py
│   ├── channel.py        # 频道处理
│   └── subtitle.py       # 字幕处理
├── main.py              # 主程序入口
└── requirements.txt      # 项目依赖
```

### 核心依赖

| 依赖库 | 用途 | 版本要求 |
|-------|------|---------|
| youtube-transcript-api | 获取YouTube视频字幕 | >=0.5.0 |
| pytube3 | YouTube视频信息获取 | >=9.6.4 |
| openai | AI模型API访问 | >=1.0.0 |
| requests | HTTP请求处理 | >=2.31.0 |
| customtkinter | 现代化UI界面 | >=5.2.1 |
| ebooklib | EPUB格式导出 | >=0.17.1 |
| reportlab | PDF格式导出 | >=4.0.8 |
| beautifulsoup4 | HTML解析 | >=4.12.2 |
| python-dotenv | 环境变量管理 | >=1.0.0 |

## 安装与运行

### 1. 克隆项目

```bash
git clone <项目地址>
cd youtube_subtitle_translator
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行程序

```bash
python main.py
```

## 使用指南

### 1. 界面介绍

程序启动后，您将看到如下界面：

- **顶部输入区域**：用于输入YouTube频道或播放列表URL
- **配置区域**：
  - AI模型选择：支持dashscope和qiniu两种模型
  - API密钥输入：输入您的AI模型API密钥
  - 导出格式选择：选择最终导出的文件格式（TXT、PDF、EPUB）
- **控制按钮区域**：
  - 开始翻译：启动字幕翻译和摘要生成任务
  - 停止处理：中断正在进行的任务
  - 导出结果：将处理结果导出为选定格式
  - 清空结果：清除当前所有处理结果
- **进度显示区域**：显示当前任务状态和进度条
- **结果显示区域**：
  - 左侧视频列表：显示处理完成的视频
  - 右侧内容区：显示选中视频的摘要和翻译字幕

### 2. 使用步骤

#### 步骤1：准备工作

1. 确保您已获取有效的AI模型API密钥（dashscope或qiniu）
2. 准备好要处理的YouTube频道或播放列表URL

#### 步骤2：配置参数

1. 在"YouTube频道URL"输入框中输入您要处理的YouTube频道或播放列表URL
2. 在"API密钥"输入框中输入您的AI模型API密钥
3. 从"AI模型"下拉菜单中选择您要使用的AI模型
4. （可选）从"导出格式"下拉菜单中选择您想要的导出格式

#### 步骤3：开始处理

1. 点击"开始翻译"按钮
2. 观察进度条和状态提示，了解处理进度
3. 处理过程中可以随时点击"停止处理"按钮中断任务

#### 步骤4：查看结果

1. 处理完成后，左侧视频列表将显示所有已处理的视频
2. 点击视频列表中的任意视频，右侧将显示该视频的摘要和翻译字幕
3. 您可以在右侧内容区查看完整的翻译字幕

#### 步骤5：导出结果

1. 确保已选择合适的导出格式
2. 点击"导出结果"按钮
3. 在弹出的文件保存对话框中选择保存路径和文件名
4. 点击"保存"按钮，等待导出完成
5. 导出成功后，您将看到提示信息

### 3. 功能详解

#### YouTube内容支持

- **单个视频**：直接输入YouTube视频URL，例如：https://www.youtube.com/watch?v=XRpHIa-2XCE&
- **播放列表**：输入YouTube播放列表URL, 例如：https://www.youtube.com/playlist?list=PLAqhIrjkxbuW1-qwe-JcXjt7hqfIyRgUk
- **整个频道**：输入YouTube频道首页URL, 例如：https://www.youtube.com/@AndrejKarpathy

#### AI模型选择

- **qiniu**：使用七牛云AI模型

- **dashscope**：使用阿里云百炼AI模型

- **如何获取API密钥？**
  请访问相应AI模型提供商的官方网站注册并获取API密钥：
  qiniu（七牛云）：https://s.qiniu.com/Iv6vM3
  dashscope（阿里云百炼）：https://bailian.console.aliyun.com/#/home

#### 导出格式说明

- **TXT**：纯文本格式，适合简单阅读和编辑
- **PDF**：便携式文档格式，适合打印和跨平台阅读
- **EPUB**：电子书格式，适合在电子书阅读器上阅读

## 常见问题

### 1. 为什么处理速度很慢？

处理速度取决于以下因素：
- 视频数量：视频越多，处理时间越长
- 视频长度：长视频字幕内容更多，处理时间更长
- 网络状况：需要从YouTube获取字幕，网络延迟会影响速度
- AI模型响应速度：不同AI模型的响应速度不同

### 2. 为什么有些视频没有字幕？

可能的原因：
- 该视频没有生成字幕
- 字幕格式不被支持
- 网络问题导致字幕获取失败

### 3. 如何获取API密钥？

请访问相应AI模型提供商的官方网站注册并获取API密钥：
- qiniu（七牛云）：https://s.qiniu.com/Iv6vM3
- dashscope（阿里云百炼）：https://bailian.console.aliyun.com/#/home

### 4. 导出结果中包含什么内容？

导出结果包含：
- 视频标题
- 视频摘要
- 翻译后的完整字幕

## 注意事项

1. 请确保您的API密钥有效且有足够的配额
2. 处理大量视频时，建议分批处理
3. 长时间处理可能会导致程序无响应，这是正常现象，请耐心等待
4. 导出大型PDF或EPUB文件时，可能需要较长时间
5. 请遵守YouTube的服务条款和版权规定
6. 请遵守AI模型提供商的使用条款
7. python版本需要使用python3
8. 需要能翻墙，访问youtube

## 更新日志

### v1.0.0
- 初始版本发布
- 支持YouTube频道、播放列表和单个视频处理
- 集成dashscope和qiniu AI模型
- 支持TXT、PDF、EPUB格式导出
- 提供现代化UI界面

## 许可证

本项目采用MIT许可证，详情请查看LICENSE文件。

---

**免责声明**：本工具仅用于学习和研究目的，请遵守相关法律法规和平台服务条款。
