from flask import Blueprint, render_template, current_app
from flask_login import login_required
from models import db, Questions, Summaries, Answers
from .summarize import generate_summary

archive_bp = Blueprint('archive', __name__)

@archive_bp.route('/archive')
@login_required
def archive_index():
    archived_questions = Questions.query.filter_by(is_archived=True).order_by(Questions.q_id.desc()).all()

    # 未作成の要約を生成して保存
    for q in archived_questions:
        if Summaries.query.get(q.q_id) is not None:
            continue
        answers = Answers.query.filter_by(q_id=q.q_id).order_by(Answers.created_at.asc()).all()
        if len(answers) > 1:
            summary_text = generate_summary(answers)
            new_summary = Summaries(q_id=q.q_id, summary=summary_text)
            db.session.add(new_summary)
    db.session.commit()

    # Questions と Summaries を結合してテンプレート用リストを作成
    joined = (
        db.session.query(Questions, Summaries)
        .outerjoin(Summaries, Questions.q_id == Summaries.q_id)
        .filter(Questions.is_archived == True)
        .order_by(Questions.deadline.asc(), Questions.q_id.asc())
        .all()
    )

    items = []
    for q, s in joined:
        if s and s.summary:
            summarized_answer = s.summary
        else:
            answer = Answers.query.filter_by(q_id=q.q_id).order_by(Answers.created_at.asc()).first()
            summarized_answer = answer.a_content
            
        items.append({
            'q_id': q.q_id,
            'q_content': q.q_content,
            'summarized_answer': summarized_answer,
            'summary': s.summary if s is not None else None,
            'created_at': q.created_at,
            'is_anonymous': q.is_anonymous,
            'user_id': q.user_id,
            'deadline': q.deadline
        })


    return render_template('archive.html', items=items)