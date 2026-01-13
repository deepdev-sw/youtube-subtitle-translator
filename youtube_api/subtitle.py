from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter, SRTFormatter

class SubtitleProcessor:
    def __init__(self):
        self.text_formatter = TextFormatter()
        self.srt_formatter = SRTFormatter()
    
    def get_video_transcript(self, video_id, language='en'):
        """
        获取视频的字幕
        
        参数:
            video_id: 视频ID
            language: 字幕语言，默认为英语
            
        返回:
            list: 字幕列表，每个元素包含text, start, duration
        """
        try:
            ytt_api = YouTubeTranscriptApi()
            fetched_transcript = ytt_api.fetch(video_id, languages=[language])
            return fetched_transcript.to_raw_data()
        except Exception as e:
            print(f"获取字幕失败: {e}")
            return None
    
    def get_video_transcript_multiple_languages(self, video_id, languages=['en', 'en-US']):
        """
        尝试从多种语言中获取字幕
        
        参数:
            video_id: 视频ID
            languages: 字幕语言列表，按优先级排序
            
        返回:
            list: 字幕列表，每个元素包含text, start, duration
        """
        try:
            ytt_api = YouTubeTranscriptApi()
            fetched_transcript = ytt_api.fetch(video_id, languages=languages)
            return fetched_transcript.to_raw_data()
        except Exception as e:
            print(f"获取字幕失败: {e}")
            return None
    
    def format_transcript_as_text(self, transcript):
        """
        将字幕格式化为纯文本
        
        参数:
            transcript: 字幕列表
            
        返回:
            str: 格式化后的纯文本
        """
        if not transcript:
            return ""
        return self.text_formatter.format_transcript(transcript)
    
    def format_transcript_as_srt(self, transcript):
        """
        将字幕格式化为SRT格式
        
        参数:
            transcript: 字幕列表
            
        返回:
            str: 格式化后的SRT文本
        """
        if not transcript:
            return ""
        return self.srt_formatter.format_transcript(transcript)
    
    def combine_short_transcripts(self, transcript, min_duration=2.0):
        """
        合并短字幕，提高翻译质量
        
        参数:
            transcript: 字幕列表
            min_duration: 合并后的最小持续时间
            
        返回:
            list: 合并后的字幕列表
        """
        if not transcript:
            return []
        
        combined = []
        current_text = ""
        current_start = transcript[0]['start']
        current_duration = 0
        
        for entry in transcript:
            if current_duration + entry['duration'] < min_duration:
                # 合并当前字幕
                current_text += " " + entry['text'] if current_text else entry['text']
                current_duration += entry['duration']
            else:
                # 保存当前合并的字幕
                combined.append({
                    'text': current_text.strip(),
                    'start': current_start,
                    'duration': current_duration
                })
                # 开始新的合并
                current_text = entry['text']
                current_start = entry['start']
                current_duration = entry['duration']
        
        # 添加最后一个合并的字幕
        if current_text:
            combined.append({
                'text': current_text.strip(),
                'start': current_start,
                'duration': current_duration
            })
        
        return combined
    
    def get_transcript_with_context(self, transcript, context_window=2):
        """
        为每个字幕添加前后上下文，提高翻译质量
        
        参数:
            transcript: 字幕列表
            context_window: 上下文窗口大小
            
        返回:
            list: 带上下文的字幕列表
        """
        if not transcript:
            return []
        
        enhanced_transcript = []
        total_entries = len(transcript)
        
        for i, entry in enumerate(transcript):
            # 获取上下文
            start_idx = max(0, i - context_window)
            end_idx = min(total_entries, i + context_window + 1)
            
            context = " ".join([t['text'] for t in transcript[start_idx:end_idx]])
            
            enhanced_entry = entry.copy()
            enhanced_entry['context'] = context
            enhanced_transcript.append(enhanced_entry)
        
        return enhanced_transcript
