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
            title=content_data.get('title', ''),
            meta_description=content_data.get('metaDescription', ''),
            keywords=content_data.get('keywords', []),
            business_type=content_data.get('businessType', '')
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
            content.from_dict(update_data)
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

    def search(self, keywords, limit=10, skip=0):
        """
        搜索内容记录
        
        Args:
            keywords (str): 搜索关键词
            limit (int): 每页记录数
            skip (int): 跳过的记录数
            
        Returns:
            list: 搜索结果列表
        """
        return Content.search(keywords, limit)

class Content:
    def __init__(self, title, meta_description, keywords, business_type):
        self.title = title
        self.meta_description = meta_description  # 保持与数据库一致的命名
        self.keywords = keywords
        self.business_type = business_type
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        
    def to_dict(self):
        """转换为字典格式，支持前端的字段命名"""
        return {
            'id': self.id if hasattr(self, 'id') else None,
            'title': self.title,
            'metaDescription': self.meta_description,  # 转换为前端使用的驼峰命名
            'keywords': self.keywords,
            'businessType': self.business_type,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at
        }
        
    def from_dict(self, data):
        """从字典更新对象"""
        self.title = data.get('title', self.title)
        self.meta_description = data.get('metaDescription', self.meta_description)
        self.keywords = data.get('keywords', self.keywords)
        self.business_type = data.get('businessType', self.business_type)
        self.updated_at = datetime.now().isoformat()
        
    def save(self):
        """保存到数据库"""
        data = {
            'title': self.title,
            'meta_description': self.meta_description,
            'keywords': self.keywords,
            'business_type': self.business_type,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        return db.save_content(data)
        
    def update(self, update_data):
        """更新内容"""
        self.from_dict(update_data)
        data = {
            'title': self.title,
            'meta_description': self.meta_description,
            'keywords': self.keywords,
            'business_type': self.business_type,
            'updated_at': datetime.now().isoformat()
        }
        db.update_content(self.id, data)
        return True
        
    @staticmethod
    def get_by_id(content_id):
        """根据ID获取内容"""
        data = db.get_content(content_id)
        if data:
            content = Content(
                title=data.get('title', ''),
                meta_description=data.get('meta_description', ''),
                keywords=data.get('keywords', []),
                business_type=data.get('business_type', '')
            )
            content.created_at = data.get('created_at', '')
            content.updated_at = data.get('updated_at', '')
            content.id = content_id  # 设置ID
            return content
        return None
        
    @staticmethod
    def get_list(limit=10, skip=0, sort_by='created_at', order='desc'):
        """获取内容列表，支持排序"""
        contents_data = db.get_contents(limit, skip)
        contents = [Content.from_db_dict(c) for c in contents_data]
        contents = [c for c in contents if c is not None]  # 过滤掉无效内容
        total = db.get_contents_count()  # 获取总数
        return contents, total
        
    @staticmethod
    def from_db_dict(data):
        """从数据库字典创建对象"""
        if isinstance(data, str):
            return None
        content = Content(
            title=data.get('title', ''),
            meta_description=data.get('meta_description', ''),
            keywords=data.get('keywords', []),
            business_type=data.get('business_type', '')
        )
        content.created_at = data.get('created_at', datetime.now().isoformat())
        content.updated_at = data.get('updated_at', content.created_at)
        content.id = data.get('id', None)
        return content
        
    @staticmethod
    def search(query_text, limit=10):
        """搜索内容，支持分页"""
        results = db.search_contents(query_text)
        # 按相关性排序
        return results[:limit]
        
    @staticmethod
    def save_batch(contents_list):
        """批量保存内容，带错误处理"""
        try:
            db_contents = []
            for content in contents_list:
                if isinstance(content, Content):
                    db_contents.append({
                        'title': content.title,
                        'meta_description': content.meta_description,
                        'keywords': content.keywords,
                        'business_type': content.business_type,
                        'created_at': content.created_at,
                        'updated_at': content.updated_at
                    })
                else:
                    # 如果是字典格式
                    db_contents.append({
                        'title': content.get('title', ''),
                        'meta_description': content.get('metaDescription', ''),
                        'keywords': content.get('keywords', []),
                        'business_type': content.get('businessType', ''),
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    })
            return db.save_batch_contents(db_contents)
        except Exception as e:
            raise Exception(f"批量保存失败: {str(e)}")

    @staticmethod
    def delete(content_id):
        """删除内容"""
        try:
            db.delete_content(content_id)
            return True
        except Exception as e:
            raise Exception(f"删除内容失败: {str(e)}")
