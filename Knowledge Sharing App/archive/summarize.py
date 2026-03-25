import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")

# Geminiモデルの設定
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-lite')


def generate_summary(answers):
    # 複数回答がある場合 → Gemini で要約
    joined_answer = "\n\n".join(
    f"回答{i+1}: {a.a_content}"
    for i, a in enumerate(answers)
    )

    prompt = f"""
以下の複数の回答以下の複数の回答内容から、重要な情報を抽出して1つに集約してください。

{joined_answer}

# 出力ルール（厳守）
- 複数の回答が同じ内容なら、その内容を1度だけ出力してください。
- 「申し訳ありません」「要約できません」「回答1では」といった解説・前置き・メタ発言は**一切禁止**です。
- 入力データにある言葉のみを使用して構成してください。
- 結果が単語のみになっても構いません。出力は要約されたテキストのみにしてください。
"""

    try:
        config = {"temperature": 0}
        response = model.generate_content(prompt, generation_config=config)
        return response.text.strip()

    except Exception as e:
        print(f"Error during summary generation: {e}")
        return answers[0].a_content