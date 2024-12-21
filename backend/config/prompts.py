"""
提示词配置文件
"""

# SEO生成相关提示词
SEO_SYSTEM_PROMPT = '''You are an SEO optimization expert. Follow these steps to generate SEO information:

1. Analyze the request carefully
2. Generate a compelling title (max 60 chars)
3. Create an engaging meta description (max 160 chars)
4. Select relevant keywords (5-10)
5. Format the output as a SINGLE JSON object
6. ONLY return the JSON object, no other text

Remember: Do not include any explanations, only output the JSON object.'''

SEO_USER_PROMPT_TEMPLATE = '''Generate an SEO-optimized JSON object for {business_type}.

Required format:
{{
    "title": "...",
    "metaDescription": "...",
    "keywords": [...]
}}

Think step by step:
1. What makes a good SEO title for this business?
2. What meta description would drive clicks?
3. What keywords do people search for?

Now generate ONLY the JSON object.'''

SEO_ASSISTANT_EXAMPLE = '''{
    "title": "Top Electronics & Gadgets Store | Best Deals Online",
    "metaDescription": "Discover amazing deals on the latest electronics and gadgets. Free shipping on orders over $50. Shop now and save big!",
    "keywords": ["electronics store", "gadgets online", "tech deals", "buy electronics", "electronic devices"]
}'''

# 生成参数配置
GENERATION_PARAMS = {
    "temperature": 0.7,
    "top_p": 0.95,
    "repetition_penalty": 1.2,
    "no_repeat_ngram_size": 3,
    "max_length": 500
}

# 字段验证配置
VALIDATION_PARAMS = {
    "title_max_length": 60,
    "meta_description_max_length": 160,
    "min_keywords": 5,
    "max_keywords": 10,
    "default_keywords": [
        "online shopping",
        "best deals",
        "top products",
        "free shipping",
        "discount offers"
    ]
}
