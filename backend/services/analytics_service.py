from datetime import datetime, timedelta
from ..models.content import ContentModel

class AnalyticsService:
    def __init__(self):
        self.content_model = ContentModel()

    def get_content_stats(self, days=30):
        """
        获取内容统计数据
        
        Args:
            days (int): 统计天数
            
        Returns:
            dict: 统计数据
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取所有内容
        contents = self.content_model.collection.find({
            'created_at': {'$gte': start_date}
        })
        
        # 初始化统计数据
        stats = {
            'total_content': 0,
            'content_types': {
                'article': 0,
                'product': 0
            },
            'average_seo_score': 0,
            'keyword_distribution': {},
            'daily_generation': {},
            'score_distribution': {
                '90-100': 0,
                '80-89': 0,
                '70-79': 0,
                '60-69': 0,
                'below-60': 0
            }
        }
        
        total_score = 0
        
        for content in contents:
            # 总数统计
            stats['total_content'] += 1
            
            # 内容类型统计
            content_type = content.get('content_type', 'article')
            stats['content_types'][content_type] += 1
            
            # SEO得分统计
            seo_score = content.get('seo_score', {}).get('total_score', 0)
            total_score += seo_score
            
            # 得分分布
            if seo_score >= 90:
                stats['score_distribution']['90-100'] += 1
            elif seo_score >= 80:
                stats['score_distribution']['80-89'] += 1
            elif seo_score >= 70:
                stats['score_distribution']['70-79'] += 1
            elif seo_score >= 60:
                stats['score_distribution']['60-69'] += 1
            else:
                stats['score_distribution']['below-60'] += 1
            
            # 关键词分布
            keywords = content.get('keywords', '').split(',')
            for keyword in keywords:
                keyword = keyword.strip()
                if keyword:
                    stats['keyword_distribution'][keyword] = \
                        stats['keyword_distribution'].get(keyword, 0) + 1
            
            # 每日生成统计
            date_str = content['created_at'].strftime('%Y-%m-%d')
            stats['daily_generation'][date_str] = \
                stats['daily_generation'].get(date_str, 0) + 1
        
        # 计算平均SEO得分
        if stats['total_content'] > 0:
            stats['average_seo_score'] = round(total_score / stats['total_content'], 2)
        
        # 对关键词分布进行排序，只保留前10个
        sorted_keywords = sorted(
            stats['keyword_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        stats['keyword_distribution'] = dict(sorted_keywords)
        
        return stats

    def get_content_quality_analysis(self, content_id):
        """
        获取单个内容的质量分析
        
        Args:
            content_id (str): 内容ID
            
        Returns:
            dict: 质量分析结果
        """
        content = self.content_model.get_by_id(content_id)
        if not content:
            return None
            
        analysis = {
            'basic_info': {
                'title': content.get('title', ''),
                'created_at': content.get('created_at', ''),
                'content_type': content.get('content_type', 'article')
            },
            'seo_metrics': content.get('seo_score', {}),
            'content_metrics': {
                'length': len(content.get('content', '')),
                'keyword_count': self._count_keywords(
                    content.get('content', ''),
                    content.get('keywords', '').split(',')
                )
            },
            'improvement_suggestions': self._generate_suggestions(content)
        }
        
        return analysis
    
    def _count_keywords(self, content, keywords):
        """统计关键词出现次数"""
        keyword_count = {}
        for keyword in keywords:
            keyword = keyword.strip()
            if keyword:
                keyword_count[keyword] = content.lower().count(keyword.lower())
        return keyword_count
    
    def _generate_suggestions(self, content):
        """生成改进建议"""
        suggestions = []
        seo_score = content.get('seo_score', {})
        
        # 标题相关建议
        title_score = seo_score.get('factors', {}).get('title', 0)
        if title_score < 80:
            suggestions.append({
                'type': 'title',
                'message': '标题SEO得分较低，建议优化标题中的关键词使用'
            })
        
        # Meta描述相关建议
        meta_score = seo_score.get('factors', {}).get('meta_description', 0)
        if meta_score < 80:
            suggestions.append({
                'type': 'meta',
                'message': 'Meta描述得分较低，建议增加关键词密度并优化描述语言'
            })
        
        # 内容质量相关建议
        content_score = seo_score.get('factors', {}).get('content_quality', 0)
        if content_score < 80:
            suggestions.append({
                'type': 'content',
                'message': '内容质量得分较低，建议增加原创性并优化关键词分布'
            })
        
        return suggestions
