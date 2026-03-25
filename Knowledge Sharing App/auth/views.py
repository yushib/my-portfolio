from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import Users  
from forms import LoginForm

auth_bp = Blueprint('auth', __name__)

# ログイン (welcome)
@auth_bp.route("/", methods=["GET", "POST"])
def welcome():
    form = LoginForm()
    
    if form.validate_on_submit():
        u_id = form.user_id.data
        password = form.password.data
        
        # ユーザーをIDで取得
        user = Users.query.get(int(u_id))
        
        if user is not None and user.check_password(password):
            login_user(user)
            
            # 属性に応じた遷移ロジック
            is_manager_selected = form.is_manager.data
            is_hr_selected = form.is_hr.data
            
            if is_hr_selected and user.is_hr:
                return redirect(url_for("contributionscores.index")) 
            elif is_manager_selected and user.is_manager:
                return redirect(url_for("managers.management"))
            else:
                return redirect(url_for("sharing.sharing"))
        
        flash("認証できません")
    
    return render_template("welcome.html", form=form)

# ログアウト
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ログアウトしました")
    # redirect先は 'Blueprint名.関数名'
    return redirect(url_for('auth.welcome'))