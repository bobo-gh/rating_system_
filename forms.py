# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SelectMultipleField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Optional
from models import Group

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 150)])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

class UserForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(message='请输入用户名'),
        Length(min=3, max=20, message='用户名长度必须在3-20个字符之间')
    ])
    password = PasswordField('密码', validators=[
        Optional(),  # 编辑时密码可选
        Length(min=8, message='密码长度至少8个字符')
    ])
    role = SelectField('角色', choices=[
        ('judge', '评委'),
        ('admin', '管理员')
    ], validators=[DataRequired(message='请选择角色')])
    groups = SelectMultipleField('可评组', coerce=int)  # 移除验证器，在视图中处理

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        # 动态加载分组选项
        self.groups.choices = [(g.id, g.name) for g in Group.query.all()]

class GroupForm(FlaskForm):
    name = StringField('分组名称', validators=[DataRequired(), Length(1, 150)])
    submit = SubmitField('提交')

class MemberForm(FlaskForm):
    exam_number = StringField('考号', validators=[DataRequired(), Length(1, 50)])
    school_stage = StringField('学段', validators=[DataRequired(), Length(1, 50)])
    subject = StringField('学科', validators=[DataRequired(), Length(1, 100)])
    name = StringField('姓名', validators=[DataRequired(), Length(1, 150)])
    group = SelectField('所属分组', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('备注')
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)
        self.group.choices = [(group.id, group.name) for group in Group.query.all()]

class UploadForm(FlaskForm):
    data_type = SelectField('数据类型', choices=[('judge', '评委'), ('member', '被评人')], validators=[DataRequired()])
    file = FileField('上传文件', validators=[DataRequired()])
    submit = SubmitField('上传')