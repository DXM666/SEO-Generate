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
        self.SEO_STRUCT = {
            "en":{
                "title": "Best Wireless Headphones 2024 - Buyer's Guide",
                "meta_description": "Check out our 2024 wireless headphones buying guide for the best Bluetooth headsets on the market.",
                "keywords": ["wireless headphones", "best bluetooth earphones", "buyer's guide"],
            },
            "zh":{
                "title": "2024年最好的无线耳机购买指南",
                "meta_description": "了解2024年无线耳机购买指南，了解市场上最好的蓝牙耳机。",
                "keywords": ["无线耳机", "最好的蓝牙耳机", "购买指南"],
            }
        }
        
    @property
    def is_valid(self):
        """检查配置是否有效"""
        return bool(self.HF_TOKEN)
