from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import db, Users, Questions, Answers, Feedbacks, HRReviews
from analysis import analyze_feedback

managers_bp = Blueprint('managers', __name__)

@managers_bp.route('/management')
@login_required
def management():
    manager_member_map = {1: [5, 6, 7], 2: [8, 9, 10, 11, 12, 13, 14], 3: [15, 16, 17, 18, 19, 20]}
    manager_id = current_user.user_id
    if manager_id not in manager_member_map:
        return redirect(url_for('auth.welcome'))
    
    member_ids = manager_member_map.get(manager_id, [])
    member_id = request.args.get('member_id', type=int)
    if not member_id or member_id not in member_ids:
        member_id = member_ids[0] if member_ids else None
    
    members = db.session.query(
        Users.user_id,
        Users.user_name,
        db.func.coalesce(HRReviews.is_rejection, False).label('is_rejection')
    ).outerjoin(HRReviews, Users.user_id == HRReviews.user_id)\
    .filter(Users.user_id.in_(member_ids)).all()
    
    contribution_data = db.session.query(
        Questions.q_id, 
        Questions.q_content, 
        Answers.a_id, 
        Answers.a_content, 
        Feedbacks.feedback 
    ).join(Answers, Questions.q_id == Answers.q_id)\
    .outerjoin(Feedbacks, Answers.a_id == Feedbacks.a_id)\
    .filter(Answers.user_id == member_id).all()
    
    return render_template('contribution_management.html', members=members, contribution_data=contribution_data, member_id=member_id)

@managers_bp.route('/analysis')
@login_required
def analysis():
    manager_member_map = {1: [5, 6, 7], 2: [8, 9, 10, 11, 12, 13, 14], 3: [15, 16, 17, 18, 19, 20]}
    manager_id = current_user.user_id
    if manager_id not in manager_member_map:
        return redirect(url_for('auth.welcome'))

    member_ids = manager_member_map.get(manager_id, [])
    user_id = request.args.get('member_id', type=int)
    if not user_id or user_id not in member_ids:
        user_id = member_ids[0] if member_ids else None

    raw_data = db.session.query(
        Users.user_name,
        Answers.a_id,
        Feedbacks.feedback,
        Feedbacks.ai_score,
        Feedbacks.revised_score,
        Feedbacks.mgr_comment,
        Feedbacks.hr_comment,
        Feedbacks.rejection_reason
    ).select_from(Answers)\
    .join(Users, Users.user_id == Answers.user_id)\
    .outerjoin(Feedbacks, Answers.a_id == Feedbacks.a_id)\
    .filter(Answers.user_id == user_id).all()

    report_data = {}

    for row in raw_data:
        name = row.user_name
        if name not in report_data:
            report_data[name] = {"total_points": 0, "details": []}
        
        # AI分析で最新の ai_score を算出
        ai_res = analyze_feedback(row.feedback or "")
        ai_score = ai_res["ai_score"]

        if row.revised_score and row.revised_score != 0:
            score = row.revised_score
        else:
            score = ai_score
        f_status = Feedbacks.query.filter_by(a_id=row.a_id).first()        
        is_resolved_val = f_status.is_resolved if f_status else False

        # 合計スコアの計算
        report_data[name]["total_points"] += (score or 0)

        # 詳細データを追加 
        report_data[name]["details"].append({
            "a_id": row.a_id,
            "ai_score": ai_score,
            "feedback": row.feedback,
            "revised_score": row.revised_score,
            "mgr_comment": row.mgr_comment,
            "is_rejection": bool(row.rejection_reason or row.hr_comment),
            "hr_comment": row.hr_comment,
            "is_resolved": is_resolved_val
        })

        # DB側のテーブルも同期
        f = Feedbacks.query.filter_by(a_id=row.a_id).first()
        if f:
            f.ai_score = ai_score
            f.sentiment = ai_res["sentiment"]

    db.session.commit()
    evaluation = HRReviews.query.filter_by(user_id=user_id).first()
    is_finalized_val = evaluation.is_finalized if evaluation else False
    for name in report_data:
        report_data[name]["is_finalized"] = is_finalized_val
    return render_template('analysis.html', report_data=report_data, current_member_id=user_id)

@managers_bp.route('/revise_score', methods=['POST'])
@login_required
def revise_score():
    a_id = request.form.get('a_id', type=int)
    revised_score = request.form.get('revised_score', type=int)
    mgr_comment = request.form.get('mgr_comment')
    member_id = request.form.get('member_id', type=int)
    
    feedbacks = Feedbacks.query.filter_by(a_id=a_id).first()
    if feedbacks:
        if feedbacks.hr_comment and feedbacks.hr_comment.strip() != "":
            feedbacks.hr_comment = None
            feedbacks.rejection_reason = None
        
            review = HRReviews.query.filter_by(user_id=member_id).first()
            if review:
                review.is_rejection = False

        feedbacks.revised_score = revised_score
        feedbacks.mgr_comment = mgr_comment
        feedbacks.is_resolved = False
        
        
        db.session.commit()
    
    return redirect(url_for('managers.analysis', member_id=member_id))