import re
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from ..config.prompts import (
    SEO_SYSTEM_PROMPT,
    SEO_USER_PROMPT_TEMPLATE,
    SEO_ASSISTANT_EXAMPLE,
    GENERATION_PARAMS,
    VALIDATION_PARAMS
)

class SEOGenerator:
    def __init__(self, model_name="meta-llama/Llama-3.2-3B-Instruct"):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """初始化模型和分词器"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_auth_token=True)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map='auto',
            )
        except Exception as e:
            raise Exception(f"模型初始化失败: {str(e)}")

    def _extract_clean_json(self, text):
        """从文本中提取和清理JSON对象"""
        # 移除代码块标记和换行
        text = re.sub(r'```(?:json)?\s*', '', text)
        text = text.replace('\n', ' ').strip()
        
        # 找到最后一个JSON对象
        json_matches = list(re.finditer(r'\{[^{]*\}', text))
        if not json_matches:
            return None
            
        try:
            json_str = json_matches[-1].group()
            # 清理JSON字符串
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            # 标准化字段名
            json_str = json_str.replace('meta_description', 'metaDescription')
            # 解析JSON
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None

    def _normalize_json_data(self, json_data):
        """规范化JSON数据"""
        if not json_data:
            return None

        # 标准化字段
        normalized_data = {
            "title": json_data.get("title", ""),
            "metaDescription": json_data.get("metaDescription", json_data.get("meta_description", "")),
            "keywords": json_data.get("keywords", [])
        }

        # 验证字段长度
        if len(normalized_data["title"]) > VALIDATION_PARAMS["title_max_length"]:
            normalized_data["title"] = normalized_data["title"][:VALIDATION_PARAMS["title_max_length"]-3] + "..."
        
        if len(normalized_data["metaDescription"]) > VALIDATION_PARAMS["meta_description_max_length"]:
            normalized_data["metaDescription"] = normalized_data["metaDescription"][:VALIDATION_PARAMS["meta_description_max_length"]-3] + "..."

        # 确保关键词数量合适
        keywords = normalized_data["keywords"]
        if len(keywords) > VALIDATION_PARAMS["max_keywords"]:
            normalized_data["keywords"] = keywords[:VALIDATION_PARAMS["max_keywords"]]
        elif len(keywords) < VALIDATION_PARAMS["min_keywords"]:
            normalized_data["keywords"].extend(
                VALIDATION_PARAMS["default_keywords"][:VALIDATION_PARAMS["min_keywords"]-len(keywords)]
            )

        return normalized_data

    def generate_seo(self, business_type):
        """生成SEO信息"""
        try:
            # 构建提示词
            messages = [
                {"role": "system", "content": SEO_SYSTEM_PROMPT},
                {"role": "user", "content": SEO_USER_PROMPT_TEMPLATE.format(business_type=business_type)},
                {"role": "assistant", "content": SEO_ASSISTANT_EXAMPLE},
                {"role": "user", "content": "Now generate a new, unique JSON with the same structure but different content."}
            ]

            # 构建输入文本
            input_text = "Let's think about this step by step:\n\n"
            for message in messages:
                role = message["role"]
                content = message["content"]
                input_text += f"{role.title()}: {content}\n\n"

            # 准备输入
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
                add_special_tokens=True
            )

            if torch.cuda.is_available():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # 生成输出
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids=inputs['input_ids'],
                    attention_mask=inputs['attention_mask'],
                    pad_token_id=self.tokenizer.pad_token_id,
                    do_sample=True,
                    **GENERATION_PARAMS
                )

            # 解码输出
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

            # 提取和处理JSON
            json_data = self._extract_clean_json(response)
            normalized_data = self._normalize_json_data(json_data)

            if normalized_data:
                return normalized_data
            else:
                raise Exception("无法生成有效的SEO信息")

        except Exception as e:
            raise Exception(f"SEO生成失败: {str(e)}")
