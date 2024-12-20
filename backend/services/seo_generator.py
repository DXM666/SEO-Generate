import torch
import gc
from transformers import AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM
from ..utils.config import Config

class SEOGenerator:
    def __init__(self,language='en'):
        self.config = Config()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.language = language
        
        if(self.language == 'zh'):
            # 加载中文模型
            self.zh_model_name = "THUDM/chatglm-6b"
            self.zh_tokenizer = AutoTokenizer.from_pretrained(
                self.zh_model_name,
                trust_remote_code=True
            )
            self.zh_model = AutoModel.from_pretrained(
                self.zh_model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16,  # 使用半精度
                load_in_8bit=True,  # 8位量化
                device_map='auto',  # 自动设备映射
                low_cpu_mem_usage=True,  # 低CPU内存使用
            )
        elif(self.language == 'en'):
            # 加载英文模型
            self.en_model_name = "google-t5/t5-small"
            self.en_tokenizer = AutoTokenizer.from_pretrained(
                self.en_model_name
            )
            self.en_model = AutoModelForSeq2SeqLM.from_pretrained(
                self.en_model_name,
                torch_dtype=torch.float16,  # 使用半精度
                load_in_8bit=True,  # 8位量化
                device_map='auto',  # 自动设备映射
                low_cpu_mem_usage=True,  # 低CPU内存使用
            )
        
        # 设置生成参数
        self.max_length = 1500
        self.temperature = 0.7
        self.top_p = 0.9
        self.top_k = 40
    
    def clear_gpu_memory(self):
        """清理GPU内存"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()

    def generate(self, keywords, content_type='article'):
        """
        根据关键词生成SEO优化的内容
        """
        # 选择对应语言的模型和分词器
        if self.language == 'zh':
            model = self.zh_model
            tokenizer = self.zh_tokenizer
        else:
            model = self.en_model
            tokenizer = self.en_tokenizer
        
        # 构建提示词
        prompt = self._build_prompt(keywords, content_type)
        
        try:
            # 生成文本
            inputs = tokenizer(
                prompt, 
                return_tensors='pt', 
                padding=True, 
                truncation=True, 
                max_length=512
            )
            if torch.cuda.is_available():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = model.generate(
                    input_ids=inputs['input_ids'],
                    max_length=self.max_length,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    top_k=self.top_k,
                    num_return_sequences=1,
                    do_sample=True,
                    pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id else tokenizer.eos_token_id,
                )
            
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # 解析生成的内容
            content = self._parse_response(generated_text)
            content = self._post_process(content)
            
            # 清理内存
            self.clear_gpu_memory()
            
            return content
            
        except Exception as e:
            self.clear_gpu_memory()
            raise Exception(f"内容生成失败: {str(e)}")
    
    def _build_prompt(self, keywords, content_type):
        """构建AI提示词"""
        if self.language == 'zh':
            prompts = {
                'article': f"""
                    请基于关键词"{keywords}"创作一篇SEO优化的文章，需要：
                    1. 标题要包含关键词，吸引点击
                    2. Meta描述要简洁有力，突出价值
                    3. 正文要自然融入关键词，避免堆砌
                    4. 分段合理，层次分明
                    5. 结尾要有号召性用语
                    请按以下格式输出：
                    标题：
                    Meta描述：
                    正文：
                """,
                'product': f"""
                    请基于关键词"{keywords}"创作一段产品描述，需要：
                    1. 突出产品核心卖点
                    2. 自然融入关键词
                    3. 描述要具体详实
                    4. 包含产品规格信息
                    请按以下格式输出：
                    标题：
                    描述：
                    规格：
                """
            }
        else:
            prompts = {
                'article': f"""
                    Create an SEO-optimized article based on the keyword "{keywords}". Requirements:
                    1. Title must include keywords and be click-worthy
                    2. Meta description should be concise and highlight value
                    3. Content should naturally incorporate keywords
                    4. Proper paragraphing and structure
                    5. Include a call-to-action at the end
                    Please output in the following format:
                    Title:
                    Meta Description:
                    Content:
                """,
                'product': f"""
                    Create a product description based on the keyword "{keywords}". Requirements:
                    1. Highlight core product benefits
                    2. Naturally incorporate keywords
                    3. Detailed and specific description
                    4. Include product specifications
                    Please output in the following format:
                    Title:
                    Description:
                    Specifications:
                """
            }
        return prompts.get(content_type, prompts['article'])
    
    def _parse_response(self, text):
        """解析生成的文本"""
        # 根据语言选择分隔符
        if self.language == 'zh':
            title_key = '标题'
            meta_key = 'meta描述'
            content_key = '正文'
            desc_key = '描述'
            spec_key = '规格'
        else:
            title_key = 'title'
            meta_key = 'meta description'
            content_key = 'content'
            desc_key = 'description'
            spec_key = 'specifications'
        
        sections = text.split('\n')
        content = {}
        current_section = None
        
        for line in sections:
            line = line.strip()
            if line.lower().endswith(':'):
                section = line[:-1].lower()
                if section == title_key.lower():
                    current_section = 'title'
                elif section in [meta_key.lower(), desc_key.lower()]:
                    current_section = 'description'
                elif section in [content_key.lower(), spec_key.lower()]:
                    current_section = 'content'
                content[current_section] = ''
            elif current_section and line:
                content[current_section] += line + '\n'
                
        return content

    def _post_process(self, content):
        """后处理生成的内容"""
        # 移除多余的空行和空格
        for key in content:
            if isinstance(content[key], str):
                content[key] = '\n'.join(
                    line.strip() for line in content[key].split('\n')
                    if line.strip()
                )
        
        return content
