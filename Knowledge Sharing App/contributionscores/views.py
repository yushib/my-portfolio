from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Feedbacks, HRReviews, Users, Answers
from analysis import analyze_feedback
from flask_login import login_required, current_user

contributionscores_bp = Blueprint('contributionscores', __name__)

@contributionscores_bp.route('/contribution_scores')
@login_required
def index():
    if not current_user.is_hr:
        return redirect(url_for('mypage.index'))

    # 全ユーザーを取得
    users = Users.query.all()
    report_data = {}

    for user in users:
        # 人事とマネージャーは除外
        if user.is_hr or user.is_manager:
            continue
        
        # 評価確定状況
        evaluation = HRReviews.query.filter_by(user_id=user.user_id).first()
        is_finalized = evaluation.is_finalized if evaluation else False

        # AnswersとFeedbacksをa_idで結合して、全回答データを取得
        combined_data = db.session.query(
            Answers.a_id,
            Answers.a_content,
            Feedbacks.ai_score,
            Feedbacks.revised_score,
            Feedbacks.mgr_comment,
            Feedbacks.hr_comment,
            Feedbacks.is_resolved
        ).outerjoin(Feedbacks, Answers.a_id == Feedbacks.a_id)\
        .filter(Answers.user_id == user.user_id).all()

        total_points = 0
        detail_list = []

        for row in combined_data:
            score = 0
            
            # ロジックの徹底：修正スコア(0以外)があれば優先、なければAIスコア
            if row.revised_score and row.revised_score != 0:
                score = row.revised_score
            elif row.ai_score is not None:
                score = row.ai_score
            else:
                # Feedbacksにレコードが存在しない場合はその場で計算
                ai_res = analyze_feedback(row.a_content or "")
                score = ai_res["ai_score"]

            total_points += (score or 0)
            
            if row.mgr_comment and row.mgr_comment.strip():
                detail_list.append({
                    'a_id': row.a_id,
                    'score': score,
                    'ai_score': row.ai_score,
                    'revised_score': row.revised_score,
                    'mgr_comment': row.mgr_comment.strip(),
                    'hr_comment': row.hr_comment or "",
                    'is_resolved': row.is_resolved
            })

        # マネージャー名を取得
        manager_name_row = db.session.query(Users.user_name).filter_by(dept_id=user.dept_id, is_manager=True).first()
        manager_display_name = manager_name_row[0] if manager_name_row else ""

        report_data[user.user_name] = {
            'user_id': user.user_id,
            'total_points': total_points,
            'is_finalized': is_finalized,
            'manager_name': manager_display_name,
            'details': detail_list
        }

    return render_template('contribution_scores.html', report_data=report_data)

@contributionscores_bp.route('/send_hr_comment', methods=['POST'])
@login_required
def send_hr_comment():
    a_id = request.form.get('a_id', type=int)
    user_id = request.form.get('user_id', type=int)
    hr_comment = request.form.get('hr_comment')
    rejection = Feedbacks.query.filter_by(a_id=a_id).first()
    
    if rejection:
        rejection.hr_comment = hr_comment
        rejection.rejection_reason = hr_comment
        rejection.is_resolved = False
        if not user_id:
            user_id = rejection.user_id
    if user_id:
        evaluation = HRReviews.query.filter_by(user_id=user_id).first()
        if not evaluation:
            evaluation = HRReviews(user_id=user_id)
            db.session.add(evaluation)
        
        evaluation.is_rejection = True
        db.session.commit()
    
    return redirect(url_for('contributionscores.index'))

@contributionscores_bp.route('/finalize_user', methods=['POST'])
@login_required
def finalize_user():
    user_id = request.form.get('user_id', type=int)
    if user_id:
        feedbacks = Feedbacks.query.filter_by(user_id=user_id).all()
        for fb in feedbacks:
            fb.is_resolved = True
            fb.hr_comment = ""
            fb.rejection_reason = ""
    evaluation = HRReviews.query.filter_by(user_id=user_id).first()
    if not evaluation:
        evaluation = HRReviews(user_id=user_id)
        db.session.add(evaluation)
    
    evaluation.is_finalized = True
    evaluation.is_rejection = False
    db.session.commit()
    
    flash('評価を確定しました。')
    return redirect(url_for('contributionscores.index'))