from datetime import datetime
from ..utils.db import db

class ContentModel:
    def __init__(self):
        pass

    def create(self, content_data):
        """
        创建新的内容记录
        
        Args:
            content_data (dict): 内容数据，包括生成的内容和元数据
            
        Returns:
            str: 创建的记录ID
        """
        content = Content(
            title=content_data.get('content', {}).get('标题', ''),
            description=content_data.get('content', {}).get('meta描述', ''),
            content=content_data.get('content', {}).get('正文', ''),
            keywords=content_data.get('keywords', ''),
            content_type=content_data.get('type', 'article')
        )
        return content.save()

    def get_all(self, limit=10, skip=0):
        """
        获取所有内容记录
        
        Args:
            limit (int): 每页记录数
            skip (int): 跳过的记录数
            
        Returns:
            list: 内容记录列表
        """
        return Content.get_list(limit, skip)

    def get_by_id(self, content_id):
        """
        根据ID获取内容记录
        
        Args:
            content_id (str): 内容记录ID
            
        Returns:
            dict: 内容记录
        """
        content = Content.get_by_id(content_id)
        if content:
            return content.to_dict()
        return None

    def update(self, content_id, update_data):
        """
        更新内容记录
        
        Args:
            content_id (str): 内容记录ID
            update_data (dict): 更新的数据
            
        Returns:
            bool: 更新是否成功
        """
        content = Content.get_by_id(content_id)
        if content:
            if 'title' in update_data:
                content.title = update_data['title']
            if 'description' in update_data:
                content.description = update_data['description']
            if 'content' in update_data:
                content.content = update_data['content']
            if 'keywords' in update_data:
                content.keywords = update_data['keywords']
            if 'content_type' in update_data:
                content.content_type = update_data['content_type']
            return content.save()
        return False

    def delete(self, content_id):
        """
        删除内容记录
        
        Args:
            content_id (str): 内容记录ID
            
        Returns:
            bool: 删除是否成功
        """
        return db.delete_content(content_id)

    def search(self, keywords, content_type=None, limit=10, skip=0):
        """
        搜索内容记录
        
        Args:
            keywords (str): 搜索关键词
            content_type (str, optional): 内容类型
            limit (int): 每页记录数
            skip (int): 跳过的记录数
            
        Returns:
            list: 搜索结果列表
        """
        return Content.search(keywords)

class Content:
    def __init__(self, title, description, content, keywords, content_type='article', language='en'):
        self.title = title
        self.description = description
        self.content = content
        self.keywords = keywords
        self.content_type = content_type
        self.language = language
        self.created_at = datetime.now().isoformat()

    def to_dict(self):
        """转换为字典格式"""
        return {
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'keywords': self.keywords,
            'content_type': self.content_type,
            'language': self.language,
            'created_at': self.created_at
        }

    def save(self):
        """保存到数据库"""
        return db.save_content(self.to_dict())

    @staticmethod
    def get_by_id(content_id):
        """根据ID获取内容"""
        content_data = db.get_content(content_id)
        if not content_data:
            return None
        return Content(
            title=content_data['title'],
            description=content_data['description'],
            content=content_data['content'],
            keywords=content_data['keywords'],
            content_type=content_data.get('content_type', 'article'),
            language=content_data.get('language', 'en')
        )

    @staticmethod
    def get_list(limit=10, skip=0):
        """获取内容列表"""
        return db.get_contents(limit, skip)

    @staticmethod
    def search(query_text):
        """搜索内容"""
        return db.search_contents(query_text)

    @staticmethod
    def save_batch(contents_list):
        """批量保存内容"""
        content_dicts = [
            Content(
                title=c['title'],
                description=c['description'],
                content=c['content'],
                keywords=c['keywords'],
                content_type=c.get('content_type', 'article'),
                language=c.get('language', 'en')
            ).to_dict()
            for c in contents_list
        ]
        return db.save_batch_contents(content_dicts)
