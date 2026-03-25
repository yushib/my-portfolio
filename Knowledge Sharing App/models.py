from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

# Flask-SQLAlchemyの生成
db = SQLAlchemy()

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(128), nullable=False)
    user_name = db.Column(db.String(50), default=None)
    is_manager = db.Column(db.Boolean, default=False)
    is_hr = db.Column(db.Boolean, default=False)
    dept_id = db.Column(db.String(20), nullable=False)

    def get_id(self):
        return str(self.user_id)

    def set_password(self, password):
        self.password = generate_password_hash(password)
# 入力したパスワードとハッシュ化されたパスワードの比較
    def check_password(self, password):
        return check_password_hash(self.password, password)

# Questions (質問管理)
class Questions(db.Model):
    __tablename__ = 'questions'
    q_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    q_content = db.Column(db.Text, nullable=False)
    # カレンダー設定用
    deadline = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_anonymous = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)

    # 質問に紐づく回答を一括取得
    answers = db.relationship('Answers', backref='question', lazy=True)

# Answers (回答管理)
class Answers(db.Model):
    __tablename__ = 'answers'
    a_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    q_id = db.Column(db.Integer, db.ForeignKey('questions.q_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    a_content = db.Column(db.Text, nullable=False)
    is_finalized = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

# Feedback（フィードバックの管理）
class Feedbacks(db.Model):
    __tablename__ = 'feedbacks'                
    a_id = db.Column(db.Integer, db.ForeignKey('answers.a_id'), primary_key=True)                
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)                
    feedback = db.Column(db.Text, nullable=False)                
    created_at = db.Column(db.DateTime, default=datetime.now)                
    sentiment = db.Column(db.String(20), nullable=True)  # positive, neutral, negative, none
    ai_score = db.Column(db.Integer, default=0)         # 5, 3, 1, 0
    revised_score = db.Column(db.Integer, nullable=True, default=0)
    mgr_comment = db.Column(db.Text, nullable=True, default="")
    hr_comment = db.Column(db.Text, nullable=True, default="")
    rejection_reason = db.Column(db.Text, nullable=True, default="")
    is_resolved = db.Column(db.Boolean, default=False, nullable=False)
    
    # 回答とフィードバックが1対1になるように設定
    answer = db.relationship('Answers', backref=db.backref('feedback_entry', uselist=False))
    # ユーザー対フィードバックが1対多の関係になるように設定               
    user = db.relationship('Users', backref=db.backref('feedbacks', lazy=True))

# 人事による評価管理
class HRReviews(db.Model):
    __tablename__ = 'hr_reviews'
    
    # ユーザーIDを主キーかつ外部キーに設定
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    
    # 確定処理
    is_finalized = db.Column(db.Boolean, default=False, nullable=False)
    
    # 差戻処理
    is_rejection = db.Column(db.Boolean, default=False, nullable=False)
    
    # ユーザーと点数の確定が1対1になるように設定
    user = db.relationship('Users', backref=db.backref('hr_review', uselist=False))

    def __repr__(self):
        return f'<HRReviews user_id={self.user_id} is_finalized={self.is_finalized} is_rejection={self.is_rejection}>'
    
# AIによる要約の管理（アーカイブ）    
class Summaries(db.Model):
    __tablename__ = 'summaries'
    q_id = db.Column(db.Integer, db.ForeignKey('questions.q_id'), primary_key=True)
    summary = db.Column(db.Text, nullable=False)
    # 質問との紐付け
    question = db.relationship('Questions', uselist=False)