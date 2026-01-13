from abc import ABC, abstractmethod

class BaseTranslator(ABC):
    """
    翻译器基类，定义翻译器的基本接口
    """
    
    @abstractmethod
    def translate(self, text, source_lang='en', target_lang='zh'):
        """
        翻译文本
        
        参数:
            text: 要翻译的文本
            source_lang: 源语言，默认为英语
            target_lang: 目标语言，默认为中文
            
        返回:
            str: 翻译后的文本
        """
        pass
    
    @abstractmethod
    def translate_batch(self, texts, source_lang='en', target_lang='zh'):
        """
        批量翻译文本
        
        参数:
            texts: 要翻译的文本列表
            source_lang: 源语言，默认为英语
            target_lang: 目标语言，默认为中文
            
        返回:
            list: 翻译后的文本列表
        """
        pass
    
    def set_api_key(self, api_key):
        """
        设置API密钥
        
        参数:
            api_key: API密钥
        """
        self.api_key = api_key
