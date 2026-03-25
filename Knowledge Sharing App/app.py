from flask import Flask, redirect, url_for            
from flask_migrate import Migrate
from flask_login import LoginManager, login_required
from config import Config
from models import db, Users

# 各Blueprintのインポート
from auth.views import auth_bp
from sharing.views import sharing_bp
from mypage.views import mypage_bp
from managers.views import managers_bp
from contributionscores.views import contributionscores_bp
from archive.views import archive_bp


app = Flask(__name__)
app.config.from_object(Config)

# dbとFlaskの紐づけ
db.init_app(app)

migrate = Migrate(app, db)

# ログイン管理の設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = "ログインしてください"
login_manager.login_view = 'auth.welcome'

# Blueprintの登録
app.register_blueprint(auth_bp)
app.register_blueprint(sharing_bp, url_prefix='/sharing')
app.register_blueprint(mypage_bp)
app.register_blueprint(managers_bp)
app.register_blueprint(contributionscores_bp)
app.register_blueprint(archive_bp) 

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# マネージャー機能
@app.route('/management_redirect')
@login_required
def management():
    return redirect(url_for('managers.management'))

@app.route('/hr_redirect')
@login_required
def hr_management():
    return redirect(url_for('contributionscores.index'))

if __name__ == '__main__':
    app.run()