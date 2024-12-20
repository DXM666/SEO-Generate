import csv
import io
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from .seo_generator import SEOGenerator
from .content_validator import ContentValidator
from ..models.content import ContentModel

class BatchService:
    def __init__(self):
        self.seo_generator = SEOGenerator()
        self.content_validator = ContentValidator()
        self.content_model = ContentModel()
        self.max_workers = 5  # 最大并行处理数

    async def batch_generate(self, keywords_list, content_type='article'):
        """
        批量生成内容
        
        Args:
            keywords_list (list): 关键词列表
            content_type (str): 内容类型
            
        Returns:
            list: 生成的内容列表
        """
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for keywords in keywords_list:
                future = executor.submit(
                    self._generate_single_content,
                    keywords,
                    content_type
                )
                futures.append(future)
            
            for future in futures:
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"生成内容时出错: {str(e)}")
        
        return results

    def _generate_single_content(self, keywords, content_type):
        """生成单个内容"""
        try:
            content = self.seo_generator.generate(keywords, content_type)
            validation = self.content_validator.validate(content)
            
            # 保存到数据库
            save_data = {
                'keywords': keywords,
                'type': content_type,
                'content': content,
                'validation': validation
            }
            content_id = self.content_model.create(save_data)
            
            return {
                'content_id': content_id,
                'keywords': keywords,
                'content': content,
                'validation': validation
            }
        except Exception as e:
            print(f"处理关键词 '{keywords}' 时出错: {str(e)}")
            return None

    def export_contents(self, content_ids=None, format='csv'):
        """
        导出内容
        
        Args:
            content_ids (list): 要导出的内容ID列表，为None时导出所有内容
            format (str): 导出格式，支持'csv'和'json'
            
        Returns:
            tuple: (文件内容, 文件名)
        """
        # 获取内容
        if content_ids:
            contents = [
                self.content_model.get_by_id(content_id)
                for content_id in content_ids
                if self.content_model.get_by_id(content_id)
            ]
        else:
            contents = self.content_model.get_all()
        
        if not contents:
            raise ValueError("没有找到要导出的内容")
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'csv':
            return self._export_to_csv(contents, timestamp)
        elif format == 'json':
            return self._export_to_json(contents, timestamp)
        else:
            raise ValueError("不支持的导出格式")

    def _export_to_csv(self, contents, timestamp):
        """导出为CSV格式"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow([
            '标题', '关键词', '内容类型', 'Meta描述',
            '正文内容', 'SEO得分', '创建时间'
        ])
        
        # 写入内容
        for content in contents:
            writer.writerow([
                content.get('title', ''),
                content.get('keywords', ''),
                content.get('content_type', ''),
                content.get('meta_description', ''),
                content.get('content', ''),
                content.get('seo_score', {}).get('total_score', 0),
                content.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S')
                if content.get('created_at') else ''
            ])
        
        return output.getvalue(), f'seo_contents_{timestamp}.csv'

    def _export_to_json(self, contents, timestamp):
        """导出为JSON格式"""
        # 转换datetime对象为字符串
        contents_copy = []
        for content in contents:
            content_copy = dict(content)
            if 'created_at' in content_copy:
                content_copy['created_at'] = \
                    content_copy['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if 'updated_at' in content_copy:
                content_copy['updated_at'] = \
                    content_copy['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            contents_copy.append(content_copy)
        
        return json.dumps(
            contents_copy,
            ensure_ascii=False,
            indent=2
        ), f'seo_contents_{timestamp}.json'

    def import_keywords_file(self, file_content, file_type='csv'):
        """
        从文件导入关键词
        
        Args:
            file_content (str): 文件内容
            file_type (str): 文件类型，支持'csv'和'txt'
            
        Returns:
            list: 关键词列表
        """
        keywords_list = []
        
        if file_type == 'csv':
            csv_file = io.StringIO(file_content)
            reader = csv.reader(csv_file)
            for row in reader:
                if row and row[0].strip():  # 确保行不为空且第一列有内容
                    keywords_list.append(row[0].strip())
        
        elif file_type == 'txt':
            for line in file_content.split('\n'):
                if line.strip():  # 确保行不为空
                    keywords_list.append(line.strip())
        
        return keywords_list
