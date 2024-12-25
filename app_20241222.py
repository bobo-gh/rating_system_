# app.py

from flask import Flask, render_template, redirect, url_for, request, flash, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from config import Config
from models import db, User, Group, Member, Score
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from forms import LoginForm, UploadForm, UserForm, GroupForm, MemberForm
import pandas as pd
import os
from io import BytesIO

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# 加载用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------ 根路由定义 ------------------
@app.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        return redirect(url_for('manage_users'))
    elif current_user.role == 'judge':
        return redirect(url_for('select_group'))
    else:
        flash('无效的用户角色', 'danger')
        return redirect(url_for('logout'))

# ------------------ 数据库初始化函数 ------------------
def init_db():
    """
    初始化数据库：
    - 删除现有数据库文件（如果存在）
    - 创建所有表
    - 插入模拟数据
    """
    with app.app_context():
        db_path = os.path.join(app.root_path, 'ratings.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"已删除现有的数据库文件 '{db_path}'。")
        else:
            print("数据库文件不存在，跳过删除步骤。")

        # 创建所有表
        db.create_all()
        print("数据库表已创建。")

        # 插入模拟数据

        # 添加管理员用户
        admin = User(username='admin', password=generate_password_hash('admin123'), role='admin')
        db.session.add(admin)

        # 添加评委用户
        judge1 = User(username='judge1', password=generate_password_hash('judge123'), role='judge')
        judge2 = User(username='judge2', password=generate_password_hash('judge123'), role='judge')
        db.session.add(judge1)
        db.session.add(judge2)

        # 添加分组
        group_a = Group(name='组A')
        group_b = Group(name='组B')
        db.session.add(group_a)
        db.session.add(group_b)

        # 提交分组以获取ID
        db.session.commit()

        # 添加成员
        member1 = Member(
            exam_number='E001',
            school_stage='初中',
            subject='语文',
            name='张三',
            group_id=group_a.id,
            notes='优秀学生'
        )
        member2 = Member(
            exam_number='E002',
            school_stage='高中',
            subject='数学',
            name='李四',
            group_id=group_b.id,
            notes=''
        )
        db.session.add_all([member1, member2])

        # 提交所有更改
        db.session.commit()
        print("模拟数据已插入。")


@app.route('/admin/statistics')
@login_required
def statistics():
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))

    data = []
    members = Member.query.all()
    judges = User.query.filter_by(role='judge').all()

    for member in members:
        row = {
            '考号': member.exam_number,
            '学段': member.school_stage,
            '学科': member.subject,
            '姓名': member.name,
            '所属分组': member.group.name,
            '备注': member.notes
        }
        total = 0
        count = 0
        for judge in judges:
            score = Score.query.filter_by(judge_id=judge.id, member_id=member.id).first()
            row[judge.username] = score.score if score else 'N/A'
            if score:
                total += score.score
                count += 1
        row['平均分'] = round(total / count, 2) if count > 0 else 'N/A'
        data.append(row)

    return render_template('admin/statistics.html', data=data, judges=judges)

# ------------------ 导出评分统计为Excel ------------------

@app.route('/export_scores')
@login_required
def export_scores():
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))

    data = []
    members = Member.query.all()
    judges = User.query.filter_by(role='judge').all()

    for member in members:
        row = {
            '考号': member.exam_number,
            '学段': member.school_stage,
            '学科': member.subject,
            '姓名': member.name,
            '所属分组': member.group.name,
            '备注': member.notes
        }
        total = 0
        count = 0
        for judge in judges:
            score = Score.query.filter_by(judge_id=judge.id, member_id=member.id).first()
            row[judge.username] = score.score if score else 'N/A'
            if score:
                total += score.score
                count += 1
        row['平均分'] = round(total / count, 2) if count > 0 else 'N/A'
        data.append(row)

    df = pd.DataFrame(data)
    output = BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Scores')

    output.seek(0)
    return send_file(output, attachment_filename="scores.xlsx", as_attachment=True)


# ------------------ 管理员管理用户 ------------------

