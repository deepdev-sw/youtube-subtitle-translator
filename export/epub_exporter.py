from ebooklib import epub

class EPUBExporter:
    """
    EPUB导出器，用于导出EPUB格式的电子书
    """
    
    def __init__(self):
        self.css = """body {
    font-family: 'SimSun', 'Songti SC', serif;
    font-size: 16px;
    line-height: 1.6;
    margin: 20px;
    padding: 0;
}

h1 {
    color: #333;
    text-align: center;
    font-size: 24px;
    margin-bottom: 30px;
}

h2 {
    color: #444;
    font-size: 20px;
    margin-top: 30px;
    margin-bottom: 15px;
    border-bottom: 1px solid #ddd;
    padding-bottom: 5px;
}

h3 {
    color: #555;
    font-size: 18px;
    margin-top: 25px;
    margin-bottom: 10px;
}

p {
    margin-bottom: 15px;
    text-indent: 2em;
}

.summary {
    background-color: #f5f5f5;
    padding: 15px;
    border-left: 5px solid #ddd;
    margin: 20px 0;
}

.subtitle {
    margin: 10px 0;
}

.chapter-divider {
    height: 1px;
    background-color: #ddd;
    margin: 30px 0;
}
"""
    
    def export(self, data, output_path):
        """
        导出数据为EPUB格式
        
        参数:
            data: 要导出的数据，包含以下字段:
                - channel_title: 频道标题
                - videos: 视频列表，每个视频包含:
                    - title: 视频标题
                    - summary: 视频摘要
                    - translated_subtitles: 翻译后的字幕
            output_path: 输出文件路径
        """
        # 创建EPUB书籍
        book = epub.EpubBook()
        
        # 设置元数据
        book.set_identifier('youtube-subtitle-translator')
        book.set_title('导出视频字幕')
        book.set_language('zh')
        book.add_author('YouTube Subtitle Translator')
        
        # 添加CSS样式
        style = epub.EpubItem(
            uid="style_default",
            file_name="style/default.css",
            media_type="text/css",
            content=self.css
        )
        book.add_item(style)
        
        # 创建封面页
        cover_html = f"""
        <html>
            <head>
                <title>导出视频字幕</title>
                <link rel="stylesheet" type="text/css" href="style/default.css" />
            </head>
            <body>
                <h1>导出视频字幕</h1>
                <p>这是由YouTube Subtitle Translator生成的电子书。</p>
            </body>
        </html>
        """
        
        cover = epub.EpubHtml(
            title='封面',
            file_name='cover.xhtml',
            lang='zh'
        )
        cover.content = cover_html
        cover.add_item(style)
        book.add_item(cover)
        
        # 创建立目录
        toc = [epub.Link('cover.xhtml', '封面', 'cover')]
        spine = ['cover', 'nav']
        
        # 添加每个视频的章节
        for i, video in enumerate(data.get('videos', [])):
            video_title = video.get('title', '未知标题')
            chapter_id = f'chapter_{i+1}'
            file_name = f'chapters/{chapter_id}.xhtml'
            
            # 生成章节内容
            chapter_content = self._generate_chapter_content(video, i+1)
            
            # 创建章节
            chapter = epub.EpubHtml(
                title=f"视频 {i+1}: {video_title}",
                file_name=file_name,
                lang='zh'
            )
            chapter.content = chapter_content
            chapter.add_item(style)
            book.add_item(chapter)
            
            # 添加到目录和书脊
            toc.append(epub.Link(file_name, f"视频 {i+1}: {video_title}", chapter_id))
            spine.append(chapter)
        
        # 添加导航
        book.toc = toc
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = spine
        
        # 生成EPUB文件
        epub.write_epub(output_path, book, {})
    
    def _generate_chapter_content(self, video, index):
        """
        生成章节内容
        
        参数:
            video: 视频数据
            index: 视频索引
            
        返回:
            str: 章节HTML内容
        """
        video_title = video.get('title', '未知标题')
        summary = video.get('summary', '无摘要')
        
        # 生成字幕HTML
        subtitles_html = ""
        subtitles_html += f"<p class='subtitle'>{video['translated_subtitles']}</p>"
        
        # 生成章节HTML
        html = f"""
        <html>
            <head>
                <title>视频 {index}: {video_title}</title>
                <link rel="stylesheet" type="text/css" href="../style/default.css" />
            </head>
            <body>
                <h2>视频 {index}: {video_title}</h2>
                
                <h3>摘要</h3>
                <div class="summary">
                    <p>{summary}</p>
                </div>
                
                <h3>翻译字幕</h3>
                {subtitles_html}
                
                <div class="chapter-divider"></div>
            </body>
        </html>
        """
        
        return html
    
    def export_single_video(self, video_data, output_path):
        """
        导出单个视频的数据为EPUB格式
        
        参数:
            video_data: 单个视频的数据
            output_path: 输出文件路径
        """
        data = {
            'channel_title': video_data.get('channel_title', '未知频道'),
            'videos': [video_data]
        }
        self.export(data, output_path)
