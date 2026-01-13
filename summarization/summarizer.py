import time
import openai

class AISummarizer:
    """
    AI摘要生成器，支持阿里云百炼和七牛云大模型
    """
    
    def __init__(self, model="dashscope", api_key=None):
        """
        初始化AI摘要生成器
        
        参数:
            model: 使用的AI模型，可选值: "dashscope"(阿里云百炼), "qiniu"(七牛云)
            api_key: API密钥
        """
        self.model = model
        self.api_key = api_key
        self.client = None
        
        # 初始化AI客户端
        if api_key:
            self._init_client()
    
    def _init_client(self):
        """
        初始化AI客户端
        """
        if self.model == "dashscope":
            # 阿里云百炼使用OpenAI兼容API
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
        elif self.model == "qiniu":
            # 七牛云使用OpenAI兼容API
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.qnaigc.com/v1"
            )
    
    def set_model(self, model):
        """
        设置使用的AI模型
        
        参数:
            model: 使用的AI模型，可选值: "dashscope"(阿里云百炼), "qiniu"(七牛云)
        """
        self.model = model
        # 如果已初始化，重新初始化客户端
        if self.api_key:
            self._init_client()
    
    def summarize(self, text, max_length=200, max_retries=3):
        """
        生成文本摘要
        
        参数:
            text: 要生成摘要的文本
            max_length: 摘要的最大长度
            max_retries: 最大重试次数
            
        返回:
            str: 生成的摘要
        """
        if not text:
            return ""
        
        for attempt in range(max_retries):
            try:
                return self._summarize_common(text, max_length)
            except Exception as e:
                print(f"生成摘要失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** (attempt + 1))  # 指数退避
                else:
                    raise
    
    def summarize_long_text(self, text, max_length=300, chunk_size=2000):
        """
        生成长文本摘要，通过分块处理
        
        参数:
            text: 要生成摘要的长文本
            max_length: 摘要的最大长度
            chunk_size: 每块文本的大小
            
        返回:
            str: 生成的摘要
        """
        if not text:
            return ""
        
        # 将长文本分成块
        chunks = self._split_text(text, chunk_size)
        
        # 生成每块的摘要
        chunk_summaries = []
        for chunk in chunks:
            chunk_summary = self.summarize(chunk, max_length=max_length // len(chunks))
            chunk_summaries.append(chunk_summary)
        
        # 生成最终摘要
        combined_summary = "\n".join(chunk_summaries)
        final_summary = self.summarize(combined_summary, max_length=max_length)
        
        return final_summary
    
    def generate_chapter_summary(self, chapters, max_length=150):
        """
        生成章节摘要
        
        参数:
            chapters: 章节列表，每个章节包含title和content
            max_length: 每个章节摘要的最大长度
            
        返回:
            list: 章节摘要列表
        """
        chapter_summaries = []
        
        for chapter in chapters:
            summary = self.summarize(chapter["content"], max_length=max_length)
            chapter_summaries.append({
                "title": chapter["title"],
                "summary": summary
            })
        
        return chapter_summaries
    
    def _summarize_common(self, text, max_length):
        """
        通用摘要生成方法，适用于支持的AI模型
        """
        # 选择合适的模型
        if self.model == "dashscope":
            model = "qwen-plus"  # 阿里云百炼模型
        elif self.model == "qiniu":
            model = "qwen-turbo"  # 七牛云模型
        else:
            model = "qwen-plus"  # 默认模型
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的摘要生成助手。请根据以下文本生成简洁、准确、流畅的中文摘要，突出重点内容。"
                },
                {
                    "role": "user",
                    "content": f"请为以下文本生成不超过{max_length}字的中文摘要：\n{text}"
                }
            ],
            temperature=0.3,
        )
        
        return response.choices[0].message.content.strip()
    
    def _split_text(self, text, chunk_size):
        """
        将文本分成指定大小的块
        
        参数:
            text: 要分块的文本
            chunk_size: 每块文本的大小
            
        返回:
            list: 分块后的文本列表
        """
        chunks = []
        current_chunk = ""
        
        paragraphs = text.split("\n")
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 1 < chunk_size:
                current_chunk += paragraph + "\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
