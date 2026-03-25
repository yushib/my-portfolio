from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    user_id = StringField('ユーザーID', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    
    # 属性選択のチェックボックス
    is_manager = BooleanField('マネージャーとしてログイン')
    is_hr = BooleanField('人事部としてログイン')
    
    submit = SubmitField('ログイン')