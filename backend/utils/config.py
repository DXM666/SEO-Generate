import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        
        # 数据库配置
        self.DB_PATH = os.getenv('DB_PATH', 'data/db.json')
        
        # Hugging Face token
        self.HF_TOKEN = os.getenv('HF_TOKEN')
        
        # Razor配置
        self.TEXTRAZOR_API_KEY = os.getenv('TEXTRAZOR_API_KEY')

        
        # 其他配置
        self.MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1500'))
        self.TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
        
        # SEO配置
        self.SEO_CONFIG = {
            'title': {
                'min': 30,    # 最小标题长度
                'max': 60     # 最大标题长度
            },
            'description': {
                'min': 150,   # 最小描述长度
                'max': 160    # 最大描述长度
            },
            'content': {
                'min': 300,   # 最小内容长度
                'max': 3000   # 最大内容长度
            }
        }
        
    @property
    def is_valid(self):
        """检查配置是否有效"""
        return bool(self.HF_TOKEN)
