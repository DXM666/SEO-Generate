from textrazor import TextRazor
import re
from collections import Counter
from ..utils.config import Config
import jieba

class ContentValidator:
    def __init__(self):
        self.config = Config()
        self.client = TextRazor(api_key=self.config.TEXTRAZOR_API_KEY)
        self.client.set_language_override("chi")  # 设置为中文分析
        
    def validate(self, content):
        """
        验证内容质量
        
        Args:
            content (dict): 需要验证的内容，包含以下字段：
                - title: 标题
                - keywords: 关键词列表
                - meta_description: Meta描述
                
        Returns:
            dict: 验证结果，包括关键词密度、可读性等指标
        """
        if not content or not isinstance(content, dict):
            raise ValueError("内容格式无效")

        required_fields = ['title', 'keywords', 'meta_description']
        if not all(field in content for field in required_fields):
            raise ValueError("缺少必要的内容字段")

        validation_result = {
            'keyword_density': self._check_keyword_density(content),
            'readability': self._check_readability(content),
            'seo_score': self._calculate_seo_score(content),
            'content_structure': self._analyze_content_structure(content),
            'meta_validation': self._validate_meta_info(content)
        }
        
        return validation_result
    
    def _check_keyword_density(self, content):
        """
        检查关键词密度
        计算公式：(关键词出现次数 / 总字数) * 100
        """
        text = content['content']
        total_words = len(text)
        keyword_counts = {}
        
        for keyword in content['keywords']:
            count = len(re.findall(keyword, text))
            density = (count / total_words) * 100 if total_words > 0 else 0
            keyword_counts[keyword] = {
                'count': count,
                'density': round(density, 2)
            }
        
        # 评估密度是否合适（建议密度范围：1-3%）
        status = 'optimal'
        for kw, data in keyword_counts.items():
            if data['density'] > 3:
                status = 'high'
            elif data['density'] < 1:
                status = 'low'
        
        return {
            'status': status,
            'details': keyword_counts,
            'suggestions': self._get_density_suggestions(keyword_counts)
        }
    
    def _check_readability(self, content):
        """
        检查内容可读性
        评估标准：
        1. 句子长度
        2. 段落长度
        3. 标点符号使用
        4. 重复词语
        """
        text = content['content']
        sentences = re.split('[。！？]', text)
        paragraphs = text.split('\n')
        
        # 分析句子长度
        sentence_lengths = [len(s.strip()) for s in sentences if s.strip()]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        
        # 分析段落长度
        paragraph_lengths = [len(p.strip()) for p in paragraphs if p.strip()]
        avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
        
        # 分析词语重复
        words = list(jieba.cut(text))
        word_freq = Counter(words)
        repeated_words = {word: count for word, count in word_freq.items() if count > 3 and len(word) > 1}
        
        suggestions = []
        score = 100
        
        # 评分规则
        if avg_sentence_length > 50:
            score -= 10
            suggestions.append("句子平均长度过长，建议适当分句")
        
        if avg_paragraph_length > 200:
            score -= 10
            suggestions.append("段落平均长度过长，建议适当分段")
            
        if len(repeated_words) > 5:
            score -= 5
            suggestions.append("存在过多重复词语，建议适当调整用词")
        
        return {
            'score': score,
            'statistics': {
                'avg_sentence_length': round(avg_sentence_length, 2),
                'avg_paragraph_length': round(avg_paragraph_length, 2),
                'repeated_words': repeated_words
            },
            'suggestions': suggestions
        }
    
    def _calculate_seo_score(self, content):
        """
        计算整体SEO得分
        评估维度：
        1. 标题优化
        2. Meta描述
        3. 内容质量
        4. 关键词使用
        5. 内容结构
        """
        scores = {}
        
        # 评估标题
        title_score = self._evaluate_title(content['title'], content['keywords'])
        scores['title'] = title_score
        
        # 评估Meta描述
        meta_score = self._evaluate_meta_description(content['meta_description'], content['keywords'])
        scores['meta_description'] = meta_score
        
        # 评估内容质量
        content_score = self._evaluate_content_quality(content['content'])
        scores['content_quality'] = content_score
        
        # 计算总分（权重可调整）
        total_score = (
            title_score * 0.3 +
            meta_score * 0.2 +
            content_score * 0.5
        )
        
        return {
            'total_score': round(total_score, 2),
            'factors': scores,
            'suggestions': self._get_seo_suggestions(scores)
        }
    
    def _analyze_content_structure(self, content):
        """
        分析内容结构
        检查：
        1. 标题层级
        2. 段落分布
        3. 图片使用
        4. 列表使用
        """
        text = content['content']
        
        # 分析标题层级
        h1_count = len(re.findall(r'#\s', text))
        h2_count = len(re.findall(r'##\s', text))
        h3_count = len(re.findall(r'###\s', text))
        
        # 分析段落
        paragraphs = [p for p in text.split('\n') if p.strip()]
        
        # 分析图片
        image_count = len(re.findall(r'!\[.*?\]\(.*?\)', text))
        
        # 分析列表
        list_count = len(re.findall(r'[-*]\s', text))
        
        structure_score = 100
        suggestions = []
        
        if h1_count == 0:
            structure_score -= 10
            suggestions.append("缺少主标题，建议添加")
        
        if h2_count < 2:
            structure_score -= 5
            suggestions.append("二级标题数量不足，建议增加文章结构")
            
        if image_count == 0:
            structure_score -= 5
            suggestions.append("未使用图片，建议适当添加图片增强内容")
            
        if list_count == 0:
            structure_score -= 5
            suggestions.append("未使用列表，建议使用列表来组织内容")
        
        return {
            'score': structure_score,
            'structure': {
                'headings': {
                    'h1': h1_count,
                    'h2': h2_count,
                    'h3': h3_count
                },
                'paragraphs': len(paragraphs),
                'images': image_count,
                'lists': list_count
            },
            'suggestions': suggestions
        }
    
    def _validate_meta_info(self, content):
        """
        验证Meta信息
        检查：
        1. 标题长度
        2. Meta描述长度
        3. 关键词使用
        """
        title = content['title']
        meta_description = content['meta_description']
        keywords = content['keywords']
        
        issues = []
        
        # 检查标题长度（建议：10-60个字符）
        if len(title) < 10:
            issues.append("标题过短，建议在10-60个字符之间")
        elif len(title) > 60:
            issues.append("标题过长，建议在10-60个字符之间")
            
        # 检查Meta描述长度（建议：120-160个字符）
        if len(meta_description) < 120:
            issues.append("Meta描述过短，建议在120-160个字符之间")
        elif len(meta_description) > 160:
            issues.append("Meta描述过长，建议在120-160个字符之间")
            
        # 检查关键词使用
        if not any(kw in title for kw in keywords):
            issues.append("标题中未包含关键词")
        if not any(kw in meta_description for kw in keywords):
            issues.append("Meta描述中未包含关键词")
            
        return {
            'status': 'valid' if not issues else 'invalid',
            'issues': issues,
            'meta_lengths': {
                'title': len(title),
                'description': len(meta_description)
            }
        }
    
    def _get_density_suggestions(self, keyword_counts):
        """生成关键词密度相关建议"""
        suggestions = []
        for keyword, data in keyword_counts.items():
            if data['density'] > 3:
                suggestions.append(f"关键词'{keyword}'的密度过高({data['density']}%)，建议适当减少使用")
            elif data['density'] < 1:
                suggestions.append(f"关键词'{keyword}'的密度过低({data['density']}%)，建议适当增加使用")
        return suggestions
    
    def _get_seo_suggestions(self, scores):
        """根据各项得分生成SEO优化建议"""
        suggestions = []
        if scores['title'] < 80:
            suggestions.append("标题优化空间较大，建议包含关键词并注意长度")
        if scores['meta_description'] < 80:
            suggestions.append("Meta描述需要改进，建议包含关键词并控制在合适长度")
        if scores['content_quality'] < 80:
            suggestions.append("内容质量有待提升，建议注意关键词分布和内容结构")
        return suggestions
    
    def _evaluate_title(self, title, keywords):
        """评估标题质量"""
        score = 100
        
        # 检查长度
        if len(title) < 10 or len(title) > 60:
            score -= 20
            
        # 检查关键词
        if not any(kw in title for kw in keywords):
            score -= 30
            
        # 检查标点符号使用
        if len(re.findall(r'[。，、？！]', title)) > 2:
            score -= 10
            
        return score
    
    def _evaluate_meta_description(self, description, keywords):
        """评估Meta描述质量"""
        score = 100
        
        # 检查长度
        if len(description) < 120 or len(description) > 160:
            score -= 20
            
        # 检查关键词
        if not any(kw in description for kw in keywords):
            score -= 30
            
        # 检查可读性
        if len(re.findall(r'[。，、？！]', description)) > 4:
            score -= 10
            
        return score
    
    def _evaluate_content_quality(self, content):
        """评估内容质量"""
        score = 100
        
        # 检查内容长度
        if len(content) < 800:
            score -= 20
        
        # 检查段落数量
        paragraphs = [p for p in content.split('\n') if p.strip()]
        if len(paragraphs) < 5:
            score -= 10
            
        # 检查标点符号使用
        punctuation_ratio = len(re.findall(r'[。，、？！]', content)) / len(content)
        if punctuation_ratio > 0.2:
            score -= 10
            
        return score
