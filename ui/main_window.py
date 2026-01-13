import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from youtube_api import ChannelProcessor, SubtitleProcessor
from translation import AITranslator
from summarization import AISummarizer
from export import TextExporter, PDFExporter, EPUBExporter
import threading
import time

class MainWindow:
    """
    主窗口类，使用customtkinter创建现代化的UI界面
    """
    
    def __init__(self):
        # 设置主题
        ctk.set_appearance_mode("System")  # 可选: "System", "Light", "Dark"
        ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"
        
        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("YouTube字幕翻译工具")
        self.root.geometry("1200x800")
        
        # 初始化处理器
        self.channel_processor = ChannelProcessor()
        self.subtitle_processor = SubtitleProcessor()
        self.translator = None
        self.summarizer = None
        
        # 初始化导出器
        self.text_exporter = TextExporter()
        self.pdf_exporter = PDFExporter()
        self.epub_exporter = EPUBExporter()
        
        # 数据存储
        self.processed_data = {
            'videos':[]
        }
        self.current_video_index = 0
        self.is_stop = False
        
        # 创建UI组件
        self._create_widgets()
        
    def _create_widgets(self):
        """
        创建UI组件
        """
        # 主框架
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 顶部输入区域
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        ctk.CTkLabel(input_frame, text="YouTube频道URL:", font=ctk.CTkFont(size=14)).pack(side=tk.LEFT, padx=10, pady=10)
        self.url_entry = ctk.CTkEntry(input_frame, placeholder_text="输入YouTube频道或播放列表URL", width=600)
        self.url_entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        
        # 配置区域
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.pack(fill=tk.X, pady=10)
        
        # AI模型选择
        model_frame = ctk.CTkFrame(config_frame)
        model_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        ctk.CTkLabel(model_frame, text="AI模型:", font=ctk.CTkFont(size=12)).pack(side=tk.LEFT, padx=5)
        self.model_var = ctk.StringVar(value="qiniu")
        model_dropdown = ctk.CTkOptionMenu(model_frame, variable=self.model_var, values=["dashscope", "qiniu"])
        model_dropdown.pack(side=tk.LEFT, padx=5)
        
        # API密钥输入
        api_frame = ctk.CTkFrame(config_frame)
        api_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        ctk.CTkLabel(api_frame, text="API密钥:", font=ctk.CTkFont(size=12)).pack(side=tk.LEFT, padx=5)
        self.api_key_entry = ctk.CTkEntry(api_frame, placeholder_text="输入API密钥", show="*", width=300)
        self.api_key_entry.pack(side=tk.LEFT, padx=5)
        
        # 导出格式选择
        export_frame = ctk.CTkFrame(config_frame)
        export_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        ctk.CTkLabel(export_frame, text="导出格式:", font=ctk.CTkFont(size=12)).pack(side=tk.LEFT, padx=5)
        self.export_format_var = ctk.StringVar(value="txt")
        export_dropdown = ctk.CTkOptionMenu(export_frame, variable=self.export_format_var, values=["txt", "pdf", "epub"])
        export_dropdown.pack(side=tk.LEFT, padx=5)
        
        # 控制按钮区域
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ctk.CTkButton(button_frame, text="开始翻译", command=self._start_processing, font=ctk.CTkFont(size=14), width=150)
        self.start_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.stop_button = ctk.CTkButton(button_frame, text="停止处理", command=self._stop_processing, font=ctk.CTkFont(size=14), width=150)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.stop_button.configure(state=tk.DISABLED)
        
        self.export_button = ctk.CTkButton(button_frame, text="导出结果", command=self._export_results, font=ctk.CTkFont(size=14), width=150)
        self.export_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.export_button.configure(state=tk.DISABLED)
        
        self.clear_button = ctk.CTkButton(button_frame, text="清空结果", command=self._clear_results, font=ctk.CTkFont(size=14), width=150)
        self.clear_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.clear_button.configure(state=tk.DISABLED)

        
        # 进度显示区域
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="准备就绪", font=ctk.CTkFont(size=12))
        self.progress_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        self.progress_bar.set(0)
        
        # 结果显示区域
        result_frame = ctk.CTkFrame(main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 左侧视频列表
        left_frame = ctk.CTkFrame(result_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        ctk.CTkLabel(left_frame, text="视频列表", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.video_listbox = tk.Listbox(left_frame, width=40, height=20, font=ctk.CTkFont(size=12))
        self.video_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.video_listbox.bind("<<ListboxSelect>>", self._on_video_select)
        
        # 右侧内容显示
        right_frame = ctk.CTkFrame(result_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 摘要显示
        summary_label = ctk.CTkLabel(right_frame, text="视频摘要", font=ctk.CTkFont(size=14, weight="bold"))
        summary_label.pack(pady=10)
        
        self.summary_text = ctk.CTkTextbox(right_frame, height=150, font=ctk.CTkFont(size=12))
        self.summary_text.pack(fill=tk.X, pady=10, padx=10)
        self.summary_text.configure(state=tk.DISABLED)
        
        # 字幕显示
        subtitle_label = ctk.CTkLabel(right_frame, text="翻译字幕", font=ctk.CTkFont(size=14, weight="bold"))
        subtitle_label.pack(pady=10)
        
        self.subtitle_text = ctk.CTkTextbox(right_frame, font=ctk.CTkFont(size=12))
        self.subtitle_text.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        self.subtitle_text.configure(state=tk.DISABLED)
        
    def _start_processing(self):
        
        """
        开始处理YouTube频道
        """
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("错误", "请输入YouTube频道或播放列表URL")
            return
        
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("错误", "请输入API密钥")
            return
        
        model = self.model_var.get()
        if not model:
            messagebox.showerror("错误", "请选择模型")
            return

         # 清空之前的结果
        # self._clear_results()
        
        # 初始化翻译器和摘要生成器（只支持阿里云百炼）
        # self.translator = AITranslator(api_key=api_key, model=model)
        # self.summarizer = AISummarizer(api_key=api_key, model=model)
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.export_button.configure(state=tk.DISABLED)
        self.clear_button.configure(state=tk.DISABLED)
        
        # 在新线程中处理，避免阻塞UI
        threading.Thread(target=self._process_channel, args=(url, api_key, model, self._update_status_progress, self._receive_video, self._finish_process)).start()

    def _update_status_progress(self, status, progress):
        """
        更新状态和进度条
        """
        self._update_status(status)
        self._update_progress(progress)

    def _receive_video(self, video):
        """
        接收处理后的视频数据
        """
        self.processed_data['videos'].append(video)
        self.root.after(0, self._add_video_to_list, video['title'])

    def _finish_process(self):
        """
        处理完成后更新UI
        """
        self.is_stop = False
        self.root.after(0, lambda: self.stop_button.configure(text="停止处理"))
        self.root.after(0, lambda: self.start_button.configure(state=tk.DISABLED))
        self.root.after(0, lambda: self.stop_button.configure(state=tk.DISABLED))
        self.root.after(0, lambda: self.export_button.configure(state=tk.NORMAL))   
        self.root.after(0, lambda: self.clear_button.configure(state=tk.NORMAL))   
        
    def _process_channel(self, url, api_key, model, status_progress_updater, video_receiver, finish_callback):
        """
        处理YouTube频道、播放列表或单个视频
        """
        progress = 0.1
        try:
            if self.is_stop:
                return
            # 1. 获取URL类型和ID
            status_progress_updater("正在分析URL...", progress)

            channel_processor = ChannelProcessor()
            subtitle_processor = SubtitleProcessor()
            translator = AITranslator(api_key=api_key, model=model)
            summarizer = AISummarizer(api_key=api_key, model=model)
            
            url_type, id = channel_processor.get_url_type_and_id(url)
            
            # 根据URL类型获取视频列表
            if self.is_stop:
                return
            status_progress_updater(f"正在获取{url_type}信息...", progress)
            videos = channel_processor.get_channel_videos(id, url_type)
            
            if not videos:
                if self.is_stop:
                    return
                status_progress_updater("未找到视频", progress)
                return
            
            # 保存处理数据

            # 2. 处理每个视频
            total_videos = len(videos)
            for i, video in enumerate(videos):
                progress = 0.1 + (i / total_videos) * 0.8
                if self.is_stop:
                    return
                status_progress_updater(f"正在处理视频 {i+1}/{total_videos}: {video['title']}", progress)
                
                # 获取字幕
                transcript = subtitle_processor.get_video_transcript_multiple_languages(video['video_id'])
                if not transcript:
                    continue
                
                # 合并所有字幕为一个整体，提高翻译质量
                # 首先收集所有字幕文本
                full_text = ""
                for entry in transcript:
                    full_text += entry['text'] + "\n"
                
                # 一次性翻译整个文本
                translated_full_text = translator.translate(full_text)
                
                # 生成摘要
                summary = summarizer.summarize(translated_full_text, max_length=300)
                
                # 保存处理结果
                processed_video = video.copy()
                processed_video['translated_subtitles'] = translated_full_text
                processed_video['summary'] = summary
                # 保存处理数据
                # self.processed_data['videos'].append(processed_video)
                
                # 发送处理后的视频数据
                video_receiver(processed_video)
                
                # 更新视频列表
                # self.root.after(0, self._add_video_to_list, processed_video['title'], i)
            
            # 3. 完成处理
            progress = 1.0
            if self.is_stop:
                return
            status_progress_updater(f"处理完成，共处理 {total_videos} 个视频", progress)
            
        except Exception as e:
            status_progress_updater(f"处理失败: {str(e)}", progress)
            messagebox.showerror("错误", f"处理失败: {str(e)}")
        finally:
            finish_callback()
    
    def _update_status(self, status):
        """
        更新状态信息
        """
        self.root.after(0, lambda: self.progress_label.configure(text=status))
    
    def _update_progress(self, value):
        """
        更新进度条
        """
        self.root.after(0, lambda: self.progress_bar.set(value))
    
    def _add_video_to_list(self, title):
        """
        添加视频到列表
        """
        self.video_listbox.insert(tk.END, title)
    
    def _on_video_select(self, event):
        """
        处理视频列表选择事件
        """
        selection = self.video_listbox.curselection()
        if selection:
            index = selection[0]
            self._display_video(index)
    
    def _display_video(self, index):
        """
        显示选中视频的内容
        """
        if not self.processed_data or index >= len(self.processed_data['videos']):
            return
        
        video = self.processed_data['videos'][index]
        
        # 显示摘要
        self.summary_text.configure(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, video['summary'])
        self.summary_text.configure(state=tk.DISABLED)
        
        # 显示字幕
        self.subtitle_text.configure(state=tk.NORMAL)
        self.subtitle_text.delete(1.0, tk.END)
        self.subtitle_text.insert(tk.END, video['translated_subtitles'])
        self.subtitle_text.configure(state=tk.DISABLED)
        
        # 更新当前视频索引
        self.current_video_index = index
        
    def _export_results(self):
        """
        导出结果
        """
        if not len(self.processed_data['videos']):
            messagebox.showerror("错误", "没有可导出的结果")
            return
        
        # 选择导出格式
        export_format = self.export_format_var.get()
        if not export_format:
            messagebox.showerror('错误', '未选择导出模式')
            return
        

        # 选择保存路径
        file_types = {
            "txt": ["文本文件", "*.txt"],
            "pdf": ["PDF文件", "*.pdf"],
            "epub": ["EPUB电子书", "*.epub"]
        }
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{export_format}",
            filetypes=[file_types[export_format]],
            title=f"导出为{file_types[export_format][0]}"
        )
        
        if not file_path:
            return
        
        self.export_button.configure(state=tk.DISABLED)

        try:
            # 导出结果
            self._update_status(f"正在导出 {export_format} 文件...")
            
            if export_format == "txt":
                self.text_exporter.export(self.processed_data, file_path)
            elif export_format == "pdf":
                self.pdf_exporter.export(self.processed_data, file_path)
            elif export_format == "epub":
                self.epub_exporter.export(self.processed_data, file_path)
            
            self._update_status(f"导出成功: {file_path}")
            messagebox.showinfo("成功", f"文件已导出到: {file_path}")
        except Exception as e:
            self._update_status(f"导出失败: {str(e)}")
            messagebox.showerror("错误", f"导出失败: {str(e)}")
        finally:
            self.export_button.configure(state=tk.NORMAL)
    
    def _stop_processing(self):
        """
        停止处理
        """
        self.is_stop=True
        self.stop_button.configure(state=tk.DISABLED)
        # 停止按钮显示为停止中
        self.stop_button.configure(text="停止中")
    
    def _clear_results(self):
        """
        清空结果
        """
        # 清空视频列表
        self.video_listbox.delete(0, tk.END)
        
        # 清空摘要和字幕显示
        self.summary_text.configure(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.configure(state=tk.DISABLED)
        
        self.subtitle_text.configure(state=tk.NORMAL)
        self.subtitle_text.delete(1.0, tk.END)
        self.subtitle_text.configure(state=tk.DISABLED)
        
        # 重置进度
        self._update_status_progress("准备就绪", 0)
        self.root.after(0, lambda: self.export_button.configure(state=tk.DISABLED))
        self.root.after(0, lambda: self.stop_button.configure(state=tk.DISABLED))
        self.root.after(0, lambda: self.start_button.configure(state=tk.NORMAL))
        self.root.after(0, lambda: self.clear_button.configure(state=tk.DISABLED))
        
        # 清空数据
        self.processed_data = {
            'videos': []
        }
        self.current_video_index = 0
        
    
    def run(self):
        """
        运行主窗口
        """
        self.root.mainloop()
