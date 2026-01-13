from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

class PDFExporter:
    """
    PDF导出器，用于导出PDF格式的结果
    """
    
    def __init__(self):
        # 注册支持中文的字体
        try:
            # 尝试使用系统字体
            font_paths = [
                '/Library/Fonts/Arial Unicode.ttf',  # macOS
                '/Library/Fonts/Songti.ttc',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
                'C:/Windows/Fonts/simhei.ttf',  # Windows
            ]
            
            font_loaded = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    font_loaded = True
                    print(f"成功加载字体: {font_path}")
                    break
            
            if not font_loaded:
                # 如果没有找到系统字体，使用ReportLab的CID字体
                print("使用ReportLab的CID字体")
        except Exception as e:
            print(f"字体加载失败: {e}")
        
        self.styles = getSampleStyleSheet()
        # 自定义样式
        # 确定使用的字体
        if 'ChineseFont' in pdfmetrics.getRegisteredFontNames():
            font_name = 'ChineseFont'
        else:
            # 使用ReportLab的CID字体作为 fallback
            font_name = 'STSong-Light'
        
        self.styles.add(ParagraphStyle(
            name='ChannelTitle',
            parent=self.styles['Heading1'],
            alignment=TA_CENTER,
            spaceAfter=24,
            fontName=font_name
        ))
        
        self.styles.add(ParagraphStyle(
            name='VideoTitle',
            parent=self.styles['Heading2'],
            spaceAfter=12,
            fontName=font_name
        ))
        
        self.styles.add(ParagraphStyle(
            name='SummaryHeading',
            parent=self.styles['Heading3'],
            spaceAfter=6,
            fontName=font_name
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubtitleHeading',
            parent=self.styles['Heading3'],
            spaceAfter=6,
            fontName=font_name
        ))
        
        # Update existing BodyText style instead of adding it again
        self.styles['BodyText'].spaceAfter = 6
        self.styles['BodyText'].leading = 16
        self.styles['BodyText'].fontName = font_name
    
    def export(self, data, output_path):
        """
        导出数据为PDF格式
        
        参数:
            data: 要导出的数据，包含以下字段:
                - channel_title: 频道标题
                - videos: 视频列表，每个视频包含:
                    - title: 视频标题
                    - summary: 视频摘要
                    - translated_subtitles: 翻译后的字幕
            output_path: 输出文件路径
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        
        # 添加每个视频的内容
        for i, video in enumerate(data.get('videos', [])):
            # 视频标题
            video_title = video.get('title', '未知标题')
            story.append(Paragraph(f"视频 {i+1}: {video_title}", self.styles['VideoTitle']))
            
            # 摘要
            story.append(Paragraph("【摘要】", self.styles['SummaryHeading']))
            summary = video.get('summary', '无摘要')
            story.append(Paragraph(summary, self.styles['BodyText']))
            story.append(Spacer(1, 1*cm))
            
            # 翻译后的字幕
            story.append(Paragraph("【翻译字幕】", self.styles['SubtitleHeading']))
            story.append(Paragraph(video['translated_subtitles'], self.styles['BodyText']))
            
            # 添加分页（最后一个视频除外）
            if i < len(data.get('videos', [])) - 1:
                story.append(PageBreak())
            else:
                story.append(Spacer(1, 1*cm))
        
        # 生成PDF
        doc.build(story)
    
    def export_single_video(self, video_data, output_path):
        """
        导出单个视频的数据为PDF格式
        
        参数:
            video_data: 单个视频的数据
            output_path: 输出文件路径
        """
        data = {
            'channel_title': video_data.get('channel_title', '未知频道'),
            'videos': [video_data]
        }
        self.export(data, output_path)
