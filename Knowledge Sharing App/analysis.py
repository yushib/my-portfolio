import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")

# Geminiモデルの設定
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-lite')

def analyze_feedback(text):
    if not text:
        return {"sentiment": "none", "ai_score": 0, "rev": "未入力"}

    prompt = f"""
    以下のフィードバック内容を分析し、指定の形式で回答してください。
    
    【ルール】
    1. 感情判定(sentiment): positive, neutral, negative, none のいずれか
    2. スコア(ai_score): positive=5, neutral=3, negative=1, none=0
    
    【Few-Shot Learning】
    フィードバック：よくわかりました。 -> positive | 5
    フィードバック：少しは参考になりました。 -> neutral | 3
    フィードバック：Not sure if this is right. -> negative | 1
    
    【出力形式】
    感情 | スコア
    
    フィードバック：
    {text}
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"temperature": 0})
        output = response.text.strip()
        
        print("DEBUG OUTPUT:", output)
        
        match = re.search(r"(positive|neutral|negative|none)\s*\|\s*(\d+)", output, re.IGNORECASE)
        if not match:
            return {"sentiment": "none", "ai_score": 0}
        sentiment = match.group(1).lower()
        score = int(match.group(2))
        
        return {
            "sentiment": sentiment,
            "ai_score": score
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"sentiment": "none", "ai_score": 0}