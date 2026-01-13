import os
import time
import openai
from .base_translator import BaseTranslator

class AITranslator(BaseTranslator):
    """
    AI翻译器，支持阿里云百炼和七牛云大模型
    """
    
    def __init__(self, model="dashscope", api_key=None):
        """
        初始化AI翻译器
        
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
    
    def translate(self, text, source_lang='en', target_lang='zh', max_retries=3):
        """
        翻译文本
        
        参数:
            text: 要翻译的文本
            source_lang: 源语言，默认为英语
            target_lang: 目标语言，默认为中文
            max_retries: 最大重试次数
            
        返回:
            str: 翻译后的文本
        """
        if not text:
            return ""
        
        for attempt in range(max_retries):
            try:
                return self._translate_common(text, source_lang, target_lang)
            except Exception as e:
                print(f"翻译失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** (attempt + 1))  # 指数退避
                else:
                    raise
    
    def translate_batch(self, texts, source_lang='en', target_lang='zh', batch_size=5):
        """
        批量翻译文本
        
        参数:
            texts: 要翻译的文本列表
            source_lang: 源语言，默认为英语
            target_lang: 目标语言，默认为中文
            batch_size: 每批处理的文本数量
            
        返回:
            list: 翻译后的文本列表
        """
        translated_texts = []
        
        # 分批处理
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            # 对于所有模型使用统一的批量处理方式
            batch_translations = self._translate_batch_common(batch, source_lang, target_lang)
            translated_texts.extend(batch_translations)
            
            # 避免API速率限制
            time.sleep(1)
        
        return translated_texts
    
    def _translate_common(self, text, source_lang, target_lang):
        """
        通用翻译方法，适用于支持的AI模型
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
                    "content": f"你是一个专业的翻译助手。请将{source_lang}文本翻译成{target_lang}，保持原意准确，语言流畅自然。"
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.3,
        )
        
        return response.choices[0].message.content.strip()
    
    def _translate_batch_common(self, texts, source_lang, target_lang):
        """
        通用批量翻译方法，适用于支持的AI模型
        """
        # 选择合适的模型
        if self.model == "dashscope":
            model = "qwen-plus"  # 阿里云百炼模型
        elif self.model == "qiniu":
            model = "qwen-turbo"  # 七牛云模型
        else:
            model = "qwen-plus"  # 默认模型
        
        responses = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"你是一个专业的翻译助手。请将以下{source_lang}文本翻译成{target_lang}，保持原意准确，语言流畅自然。每个文本单独翻译，用换行符分隔。"
                },
                {
                    "role": "user",
                    "content": "\n".join(texts)
                }
            ],
            temperature=0.3,
        )
        
        translated_text = responses.choices[0].message.content.strip()
        return translated_text.split("\n")
    
    def translate_with_context(self, text, context, source_lang='en', target_lang='zh'):
        """
        带上下文的翻译，提高翻译质量
        
        参数:
            text: 要翻译的文本
            context: 上下文信息
            source_lang: 源语言，默认为英语
            target_lang: 目标语言，默认为中文
            
        返回:
            str: 翻译后的文本
        """
        if not text:
            return ""
        
        # 选择合适的模型
        if self.model == "dashscope":
            model = "qwen-plus"  # 阿里云百炼模型
        elif self.model == "qiniu":
            model = "qwen-turbo"  # 七牛云模型
        else:
            model = "qwen-plus"  # 默认模型
        
        # 构建带上下文的翻译请求
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"你是一个专业的翻译助手。请将{source_lang}文本翻译成{target_lang}，保持原意准确，语言流畅自然。请参考上下文信息以获得更准确的翻译。"
                },
                {
                    "role": "user",
                    "content": f"上下文：{context}\n\n要翻译的文本：{text}"
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
