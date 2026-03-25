from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Questions, Feedbacks
from datetime import datetime

# Blueprintの定義
mypage_bp = Blueprint('mypage', __name__)

# マイページ画面
@mypage_bp.route('/mypage')
@login_required
def mypage():
    # ログインユーザーのIDを取得
    user_id = int(current_user.get_id())                
    
    # ログインユーザーと質問の紐づけ
    my_questions = Questions.query.filter_by(user_id=user_id).order_by(Questions.q_id.desc()).all()                
    
    # mypage.html に質問データを渡す
    return render_template('mypage.html', questions=my_questions)                

# フィードバック送信機能
@mypage_bp.route('/post_feedback/<int:a_id>', methods=['POST'])
@login_required
def post_feedback(a_id):
    feedback = request.form.get('feedback')                
    
    if not feedback:
        return redirect(url_for('mypage.mypage'))                
    
    # データベースへの保存処理
    new_feedback = Feedbacks(
        user_id=current_user.user_id,
        feedback=feedback,
        created_at=datetime.now(),
        a_id=a_id
    )
    db.session.add(new_feedback)
    db.session.commit()
    
    return redirect(url_for('mypage.mypage'))