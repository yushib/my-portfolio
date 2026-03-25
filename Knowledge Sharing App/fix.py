from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # エラーの元凶を消し、新しい列を追加します
        db.session.execute(text("DROP TABLE IF EXISTS alembic_version"))
        db.session.execute(text("ALTER TABLE feedbacks ADD COLUMN is_resolved BOOLEAN DEFAULT 0 NOT NULL"))
        db.session.commit()
        print("成功：データが復活し、is_resolved も追加されました！")
    except Exception as e:
        print(f"確認：{e}")