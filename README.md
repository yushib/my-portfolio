# Knowledge Sharing App

A web application designed to improve knowledge sharing inside organizations.

The system allows employees to ask questions anonymously and
visualizes the contribution level of answers using AI-based sentiment analysis.

Tech Stack:
Python / Flask / SQLite / SQLAlchemy / Gemini API

---

企業内で「質問しづらい」「質問に回答しても適切に評価されない」という課題を解決するために  
匿名で気軽に質問できて、回答の貢献度を可視化したアプリケーションを開発しました。

---

## 機能概要

### 従業員
- 質問を投稿・編集・キャンセル
- 回答を投稿
- My Page で質問と回答を管理
- 回答へのフィードバックを送信

### マネージャー
- 部下の回答とフィードバックを一覧で確認
- AI による感情分析で算出したスコアを確認
- スコアの修正と修正理由を送信

### 人事
- 全従業員のスコアを確認
- マネージャーの修正理由を確認
- 修正理由が不透明であれば差し戻し
- 最終スコアを確定

---

## 使用技術
- フロント：HTML / CSS / JavaScript / Bootstrap
- バックエンド：Python / Flask / Jinja2 / Gemini API
- データベース：SQLite（SQLAlchemy）

---

## AI 活用
- フィードバックの感情分析
- スコアリング（1 / 3 / 5）
- 複数回答の要約生成

---

## 環境変数の設定

このアプリを実行するには、Google APIキーが必要です。

1. プロジェクト直下に `.env` ファイルを作成してください。
2. 以下の環境変数を設定してください。

Google_API_KEY=your_api_key

---
## 主なディレクトリ構成
```
app.py
config.py
models.py
forms.py
analysis.py
fix.py
sample_db.py
templates/
sharing/
mypage/
managers/
contributionscores/
archive/
auth/
```
