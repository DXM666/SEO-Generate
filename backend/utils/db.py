from tinydb import TinyDB, Query
from datetime import datetime
import os
import re

class Database:
    def __init__(self, db_path='data/db.json'):
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db = TinyDB(db_path, encoding='utf-8')
        self.contents = self.db.table('contents')
        self.analytics = self.db.table('analytics')
        self.Query = Query()

    def save_content(self, content_data):
        """保存生成的内容"""
        content_data['created_at'] = datetime.now().isoformat()
        return self.contents.insert(content_data)

    def get_content(self, content_id):
        """获取单个内容"""
        try:
            content = self.contents.get(doc_id=int(content_id))
            if content:
                content['id'] = content_id
            return content
        except Exception as e:
            raise Exception(f"获取内容失败: {str(e)}")

    def get_contents(self, limit=10, skip=0, sort_by='created_at', order='desc'):
        """获取内容列表，支持排序和分页"""
        try:
            all_contents = self.contents.all()
            # 为每个内容添加ID
            for content in all_contents:
                content['id'] = content.doc_id
            # 按指定字段排序
            sorted_contents = sorted(
                all_contents,
                key=lambda x: x.get(sort_by, ''),
                reverse=(order.lower() == 'desc')
            )
            # 分页
            paginated = sorted_contents[skip:skip + limit]
            return {
                'items': paginated,
                'total': len(all_contents),
                'page': skip // limit + 1,
                'total_pages': (len(all_contents) + limit - 1) // limit
            }
        except Exception as e:
            raise Exception(f"获取内容列表失败: {str(e)}")

    def update_content(self, content_id, data):
        """更新内容"""
        try:
            self.contents.update(data, doc_ids=[int(content_id)])
            return True
        except Exception as e:
            raise Exception(f"更新内容失败: {str(e)}")

    def delete_content(self, content_id):
        """删除内容"""
        try:
            # 检查内容是否存在
            content = self.get_content(content_id)
            if not content:
                raise Exception("内容不存在")
                
            # 删除内容
            self.contents.remove(doc_ids=[int(content_id)])
            return True
        except Exception as e:
            raise Exception(f"删除内容失败: {str(e)}")

    def search_contents(self, query_text, search_fields=None):
        """增强的搜索功能"""
        try:
            if not search_fields:
                search_fields = ['title', 'meta_description', 'keywords', 'business_type']
            
            all_contents = self.contents.all()
            results = []
            
            for content in all_contents:
                score = 0
                for field in search_fields:
                    value = content.get(field, '')
                    if isinstance(value, list):
                        value = ' '.join(value)
                    if isinstance(value, str):
                        # 计算匹配次数
                        matches = len(re.findall(re.escape(query_text), value, re.I))
                        # 根据字段重要性加权
                        weight = 2.0 if field in ['title', 'keywords'] else 1.0
                        score += matches * weight
                
                if score > 0:
                    content_copy = dict(content)
                    content_copy['relevance'] = score
                    content_copy['id'] = content.doc_id
                    results.append(content_copy)
            
            # 按分数排序
            results.sort(key=lambda x: x['relevance'], reverse=True)
            return results
            
        except Exception as e:
            raise Exception(f"搜索内容失败: {str(e)}")

    def get_analytics(self, start_date=None, end_date=None):
        """获取分析数据"""
        query = self.Query.created_at.exists()
        if start_date:
            query = query & (self.Query.created_at >= start_date)
        if end_date:
            query = query & (self.Query.created_at <= end_date)
        return self.contents.search(query)

    def get_contents_count(self):
        """获取内容总数"""
        return len(self.contents.all())

    def save_batch_contents(self, contents_list):
        """增强的批量保存功能"""
        try:
            # 验证数据格式
            required_fields = ['title', 'meta_description', 'keywords']
            for content in contents_list:
                missing_fields = [field for field in required_fields if field not in content]
                if missing_fields:
                    raise ValueError(f"内容缺少必要字段: {', '.join(missing_fields)}")
            
            # 添加时间戳
            timestamp = datetime.now().isoformat()
            for content in contents_list:
                content['created_at'] = timestamp
                content['updated_at'] = timestamp
            
            # 批量插入
            inserted_ids = self.contents.insert_multiple(contents_list)
            return {
                'success': True,
                'inserted_count': len(inserted_ids),
                'inserted_ids': inserted_ids
            }
            
        except Exception as e:
            raise Exception(f"批量保存失败: {str(e)}")

# 创建全局数据库实例
db = Database()
