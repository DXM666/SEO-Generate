import torch
from transformers import AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM, AutoModelForCausalLM
import gc
from pprint import pprint
import re
import json


def test_gpu():
    print("PyTorch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("CUDA version:", torch.version.cuda)
        print("CUDA device count:", torch.cuda.device_count())
        print("Current CUDA device:", torch.cuda.current_device())
        print("CUDA device name:", torch.cuda.get_device_name(0))
        print("GPU Memory Usage:")
        print(torch.cuda.memory_summary())

def clear_gpu_memory():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()
   
def test_models():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\nTesting English models on {device}...")
    
    en_model_name = "meta-llama/Llama-3.2-3B-Instruct"
    try:
        tokenizer = AutoTokenizer.from_pretrained(en_model_name,use_auth_token=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        model = AutoModelForCausalLM.from_pretrained(
            en_model_name,
            torch_dtype=torch.float16,
            device_map='auto',
        )
        pprint("English model loaded successfully!")

        base_sys = '''You are an SEO optimization expert. Follow these steps to generate SEO information:

1. Analyze the request carefully
2. Generate a compelling title (max 60 chars)
3. Create an engaging meta description (max 160 chars)
4. Select relevant keywords (5-10)
5. Format the output as a SINGLE JSON object
6. ONLY return the JSON object, no other text

Remember: Do not include any explanations, only output the JSON object.'''

        base_user = '''Generate an SEO-optimized JSON object for an e-commerce website that sells electronics and gadgets.

Required format:
{
    "title": "...",
    "metaDescription": "...",
    "keywords": [...]
}

Think step by step:
1. What makes a good SEO title for electronics store?
2. What meta description would drive clicks?
3. What keywords do people search for?

Now generate ONLY the JSON object.'''

        assistant_example = '''{
    "title": "Top Electronics & Gadgets Store | Best Deals Online",
    "metaDescription": "Discover amazing deals on the latest electronics and gadgets. Free shipping on orders over $50. Shop now and save big!",
    "keywords": ["electronics store", "gadgets online", "tech deals", "buy electronics", "electronic devices"]
}'''

        messages = [
            {"role": "system", "content": base_sys},
            {"role": "user", "content": base_user},
            {"role": "assistant", "content": assistant_example},
            {"role": "user", "content": "Now generate a new, unique JSON with the same structure but different content."}
        ]

        input_text = "Let's think about this step by step:\n\n"
        for message in messages:
            role = message["role"]
            content = message["content"]
            input_text += f"{role.title()}: {content}\n\n"

        inputs = tokenizer(
            input_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
            add_special_tokens=True
        )
        
        if torch.cuda.is_available():
            inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_length=500,
                num_return_sequences=1,
                pad_token_id=tokenizer.pad_token_id,
                do_sample=True,
                temperature=0.7,  # 增加一些创造性
                top_p=0.95,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        
        # 提取JSON的新方法
        def extract_clean_json(text):
            # 移除所有的代码块标记和换行
            text = re.sub(r'```(?:json)?\s*', '', text)
            text = text.replace('\n', ' ').strip()
            
            # 找到最后一个JSON对象（因为示例JSON在前面）
            json_matches = list(re.finditer(r'\{[^{]*\}', text))
            if not json_matches:
                return None
                
            try:
                json_str = json_matches[-1].group()
                # 清理JSON字符串
                json_str = re.sub(r',\s*}', '}', json_str)  # 移除尾随逗号
                json_str = re.sub(r',\s*]', ']', json_str)  # 移除数组中的尾随逗号
                # 标准化字段名
                json_str = json_str.replace('meta_description', 'metaDescription')
                # 解析JSON
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None
        
        # 处理响应
        json_data = extract_clean_json(response)
        
        if json_data:
            # 验证和规范化字段
            normalized_data = {
                "title": json_data.get("title", ""),
                "metaDescription": json_data.get("metaDescription", json_data.get("meta_description", "")),
                "keywords": json_data.get("keywords", [])
            }
            
            # 验证字段长度
            if len(normalized_data["title"]) > 60:
                normalized_data["title"] = normalized_data["title"][:57] + "..."
            if len(normalized_data["metaDescription"]) > 160:
                normalized_data["metaDescription"] = normalized_data["metaDescription"][:157] + "..."
            
            # 确保关键词数量合适
            keywords = normalized_data["keywords"]
            if len(keywords) > 10:
                normalized_data["keywords"] = keywords[:10]
            elif len(keywords) < 5:
                normalized_data["keywords"].extend([
                    "online shopping",
                    "best deals",
                    "top products",
                    "free shipping",
                    "discount offers"
                ][:5-len(keywords)])
            
            # 格式化输出
            formatted_json = json.dumps(normalized_data, ensure_ascii=False, indent=2)
            print("\n生成的SEO信息：")
            print(formatted_json)
        else:
            print("未能解析有效的JSON响应")
            print("原始响应：")
            print(response)
        
    except Exception as e:
        print(f"Error testing English model: {str(e)}")
    finally:
        clear_gpu_memory()

if __name__ == "__main__":
    print("Starting GPU and model tests...\n")
    # test_gpu()
    test_models()
