from flask import Blueprint, jsonify, request, send_file
from ..services.seo_generator import SEOGenerator
from ..services.content_validator import ContentValidator
from ..services.analytics_service import AnalyticsService
from ..services.batch_service import BatchService
from ..models.content import Content
import io

# 创建蓝图
api_bp = Blueprint('api', __name__)

seo_generator = SEOGenerator()
content_validator = ContentValidator()
analytics_service = AnalyticsService()
batch_service = BatchService()

@api_bp.route('/generate', methods=['POST'])
def generate_content():
    """生成SEO内容的API端点"""
    data = request.get_json()
    keywords = data.get('keywords', '')
    content_type = data.get('type', 'article')
    language = data.get('language', 'en')
    
    try:
        # 生成内容
        generated_content = seo_generator.generate(keywords, content_type, language)
        # 验证内容
        validation_result = content_validator.validate(generated_content)
        
        # 创建并保存内容
        content = Content(
            title=generated_content.get('title', ''),
            description=generated_content.get('description', ''),
            content=generated_content.get('content', ''),
            keywords=keywords,
            content_type=content_type,
            language=language
        )
        content_id = content.save()
        
        return jsonify({
            'success': True,
            'content': generated_content,
            'validation': validation_result,
            'content_id': content_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/contents', methods=['GET'])
def get_contents():
    """获取内容列表"""
    try:
        limit = int(request.args.get('limit', 10))
        skip = int(request.args.get('skip', 0))
        contents = Content.get_list(limit, skip)
        return jsonify({
            'success': True,
            'contents': contents
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/contents/<content_id>', methods=['GET'])
def get_content(content_id):
    """获取单个内容"""
    try:
        content = Content.get_by_id(content_id)
        if content:
            return jsonify({
                'success': True,
                'content': content.to_dict()
            })
        return jsonify({
            'success': False,
            'error': 'Content not found'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/search', methods=['GET'])
def search_contents():
    """搜索内容"""
    try:
        query = request.args.get('q', '')
        results = Content.search(query)
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/batch/generate', methods=['POST'])
def batch_generate():
    """批量生成内容"""
    try:
        data = request.get_json()
        keywords_list = data.get('keywords_list', [])
        content_type = data.get('type', 'article')
        language = data.get('language', 'en')
        
        results = batch_service.batch_generate(
            keywords_list,
            content_type,
            language
        )
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/batch/export', methods=['POST'])
def export_contents():
    """导出内容"""
    try:
        data = request.get_json()
        content_ids = data.get('content_ids', [])
        export_format = data.get('format', 'csv')
        
        file_data = batch_service.export_contents(content_ids, export_format)
        
        # 创建内存文件对象
        file_obj = io.BytesIO()
        file_obj.write(file_data.encode('utf-8'))
        file_obj.seek(0)
        
        filename = f'seo_contents_{export_format}.{export_format}'
        mimetype = 'text/csv' if export_format == 'csv' else 'application/json'
        
        return send_file(
            file_obj,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/batch/import-keywords', methods=['POST'])
def import_keywords():
    """导入关键词"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
            
        keywords_list = batch_service.import_keywords_file(file)
        
        return jsonify({
            'success': True,
            'keywords_list': keywords_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
