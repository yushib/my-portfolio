from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from models import db, Questions, Answers, Summaries
from archive.summarize import generate_summary

# Blueprintの定義
sharing_bp = Blueprint('sharing', __name__)

# Knowledge Sharing画面
@sharing_bp.route('/sharing')
@login_required
def sharing(): 
    questions = Questions.query.filter_by(is_archived=False).order_by(Questions.deadline.asc()).all()
    return render_template('sharing.html', questions=questions)

# 質問登録
@sharing_bp.route('/post_question', methods=['POST'])
@login_required
def post_question():
    q_content = request.form.get('q_content')
    deadline_str = request.form.get('deadline')
    
    if not q_content or not deadline_str:
        flash("質問内容と回答期限を入力してください")
        return redirect(url_for('sharing.sharing'))

    # 8件の質問＆回答のペアを表示して、9件目以降はアーカイブ画面に自動遷移
    active_qs = Questions.query.filter_by(is_archived=False).order_by(Questions.deadline.asc(), Questions.q_id.asc()).all()
    oldest_q = None
    archived_happened = False
    
    if len(active_qs) >= 8:
        oldest_q = active_qs[0]
        oldest_q.is_archived = True
        archived_happened = True
        db.session.add(oldest_q)
        db.session.commit()
    if archived_happened and oldest_q is not None:
        answers = oldest_q.answers
        if Summaries.query.get(oldest_q.q_id) is None:
            if len(answers) > 1:
                summary = generate_summary(answers)
            elif len(answers) == 1:
                summary = answers[0].a_content
            # 念のため、回答がない場合
            else:
                summary = "残念ながら、回答はありません。"
    
            summary_record = Summaries(
                    q_id=oldest_q.q_id,
                    summary=summary
            )
            db.session.add(summary_record)
            db.session.commit()
    
    # データベースに質問を書き込む
    new_q = Questions(
        user_id=int(current_user.get_id()),
        q_content=q_content,
        deadline=datetime.strptime(deadline_str, '%Y-%m-%d'),
        is_archived=False
    )
    db.session.add(new_q)
    db.session.commit()
    return redirect(url_for('sharing.sharing'))

# 回答の投稿
@sharing_bp.route('/post_answer/<int:q_id>', methods=['POST'])
@login_required
def post_answer(q_id):
    # フォームから回答内容を取得
    a_content = request.form.get('a_content')
    # 内容が空の場合は保存せずに戻る
    if not a_content:
        return redirect(url_for('sharing.sharing'))
    
    # データベースに回答を書き込む
    new_a = Answers(
        q_id=q_id,
        user_id=int(current_user.get_id()),
        a_content=a_content
    )
    db.session.add(new_a)
    db.session.commit()
    return redirect(url_for('sharing.sharing'))

# 質問の編集
@sharing_bp.route('/update_question/<int:q_id>', methods=['POST'])
@login_required
def update_question(q_id):
    # q_idに紐づいた質問内容を取得
    question = Questions.query.get_or_404(q_id)
    new_content = request.form.get('q_content')
    # 質問が編集された場合、新しい質問で上書き
    if new_content:
        question.q_content = new_content
        db.session.commit()
    return redirect(url_for('sharing.sharing'))

# 質問のキャンセル
@sharing_bp.route('/delete_question/<int:q_id>', methods=['POST'])
@login_required
def delete_question(q_id):
    question = Questions.query.get(q_id)
    # 登録した質問に対して既に回答がある場合は削除しない
    if question.answers:
        return redirect(url_for("sharing.sharing"))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for("sharing.sharing"))