@app.route('/admin/manage_users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)


@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('用户名已存在', 'warning')
            return redirect(url_for('add_user'))
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            password=hashed_password,
            role=form.role.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('用户已添加', 'success')
        return redirect(url_for('manage_users'))
    return render_template('admin/add_user.html', form=form)


@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if request.method == 'POST' and form.validate_on_submit():
        user.username = form.username.data
        if form.password.data:
            user.password = generate_password_hash(form.password.data)
        user.role = form.role.data
        db.session.commit()
        flash('用户已更新', 'success')
        return redirect(url_for('manage_users'))
    return render_template('admin/edit_user.html', form=form, user=user)


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('无权执行此操作', 'danger')
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash('无法删除管理员账号', 'danger')
        return redirect(url_for('manage_users'))
    db.session.delete(user)
    db.session.commit()
    flash('用户已删除', 'success')
    return redirect(url_for('manage_users'))


# ------------------ 管理员管理分组 ------------------

@app.route('/admin/manage_groups')
@login_required
def manage_groups():
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    groups = Group.query.all()
    return render_template('admin/manage_groups.html', groups=groups)


@app.route('/admin/add_group', methods=['GET', 'POST'])
@login_required
def add_group():
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    form = GroupForm()
    if form.validate_on_submit():
        if Group.query.filter_by(name=form.name.data).first():
            flash('分组名称已存在', 'warning')
            return redirect(url_for('add_group'))
        new_group = Group(name=form.name.data)
        db.session.add(new_group)
        db.session.commit()
        flash('分组已添加', 'success')
        return redirect(url_for('manage_groups'))
    return render_template('admin/add_group.html', form=form)


@app.route('/admin/edit_group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def edit_group(group_id):
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    group = Group.query.get_or_404(group_id)
    form = GroupForm(obj=group)
    if request.method == 'POST' and form.validate_on_submit():
        group.name = form.name.data
        db.session.commit()
        flash('分组已更新', 'success')
        return redirect(url_for('manage_groups'))
    return render_template('admin/edit_group.html', form=form, group=group)


@app.route('/admin/delete_group/<int:group_id>', methods=['POST'])
@login_required
def delete_group(group_id):
    if current_user.role != 'admin':
        flash('无权执行此操作', 'danger')
        return redirect(url_for('index'))
    group = Group.query.get_or_404(group_id)
    if group.members:
        flash('无法删除有成员的分组', 'danger')
        return redirect(url_for('manage_groups'))
    db.session.delete(group)
    db.session.commit()
    flash('分组已删除', 'success')
    return redirect(url_for('manage_groups'))


# ------------------ 管理员管理成员 ------------------

@app.route('/admin/manage_members')
@login_required
def manage_members():
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    members = Member.query.all()
    groups = Group.query.all()
    return render_template('admin/manage_members.html', members=members, groups=groups)


@app.route('/admin/add_member', methods=['GET', 'POST'])
@login_required
def add_member():
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    form = MemberForm()
    form.group.choices = [(g.id, g.name) for g in Group.query.all()]
    if form.validate_on_submit():
        # 检查考号的唯一性
        if Member.query.filter_by(exam_number=form.exam_number.data).first():
            flash('考号已存在，请使用不同的考号。', 'warning')
            return redirect(url_for('add_member'))
        new_member = Member(
            exam_number=form.exam_number.data,
            school_stage=form.school_stage.data,
            subject=form.subject.data,
            name=form.name.data,
            group_id=form.group.data,
            notes=form.notes.data
        )
        db.session.add(new_member)
        db.session.commit()
        flash('成员已添加', 'success')
        return redirect(url_for('manage_members'))
    return render_template('admin/add_member.html', form=form)


@app.route('/admin/edit_member/<int:member_id>', methods=['GET', 'POST'])
@login_required
def edit_member(member_id):
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    member = Member.query.get_or_404(member_id)
    form = MemberForm(obj=member)
    form.group.choices = [(g.id, g.name) for g in Group.query.all()]
    if request.method == 'POST' and form.validate_on_submit():
        # 如果考号被修改，检查其唯一性
        if form.exam_number.data != member.exam_number:
            if Member.query.filter_by(exam_number=form.exam_number.data).first():
                flash('考号已存在，请使用不同的考号。', 'warning')
                return redirect(url_for('edit_member', member_id=member.id))
        member.exam_number = form.exam_number.data
        member.school_stage = form.school_stage.data
        member.subject = form.subject.data
        member.name = form.name.data
        member.group_id = form.group.data
        member.notes = form.notes.data
        db.session.commit()
        flash('成员已更新', 'success')
        return redirect(url_for('manage_members'))
    return render_template('admin/edit_member.html', form=form, member=member)


@app.route('/admin/delete_member/<int:member_id>', methods=['POST'])
@login_required
def delete_member(member_id):
    if current_user.role != 'admin':
        flash('无权执行此操作', 'danger')
        return redirect(url_for('index'))
    member = Member.query.get_or_404(member_id)
    if member.scores:
        flash('无法删除已被评分的成员', 'danger')
        return redirect(url_for('manage_members'))
    db.session.delete(member)
    db.session.commit()
    flash('成员已删除', 'success')
    return redirect(url_for('manage_members'))


# ------------------ 管理员上传数据 ------------------
@app.route('/admin/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))

    form = UploadForm()
    if form.validate_on_submit():
        data_type = form.data_type.data
        file = form.file.data
        filename = secure_filename(file.filename)
        # 生成唯一的文件名，避免冲突
        unique_filename = f"{data_type}_{os.urandom(8).hex()}_{filename}"
        filepath = os.path.join(app.root_path, 'data', unique_filename)

        try:
            # 确保 data 目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            # 保存上传文件
            file.save(filepath)

            # 读取上传的Excel文件
            df = pd.read_excel(filepath)

            if data_type == 'judge':
                # 期望的列：username, password, role
                required_columns = {'username', 'password', 'role'}
                if not required_columns.issubset(set(df.columns)):
                    flash('上传的评委文件缺少必要的列：username, password, role', 'danger')
                    os.remove(filepath)
                    return redirect(url_for('upload'))

                for index, row in df.iterrows():
                    if pd.isna(row['username']) or pd.isna(row['password']) or pd.isna(row['role']):
                        continue  # 跳过有缺失字段的行
                    if User.query.filter_by(username=row['username']).first():
                        continue  # 跳过已存在的用户
                    hashed_password = generate_password_hash(row['password'])
                    user = User(username=row['username'], password=hashed_password, role=row['role'])
                    db.session.add(user)

            elif data_type == 'member':
                # 期望的列：exam_number, school_stage, subject, name, group_id, notes
                required_columns = {'exam_number', 'school_stage', 'subject', 'name', 'group_id'}
                if not required_columns.issubset(set(df.columns)):
                    flash('上传的被评人文件缺少必要的列：exam_number, school_stage, subject, name, group_id', 'danger')
                    os.remove(filepath)
                    return redirect(url_for('upload'))

                for index, row in df.iterrows():
                    if pd.isna(row['exam_number']) or pd.isna(row['school_stage']) or pd.isna(
                            row['subject']) or pd.isna(row['name']) or pd.isna(row['group_id']):
                        continue  # 跳过有缺失字段的行
                    if Member.query.filter_by(exam_number=row['exam_number']).first():
                        continue  # 跳过已存在的成员
                    # 确认 group_id 存在
                    group = Group.query.get(row['group_id'])
                    if not group:
                        flash(f"分组 ID {row['group_id']} 不存在，无法添加成员 '{row['name']}'。", 'warning')
                        continue
                    member = Member(
                        exam_number=row['exam_number'],
                        school_stage=row['school_stage'],
                        subject=row['subject'],
                        name=row['name'],
                        group_id=row['group_id'],
                        notes=row.get('notes', '')  # 如果没有备注，则为空字符串
                    )
                    db.session.add(member)

            else:
                flash('未知的数据类型', 'danger')
                os.remove(filepath)
                return redirect(url_for('upload'))

            db.session.commit()
            flash('数据已成功导入', 'success')

        except Exception as e:
            flash(f'导入数据时出错: {e}', 'danger')

        finally:
            # 确保上传文件被移除
            if os.path.exists(filepath):
                os.remove(filepath)

        return redirect(url_for('index'))

    return render_template('admin/upload.html', form=form)


# ------------------ 评委评分功能 ------------------
@app.route('/judge/select_group', methods=['GET', 'POST'])
@login_required
def select_group():
    if current_user.role != 'judge':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    groups = Group.query.all()
    if request.method == 'POST':
        group_id = request.form.get('group')
        return redirect(url_for('rate_members', group_id=group_id))
    return render_template('judge/select_group.html', groups=groups)


@app.route('/judge/rate_members/<int:group_id>', methods=['GET', 'POST'])
@login_required
def rate_members(group_id):
    if current_user.role != 'judge':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    group = Group.query.get_or_404(group_id)
    members = group.members
    if request.method == 'POST':
        has_errors = False
        for member in members:
            score_value = request.form.get(f'score_{member.id}')
            if score_value:
                existing_score = Score.query.filter_by(judge_id=current_user.id, member_id=member.id).first()
                if not existing_score:
                    try:
                        score_int = int(score_value)
                        if 0 <= score_int <= 100:
                            new_score = Score(judge_id=current_user.id, member_id=member.id, score=score_int)
                            db.session.add(new_score)
                        else:
                            flash(f'分数 {score_int} 无效，请输入0到100之间的整数', 'warning')
                            has_errors = True
                    except ValueError:
                        flash(f'分数 {score_value} 无效，请输入整数', 'warning')
                        has_errors = True
                else:
                    flash(f'您已对成员 "{member.name}" 评分，无法重新评分。', 'warning')
        if not has_errors:
            db.session.commit()
            flash('评分已提交', 'success')
            return redirect(url_for('select_group'))
    return render_template('judge/rate_members.html', group=group, members=members)


# ------------------ 下载模板 ------------------
@app.route('/admin/download_template/<template_type>')
@login_required
def download_template(template_type):
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))

    if template_type == 'judge':
        filename = 'judges_template.xlsx'
    elif template_type == 'member':
        filename = 'members_template.xlsx'
    else:
        flash('未知的模板类型', 'danger')
        return redirect(url_for('upload'))

    directory = os.path.join(app.root_path, 'templates', 'templates_files')  # 假设模板文件存放在 'templates/templates_files'
    return send_from_directory(directory, filename, as_attachment=True)

# ------------------ 主程序入口 ------------------

if __name__ == '__main__':
    # 初始化数据库并插入模拟数据
    # init_db()
    # 运行Flask应用
    app.run(debug=True)