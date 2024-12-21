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
    """
    生成SEO内容的API端点
    
    请求方式：POST
    请求体：
    {
        "business_type": "string",  # 必填，业务类型描述
        "language": "string"        # 可选，语言选择 (默认为 "en")
    }
    
    返回：
    {
        "success": true,
        "data": {
            "title": "SEO优化的标题",
            "metaDescription": "Meta描述",
            "keywords": ["关键词1", "关键词2"]
        },
        "validation": {
            "keyword_density": {...},
            "readability": {...},
            "seo_score": {...}
        }
    }
    """
    try:
        data = request.get_json()
        if not data or 'business_type' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要的business_type参数'
            }), 400
            
        business_type = data['business_type']
        
        # 生成SEO内容
        generated_content = seo_generator.generate_seo(business_type)
        
        # 验证内容
        validation_result = content_validator.validate(generated_content)
        
        # 创建并保存内容
        content = Content(
            title=generated_content['title'],
            meta_description=generated_content['metaDescription'],
            keywords=generated_content['keywords'],
            business_type=business_type
        )
        content_id = content.save()
        
        return jsonify({
            'success': True,
            'data': generated_content,
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
    """
    获取内容列表
    
    请求方式：GET
    请求参数：
    - limit: 可选，整数，每页数量，默认10
    - skip: 可选，整数，跳过数量，默认0
    
    返回：
    {
        "success": true,
        "contents": [{
            "id": "xxx",
            "title": "标题",
            "description": "描述",
            "content": "内容",
            "keywords": ["关键词1", "关键词2"],
            "created_at": "2024-01-01 00:00:00"
        }],
        "total": 100,
        "page": 1,
        "total_pages": 10
    }
    """
    try:
        limit = int(request.args.get('limit', 10))
        skip = int(request.args.get('skip', 0))
        
        contents, total = Content.get_list(limit, skip)
        return jsonify({
            'success': True,
            'contents': contents,
            'total': total,
            'page': skip // limit + 1,
            'total_pages': (total + limit - 1) // limit
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/contents/<content_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_content(content_id):
    """
    管理单个内容：获取、更新、删除
    
    请求方式：
    - GET: 获取内容详情
    - PUT: 更新内容
    - DELETE: 删除内容
    
    PUT请求体：
    {
        "title": "新标题",        # 可选
        "description": "新描述",  # 可选
        "content": "新内容",      # 可选
        "keywords": ["新关键词"]   # 可选
    }
    
    返回：
    {
        "success": true,
        "content": {
            "id": "xxx",
            "title": "标题",
            "description": "描述",
            "content": "内容",
            "keywords": ["关键词1", "关键词2"],
            "created_at": "2024-01-01 00:00:00",
            "updated_at": "2024-01-01 00:00:00"
        }
    }
    """
    try:
        if request.method == 'GET':
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
            
        elif request.method == 'PUT':
            data = request.get_json()
            content = Content.get_by_id(content_id)
            if not content:
                return jsonify({
                    'success': False,
                    'error': 'Content not found'
                }), 404
            
            # 更新内容
            updated = content.update(data)
            return jsonify({
                'success': True,
                'content': updated.to_dict()
            })
            
        elif request.method == 'DELETE':
            result = Content.delete(content_id)
            return jsonify({
                'success': result
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/search', methods=['GET'])
def search_contents():
    """
    搜索内容
    
    请求方式：GET
    请求参数：
    - q: 必填，字符串，搜索关键词
    - type: 可选，字符串，内容类型筛选
    - limit: 可选，整数，返回数量限制，默认10
    
    返回：
    {
        "success": true,
        "results": [{
            "id": "xxx",
            "title": "标题",
            "description": "描述",
            "content": "内容",
            "keywords": ["关键词1", "关键词2"],
            "relevance": 0.95
        }],
        "total": 10
    }
    """
    try:
        query = request.args.get('q', '')
        content_type = request.args.get('type')
        limit = int(request.args.get('limit', 10))
        
        results = Content.search(query, content_type, limit)
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/batch/generate', methods=['POST'])
def batch_generate():
    """
    批量生成内容
    
    请求方式：POST
    请求体：
    {
        "keywords": [
            ["关键词1", "关键词2"],
            ["关键词3", "关键词4"]
        ],
        "type": "article",     # 可选，内容类型
        "language": "zh",      # 可选，语言
        "length": "medium"     # 可选，内容长度
    }
    
    返回：
    {
        "success": true,
        "task_id": "xxx",     # 任务ID，用于查询进度
        "total": 2            # 总任务数
    }
    """
    try:
        data = request.get_json()
        keywords_list = data.get('keywords', [])
        content_type = data.get('type', 'article')
        language = data.get('language', 'zh')
        length = data.get('length', 'medium')
        
        task_id = batch_service.create_task(keywords_list, content_type, language, length)
        return jsonify({
            'success': True,
            'task_id': task_id,
            'total': len(keywords_list)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/batch/status/<task_id>', methods=['GET'])
def get_batch_status(task_id):
    """
    获取批量任务状态
    
    请求方式：GET
    
    返回：
    {
        "success": true,
        "status": "running",   # running/completed/failed
        "progress": {
            "total": 10,
            "completed": 5,
            "failed": 0
        },
        "results": [{
            "keywords": ["关键词1", "关键词2"],
            "content_id": "xxx",
            "status": "success"
        }]
    }
    """
    try:
        status = batch_service.get_task_status(task_id)
        return jsonify({
            'success': True,
            **status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/export', methods=['POST'])
def export_contents():
    """
    导出内容
    
    请求方式：POST
    请求体：
    {
        "content_ids": ["xxx", "yyy"],  # 可选，指定要导出的内容ID
        "format": "csv",               # 必填，导出格式：csv/excel/json
        "type": "article",            # 可选，按类型筛选
        "language": "zh",             # 可选，按语言筛选
        "date_range": {               # 可选，按日期范围筛选
            "start": "2024-01-01",
            "end": "2024-01-31"
        }
    }
    
    返回：文件流
    """
    try:
        data = request.get_json()
        content_ids = data.get('content_ids', [])
        export_format = data.get('format', 'csv')
        content_type = data.get('type')
        language = data.get('language')
        date_range = data.get('date_range')
        
        file_data = batch_service.export_contents(
            content_ids, export_format, content_type, language, date_range
        )
        
        return send_file(
            io.BytesIO(file_data),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=f'contents.{export_format}'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/import/keywords', methods=['POST'])
def import_keywords():
    """
    导入关键词
    
    请求方式：POST
    Content-Type: multipart/form-data
    
    表单参数：
    - file: 必填，文件对象，支持csv/excel格式
    - type: 可选，字符串，内容类型
    - language: 可选，字符串，语言
    
    返回：
    {
        "success": true,
        "task_id": "xxx",     # 任务ID，用于批量生成
        "total": 100,         # 导入的关键词组数
        "invalid": []         # 无效的行数据
    }
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
            
        file = request.files['file']
        content_type = request.form.get('type')
        language = request.form.get('language')
        
        result = batch_service.import_keywords(file, content_type, language)
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """
    获取数据分析概览
    
    请求方式：GET
    请求参数：
    - period: 可选，字符串，统计周期：day/week/month/year，默认month
    - start_date: 可选，日期字符串，开始日期
    - end_date: 可选，日期字符串，结束日期
    
    返回：
    {
        "success": true,
        "data": {
            "total_contents": 1000,
            "contents_by_type": {
                "article": 500,
                "product": 300,
                "blog": 200
            },
            "contents_by_language": {
                "zh": 600,
                "en": 400
            },
            "generation_trend": [{
                "date": "2024-01-01",
                "count": 10
            }],
            "average_scores": {
                "seo": 85,
                "readability": 90
            }
        }
    }
    """
    try:
        period = request.args.get('period', 'month')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        overview = analytics_service.get_overview(period, start_date, end_date)
        return jsonify({
            'success': True,
            'data': overview
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/analytics/keywords', methods=['GET'])
def get_keywords_analytics():
    """
    获取关键词分析
    
    请求方式：GET
    请求参数：
    - period: 可选，字符串，统计周期：day/week/month/year，默认month
    - limit: 可选，整数，返回数量，默认10
    
    返回：
    {
        "success": true,
        "data": {
            "top_keywords": [{
                "keyword": "关键词1",
                "count": 100,
                "average_score": 85
            }],
            "keyword_trends": [{
                "date": "2024-01-01",
                "keywords": {
                    "关键词1": 10,
                    "关键词2": 8
                }
            }]
        }
    }
    """
    try:
        period = request.args.get('period', 'month')
        limit = int(request.args.get('limit', 10))
        
        analytics = analytics_service.get_keywords_analytics(period, limit)
        return jsonify({
            'success': True,
            'data': analytics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
