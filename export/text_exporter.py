class TextExporter:
    """
    文本导出器，用于导出TXT格式的结果
    """
    
    def export(self, data, output_path):
        """
        导出数据为TXT格式
        
        参数:
            data: 要导出的数据，包含以下字段:
                - channel_title: 频道标题
                - videos: 视频列表，每个视频包含:
                    - title: 视频标题
                    - summary: 视频摘要
                    - translated_subtitles: 翻译后的字幕
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            # 写入每个视频的内容
            for i, video in enumerate(data.get('videos', []), 1):
                f.write(f"视频 {i}: {video.get('title', '未知标题')}\n")
                f.write("-" * 50 + "\n")
                
                # 写入摘要
                f.write("【摘要】\n")
                f.write(f"{video.get('summary', '无摘要')}\n\n")
                
                # 写入翻译后的字幕
                f.write("【翻译字幕】\n")
                f.write(f"{video['translated_subtitles']}\n")
                
                f.write("\n" + "=" * 50 + "\n\n")
    
    def export_single_video(self, video_data, output_path):
        """
        导出单个视频的数据为TXT格式
        
        参数:
            video_data: 单个视频的数据
            output_path: 输出文件路径
        """
        data = {
            'channel_title': video_data.get('channel_title', '未知频道'),
            'videos': [video_data]
        }
        self.export(data, output_path)
