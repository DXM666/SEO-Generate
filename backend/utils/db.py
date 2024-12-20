from tinydb import TinyDB, Query
from datetime import datetime
import os

class Database:
    def __init__(self, db_path='data/db.json'):
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db = TinyDB(db_path)
        self.contents = self.db.table('contents')
        self.analytics = self.db.table('analytics')
        self.Query = Query()

    def save_content(self, content_data):
        """保存生成的内容"""
        content_data['created_at'] = datetime.now().isoformat()
        return self.contents.insert(content_data)

    def get_content(self, content_id):
        """获取指定ID的内容"""
        return self.contents.get(doc_id=content_id)

    def get_contents(self, limit=10, skip=0):
        """获取内容列表"""
        all_contents = self.contents.all()
        # 按创建时间排序
        sorted_contents = sorted(
            all_contents,
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )
        return sorted_contents[skip:skip + limit]

    def update_content(self, content_id, updates):
        """更新内容"""
        updates['updated_at'] = datetime.now().isoformat()
        self.contents.update(updates, doc_ids=[content_id])
        return self.get_content(content_id)

    def delete_content(self, content_id):
        """删除内容"""
        self.contents.remove(doc_ids=[content_id])

    def search_contents(self, query_text):
        """搜索内容"""
        # 简单的关键词匹配搜索
        query = self.Query.keywords.search(query_text, flags='i') | \
                self.Query.title.search(query_text, flags='i') | \
                self.Query.content.search(query_text, flags='i')
        return self.contents.search(query)

    def get_analytics(self, start_date=None, end_date=None):
        """获取分析数据"""
        query = self.Query.created_at.exists()
        if start_date:
            query = query & (self.Query.created_at >= start_date)
        if end_date:
            query = query & (self.Query.created_at <= end_date)
        return self.contents.search(query)

    def save_batch_contents(self, contents_list):
        """批量保存内容"""
        timestamp = datetime.now().isoformat()
        for content in contents_list:
            content['created_at'] = timestamp
        return self.contents.insert_multiple(contents_list)

# 创建全局数据库实例
db = Database()
