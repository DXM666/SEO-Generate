import torch
from transformers import AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM
import gc

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
    print("\nTesting models...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 测试中文模型
    print("\nTesting Chinese model (ChatGLM-6B)...")
    zh_model_name = "THUDM/chatglm-6b"
    try:
        tokenizer = AutoTokenizer.from_pretrained(zh_model_name, trust_remote_code=True)
        model = AutoModel.from_pretrained(
            zh_model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16,  # 使用半精度
            load_in_8bit=True,  # 8位量化
            device_map='auto',  # 自动设备映射
            low_cpu_mem_usage=True,  # 低CPU内存使用
        )
        print("Chinese model loaded successfully!")
        
        # 测试简单的生成
        inputs = tokenizer("你好，请介绍一下自己。", return_tensors="pt", padding=True, truncation=True, max_length=512)
        if torch.cuda.is_available():
            inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs['input_ids'],
                max_length=100,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id else tokenizer.eos_token_id,
            )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print("Sample response:", response)
        
        # 清理内存
        del model
        clear_gpu_memory()
        
    except Exception as e:
        print("Error loading Chinese model:", str(e))
    
    # 测试英文模型
    print("\nTesting English model (T5-small)...")
    en_model_name = "google-t5/t5-small"
    try:
        tokenizer = AutoTokenizer.from_pretrained(en_model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(
            en_model_name,
            torch_dtype=torch.float16,  # 使用半精度
            load_in_8bit=True,  # 8位量化
            device_map='auto',  # 自动设备映射
            low_cpu_mem_usage=True,  # 低CPU内存使用
        )
        print("English model loaded successfully!")
        
        # 测试简单的生成
        input_text = "translate English to Chinese: How are you?"
        inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        if torch.cuda.is_available():
            inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs['input_ids'],
                max_length=100,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id else tokenizer.eos_token_id,
            )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print("Sample response:", response)
        
        # 清理内存
        del model
        clear_gpu_memory()
        
    except Exception as e:
        print("Error loading English model:", str(e))

if __name__ == "__main__":
    print("Starting GPU and model tests...\n")
    test_gpu()
    test_models()
