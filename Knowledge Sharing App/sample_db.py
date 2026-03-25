from flask import Flask
from config import Config
from models import db, Users, Questions, Answers
from werkzeug.security import generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():

    # デモユーザー用のサンプルユーザー名のリスト
    names = [
        "manager1", "manager2", "manager3", "hr1",  # 1-4
        "employee5", "employee6", "employee7", "employee8", "employee9", "employee10", "employee11", "employee12", # 5-12
        "employee13", "employee14", "employee15", "employee16", "employee17", "employee18", "employee19", "employee20"  # 13-20
    ]

    # デモユーザー用のサンプルパスワード
    user_credentials = {
        1: "password1", 2: "password2", 3: "password3", 4: "password4", 5: "password5",
        6: "password6", 7: "password7", 8: "password8", 9: "password9", 10: "passworda",
        11: "passwordb", 12: "passwordc", 13: "passwordd", 14: "passworde", 15: "passwordf",
        16: "passwordg", 17: "passwordhh", 18: "passwordi", 19: "passwordj", 20: "passwordk"
    }

    # ユーザー情報の更新および登録
    for i, name in enumerate(names, 1):
        user = Users.query.get(i)
        raw_password = user_credentials.get(i)
        
        # 部署判定ロジック
        if i == 1 or 5 <= i <= 7: d_id = "DEPT01"
        elif i == 2 or 8 <= i <= 14: d_id = "DEPT02"
        elif i == 3 or 15 <= i <= 20: d_id = "DEPT03"
        elif i == 4: d_id = "HR01"
        else: d_id = "DEPT00"

        if user:
            # 既存レコードの更新（既存のFeedbacksデータを維持）
            user.user_name = name
            user.dept_id = d_id
            user.is_manager = (1 <= i <= 3)
            user.is_hr = (i == 4)
            user.password = generate_password_hash(raw_password)
        else:
            # 新規レコードの作成（db.session.addをこのブロック内で実行）
            new_user = Users(
                user_id=i,
                password=generate_password_hash(raw_password),
                user_name=name,
                is_manager=(1 <= i <= 3), 
                is_hr=(i == 4),
                dept_id=d_id
            )
            db.session.add(new_user)

    # 質問データの登録
    q_map = {
        225: (6,  datetime(2025, 11, 25), True),
        226: (5,  datetime(2025, 11, 28), True),
        227: (11, datetime(2025, 12, 4),  True),
        228: (10, datetime(2025, 12, 20), False),
        229: (12, datetime(2026, 1, 15),  False),
        230: (5,  datetime(2026, 2, 13),  False),
        231: (9,  datetime(2026, 3, 20),  False),
        232: (8,  datetime(2026, 3, 20),  False),
        233: (7,  datetime(2026, 3, 22),  False),
        234: (10, datetime(2026, 3, 26),  False),
        235: (7,  datetime(2026, 4, 13),  False)
    }

    for q_id, (u_id, d_date, is_arc) in q_map.items():
        if not Questions.query.get(q_id):
            db.session.add(Questions(
                q_id=q_id, user_id=u_id, q_content="xxxxxxxxxx", 
                deadline=d_date, is_archived=is_arc
            ))

    # 回答データの登録
    a_map = {
        323: (5, 225), 324: (7, 225), 325: (12, 225),
        326: (6, 226), 327: (14, 226),
        328: (15, 227), 329: (6, 227), 330: (8, 227), 331: (16, 227),
        332: (5, 228), 333: (6, 228),
        334: (7, 229),
        335: (10, 230), 336: (11, 230), 337: (8, 230), 338: (9, 230), 339: (18, 230), 340: (13, 230),
        341: (17, 231),
        342: (5, 232), 343: (19, 232), 344: (12, 232), 345: (16, 232),
        346: (6, 233), 347: (13, 233), 348: (11, 233),
        349: (15, 234), 350: (20, 234), 351: (16, 234),
        352: (11, 235)
    }

    for a_id, (u_id, q_id) in a_map.items():
        if not Answers.query.get(a_id):
            db.session.add(Answers(
                a_id=a_id, user_id=u_id, q_id=q_id, a_content="yyyyyyyyyy"
            ))

    db.session.commit()
    print("登録完了")