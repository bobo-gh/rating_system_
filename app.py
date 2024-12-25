# app.py

from flask import Flask, render_template, redirect, url_for, request, flash, send_file, send_from_directory, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from config import Config
from models import db, User, Group, Member, Score, user_groups
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, UploadForm, UserForm, GroupForm, MemberForm
import pandas as pd
import os
from io import BytesIO
from functools import wraps
import jwt
from datetime import datetime, timedelta
from flask_cors import CORS
from os import environ

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
db.init_app(app)

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL', Config.SQLALCHEMY_DATABASE_URI)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# JWT token验证装饰器 - 确保这个定义在最前面
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        
        if not token:
            return jsonify({'code': 401, 'msg': '缺少token'}), 401
        
        try:
            data = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'code': 401, 'msg': '无效的token'}), 401
        except:
            return jsonify({'code': 401, 'msg': 'token已过期或无效'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# 加载用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
        admin = User(username='admin', password='admin123', role='admin')  # 明文密码
        db.session.add(admin)

        # 添加评委用户
        judge1 = User(username='judge1', password='judge123', role='judge')
        judge2 = User(username='judge2', password='judge123', role='judge')
        db.session.add(judge1)
        db.session.add(judge2)

        # 添加分组
        group_a = Group(name='组A')
        group_b = Group(name='组B')
        db.session.add(group_a)
        db.session.add(group_b)

        # 提交分组以获取ID
        db.session.commit()

        # 添加评委与组的关联
        judge1.groups.append(group_a)
        judge2.groups.append(group_b)

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


# ------------------ 路由定义 ------------------

# 路由: 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:  # 直接比较明文密码
            login_user(user, remember=False)  # 不记住登录状态
            flash('登录成功!', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'danger')
    return render_template('login.html', form=form)


# 路由: 登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已登出', 'info')
    return redirect(url_for('login'))


# 路由: 首页
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


# ------------------ 管理员管理用户 ------------------

@app.route('/admin/manage_users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    users = User.query.all()
    groups = Group.query.all()
    return render_template('admin/manage_users.html', users=users, groups=groups)


# 添加初始化数据路由
@app.route('/admin/initialize_data', methods=['GET', 'POST'])
@login_required
def initialize_data():
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        if 'judge_file' not in request.files or 'member_file' not in request.files:
            flash('请上传评委和被评人文件', 'danger')
            return redirect(request.url)

        judge_file = request.files['judge_file']
        member_file = request.files['member_file']

        if judge_file.filename == '' or member_file.filename == '':
            flash('请选择文件', 'danger')
            return redirect(request.url)

        try:
            # 只删除评分记录和成员数据，保留管理员和分组
            Score.query.delete()
            Member.query.delete()
            # 只删除评委用户，保留管理员
            User.query.filter_by(role='judge').delete()
            db.session.commit()

            # 读取并处理评委数据
            judge_df = pd.read_excel(judge_file)
            
            # 检查必要的列是否存在
            required_judge_columns = {'username', 'password', 'role', 'group_ids'}
            missing_columns = required_judge_columns - set(judge_df.columns)
            if missing_columns:
                flash(f'评委文件缺少以下必要列：{", ".join(missing_columns)}', 'danger')
                return redirect(request.url)

            # 使用字典跟踪已创建的用户
            created_users = {}
            
            for index, row in judge_df.iterrows():
                # 跳过空行
                if any(pd.isna(row[col]) for col in ['username', 'password', 'role', 'group_ids']):
                    continue

                username = row['username']
                if username in created_users:
                    # 如果用户已存在，只添加新的分组关系
                    user = created_users[username]
                else:
                    # 创建新用户
                    user = User(
                        username=username,
                        password=row['password'],
                        role=row['role']
                    )
                    db.session.add(user)
                    created_users[username] = user
                
                # 处理分组关系
                group_ids = str(row['group_ids']).split(',')
                for gid in group_ids:
                    gid = gid.strip()
                    if gid.isdigit():
                        group = Group.query.get(int(gid))
                        if group and group not in user.groups:
                            user.groups.append(group)

            db.session.commit()

            # 读取并处理被评人数据
            member_df = pd.read_excel(member_file)
            
            # 检查必要的列是否存在
            required_member_columns = {'exam_number', 'school_stage', 'subject', 'name', 'group_id', 'notes'}
            missing_columns = required_member_columns - set(member_df.columns)
            if missing_columns:
                flash(f'被评人文件缺少以下必要列：{", ".join(missing_columns)}', 'danger')
                return redirect(request.url)

            # 获取所有分组
            groups = {str(group.id): group for group in Group.query.all()}
            
            # 使用字典跟踪已创建的成员
            created_members = {}
            skipped_count = 0
            
            for index, row in member_df.iterrows():
                # 检查必要字段是否为空
                if any(pd.isna(row[col]) for col in ['exam_number', 'name', 'school_stage', 'subject', 'group_id']):
                    skipped_count += 1
                    continue

                exam_number = str(row['exam_number'])
                group_id = str(row['group_id'])
                
                # 检查分组是否存在
                if group_id not in groups:
                    flash(f'分组ID "{group_id}" 不存在，请先创建该分组', 'warning')
                    continue

                # 检查成员是否已存在
                if exam_number not in created_members:
                    member = Member.query.filter_by(exam_number=exam_number).first()
                    if not member:
                        member = Member(
                            exam_number=exam_number,
                            name=row['name'],
                            school_stage=row['school_stage'],
                            subject=row['subject'],
                            group=groups[group_id],
                            notes=row.get('notes', '')
                        )
                        db.session.add(member)
                        created_members[exam_number] = member

            db.session.commit()
            success_count = len(created_members)
            if success_count > 0:
                flash(f'成功导入 {success_count} 条记录', 'success')
            if skipped_count > 0:
                flash(f'跳过 {skipped_count} 条无效记录', 'info')

            flash('数据初始化成功', 'success')
            return redirect(url_for('manage_users'))

        except Exception as e:
            db.session.rollback()
            flash(f'数据初始化失败: {str(e)}', 'danger')
            return redirect(request.url)

    return render_template('admin/initialize_data.html')


@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    
    form = UserForm()
    if form.validate_on_submit():
        # 检查用户名是否已存在
        if User.query.filter_by(username=form.username.data).first():
            flash('用户名已存在', 'danger')
            return render_template('admin/add_user.html', form=form)
        
        # 创建新用户
        user = User(
            username=form.username.data,
            password=form.password.data,
            role=form.role.data
        )
        
        # 如果是评委，必须选择分组；如果是管理员，不能选择分组
        if form.role.data == 'judge':
            if not form.groups.data:
                flash('评委必须至少选择一个分组', 'danger')
                return render_template('admin/add_user.html', form=form)
            user.groups = Group.query.filter(Group.id.in_(form.groups.data)).all()
        else:  # 管理员
            user.groups = []  # 确保管理员没有分组
        
        db.session.add(user)
        db.session.commit()
        flash('用户添加成功', 'success')
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
    
    if request.method == 'GET':
        form.groups.data = [group.id for group in user.groups]
    
    if form.validate_on_submit():
        # 检查用户名是否被其他用户使用
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user and existing_user.id != user.id:
            flash('用户名已存在', 'danger')
            return render_template('admin/edit_user.html', form=form, user=user)
        
        user.username = form.username.data
        if form.password.data:  # 只有在提供新密码时才更新
            user.password = form.password.data
        
        # 理角色和分组
        user.role = form.role.data
        if user.role == 'judge':
            if not form.groups.data:
                flash('评委必须至少选择一个分组', 'danger')
                return render_template('admin/edit_user.html', form=form, user=user)
            user.groups = Group.query.filter(Group.id.in_(form.groups.data)).all()
        else:  # 管理员
            user.groups = []  # 确保管理员没有分组
        
        db.session.commit()
        flash('用户信息已更新', 'success')
        return redirect(url_for('manage_users'))
    
    return render_template('admin/edit_user.html', form=form, user=user)


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('无权执行此操作', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if not user.can_delete():
        flash('该用户无法删除', 'danger')
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
    if form.validate_on_submit():
        # 检查考号是否已存在
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
    if request.method == 'GET':
        form.group.data = member.group_id
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
        unique_filename = f"{data_type}_{os.urandom(8).hex()}_{filename}"
        data_dir = os.path.join(app.root_path, 'data')
        os.makedirs(data_dir, exist_ok=True)
        filepath = os.path.join(data_dir, unique_filename)

        try:
            file.save(filepath)
            df = pd.read_excel(filepath)

            if data_type == 'judge':
                required_columns = {'username', 'password', 'role', 'group_ids'}
                if not required_columns.issubset(set(df.columns)):
                    flash('上传的评委文件缺少必要的列：username, password, role, group_ids', 'danger')
                    os.remove(filepath)
                    return redirect(url_for('upload'))

                # 使用字典跟踪已创建的用户
                created_users = {}
                
                for index, row in df.iterrows():
                    if pd.isna(row['username']) or pd.isna(row['password']) or pd.isna(row['role']) or pd.isna(row['group_ids']):
                        continue  # 跳过有缺失字段的行

                    username = row['username']
                    # 检查用户是否已存在
                    user = User.query.filter_by(username=username).first()
                    if not user:
                        user = User(
                            username=username,
                            password=row['password'],
                            role=row['role']
                        )
                        db.session.add(user)
                        db.session.flush()  # 获取用户ID
                    
                    # 处理分组关系
                    group_ids = str(row['group_ids']).split(',')
                    for gid in group_ids:
                        gid = gid.strip()
                        if gid.isdigit():
                            group = Group.query.get(int(gid))
                            if group and group not in user.groups:
                                user.groups.append(group)

                db.session.commit()
                flash('评委数据导入成功', 'success')

            elif data_type == 'member':
                # 检查必要的列
                required_columns = {'exam_number', 'school_stage', 'subject', 'name', 'group_id', 'notes'}
                missing_columns = required_columns - set(df.columns)
                if missing_columns:
                    flash(f'上传的文件缺少以下必要列：{", ".join(missing_columns)}', 'danger')
                    os.remove(filepath)
                    return redirect(url_for('upload'))

                # 获取所有分组
                groups = {str(group.id): group for group in Group.query.all()}
                
                # 使用字典跟踪已创建的成员
                created_members = {}
                skipped_count = 0
                
                for index, row in df.iterrows():
                    # 检查必要字段是否为空
                    if any(pd.isna(row[col]) for col in ['exam_number', 'name', 'school_stage', 'subject', 'group_id']):
                        skipped_count += 1
                        continue

                    exam_number = str(row['exam_number'])
                    group_id = str(row['group_id'])
                    
                    # 检查分组是否存在
                    if group_id not in groups:
                        flash(f'分组ID "{group_id}" 不存在，请先创建该分组', 'warning')
                        continue

                    # 检查成员是否已存在
                    if exam_number not in created_members:
                        member = Member.query.filter_by(exam_number=exam_number).first()
                        if not member:
                            member = Member(
                                exam_number=exam_number,
                                name=row['name'],
                                school_stage=row['school_stage'],
                                subject=row['subject'],
                                group=groups[group_id],
                                notes=row.get('notes', '')
                            )
                            db.session.add(member)
                            created_members[exam_number] = member

                db.session.commit()
                success_count = len(created_members)
                if success_count > 0:
                    flash(f'成功导入 {success_count} 条记录', 'success')
                if skipped_count > 0:
                    flash(f'跳过 {skipped_count} 条无效记录', 'info')

            os.remove(filepath)
            return redirect(url_for('upload'))

        except Exception as e:
            db.session.rollback()
            if os.path.exists(filepath):
                os.remove(filepath)
            flash(f'导入数据时出错: {str(e)}', 'danger')
            return redirect(url_for('upload'))

    return render_template('admin/upload.html', form=form)


# ------------------ 评委评分功能 ------------------

@app.route('/judge/select_group', methods=['GET', 'POST'])
@login_required
def select_group():
    if current_user.role != 'judge':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    
    # 直接使用 groups，因为它已经是列表了
    groups = current_user.groups
    
    if request.method == 'POST':
        group_id = request.form.get('group')
        if group_id:
            return redirect(url_for('rate_members', group_id=group_id))
    
    return render_template('judge/select_group.html', groups=groups)


@app.route('/judge/rate_members/<int:group_id>', methods=['GET', 'POST'])
@login_required
def rate_members(group_id):
    if current_user.role != 'judge':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    
    # 确认该组在评委可评的组内
    group = Group.query.get_or_404(group_id)
    if group not in current_user.groups:
        flash('您无权评估此组', 'danger')
        return redirect(url_for('select_group'))
    
    members = Member.query.filter_by(group_id=group_id).all()
    
    if request.method == 'POST':
        scores_added = False  # 标记是否有新增评分
        
        for member in members:
            score_value = request.form.get(f'score_{member.id}')
            if score_value:
                existing_score = Score.query.filter_by(
                    judge_id=current_user.id, 
                    member_id=member.id
                ).first()
                
                if not existing_score:
                    try:
                        score_int = int(score_value)
                        if 0 <= score_int <= 100:
                            new_score = Score(
                                judge_id=current_user.id,
                                member_id=member.id,
                                score=score_int
                            )
                            db.session.add(new_score)
                            scores_added = True
                        else:
                            flash(f'分数 {score_int} 无效，请输入0到100之间的整数', 'warning')
                            return redirect(request.url)
                    except ValueError:
                        flash(f'分数 {score_value} 无效，请输入整数', 'warning')
                        return redirect(request.url)
        
        if scores_added:
            db.session.commit()
            flash('评分已提交', 'success')
            return redirect(url_for('select_group'))
        else:
            flash('没有新的评分需要提交', 'info')
            return redirect(request.url)
    
    # 获取当前评委对该组成员的评分情况
    member_scores = {}
    scores = Score.query.filter_by(judge_id=current_user.id).all()
    for score in scores:
        member_scores[score.member_id] = score.score
    
    return render_template('judge/rate_members.html', 
                         group=group, 
                         members=members,
                         member_scores=member_scores)


# ------------------ 评分统计 ------------------

@app.route('/admin/statistics')
@login_required
def statistics():
    if current_user.role != 'admin':
        flash('无权访问该页面', 'danger')
        return redirect(url_for('index'))
    
    # 获取筛选参数
    selected_stage = request.args.get('stage', '')
    selected_subject = request.args.get('subject', '')
    
    # 获取所有分组
    groups = Group.query.all()
    statistics_data = []
    
    # 获取所有可选的学段和学科
    all_stages = db.session.query(Member.school_stage.distinct()).all()
    all_subjects = db.session.query(Member.subject.distinct()).all()
    stages = [stage[0] for stage in all_stages]
    subjects = [subject[0] for subject in all_subjects]
    
    for group in groups:
        judges = group.users.filter_by(role='judge').all()
        judge_ids = [judge.id for judge in judges]
        
        # 构建成员查询
        members_query = Member.query.filter_by(group_id=group.id)
        if selected_stage:
            members_query = members_query.filter_by(school_stage=selected_stage)
        if selected_subject:
            members_query = members_query.filter_by(subject=selected_subject)
        
        members = members_query.all()
        
        if members:  # 只添加有成员的分组
            member_stats = []
            for member in members:
                scores = Score.query.filter(
                    Score.member_id == member.id,
                    Score.judge_id.in_(judge_ids)
                ).all()
                judge_scores = {score.judge.username: score.score for score in scores}
                average = sum(judge_scores.values()) / len(judge_scores) if judge_scores else 'N/A'
                member_stats.append({
                    'exam_number': member.exam_number,
                    'school_stage': member.school_stage,
                    'subject': member.subject,
                    'name': member.name,
                    'notes': member.notes,
                    'scores': judge_scores,
                    'average': round(average, 2) if isinstance(average, float) else average
                })
            
            if member_stats:  # 只添加有统计数据的分组
                statistics_data.append({
                    'group': group,
                    'judges': judges,
                    'members': member_stats
                })
    
    return render_template(
        'admin/statistics.html',
        data=statistics_data,
        stages=stages,
        subjects=subjects,
        selected_stage=selected_stage,
        selected_subject=selected_subject
    )


# ------------------ 下载模板 ------------------
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

    # 修改目录路径，将 'template_files' 改为 'templates_files'
    directory = os.path.join(app.root_path, 'static', 'templates_files')
    # 检查文件是否存在
    file_path = os.path.join(directory, filename)
    print(file_path)
    return send_from_directory(directory, filename, as_attachment=True)


# ------------------ 导出评分统计为Excel ------------------

@app.route('/admin/export_scores')
@login_required
def export_scores():
    if current_user.role != 'admin':
        flash('无权访问该功能', 'danger')
        return redirect(url_for('index'))

    # Get all group statistics
    groups = Group.query.all()
    statistics_data = []
    for group in groups:
        judges = group.users.filter_by(role='judge').all()
        judge_ids = [judge.id for judge in judges]
        members = group.members
        group_avg_total = 0
        group_avg_count = 0
        member_stats = []
        for member in members:
            scores = Score.query.filter(Score.member_id == member.id, Score.judge_id.in_(judge_ids)).all()
            judge_scores = {score.judge.username: score.score for score in scores}
            average = sum(judge_scores.values()) / len(judge_scores) if judge_scores else 'N/A'
            if isinstance(average, float):
                group_avg_total += average
                group_avg_count += 1
            member_stats.append({
                'exam_number': member.exam_number,
                'school_stage': member.school_stage,
                'subject': member.subject,
                'name': member.name,
                'notes': member.notes,
                'scores': judge_scores,
                'average': round(average, 2) if isinstance(average, float) else average
            })
        group_average = round(group_avg_total / group_avg_count, 2) if group_avg_count > 0 else 'N/A'
        statistics_data.append({
            'group': group,
            'judges': judges,
            'members': member_stats,
            'group_average': group_average
        })

    # Create a DataFrame for all groups
    all_data = []
    for group_data in statistics_data:
        group = group_data['group']
        judges = group_data['judges']
        members = group_data['members']
        for member in members:
            row = {
                '群组': group.name,
                '考号': member['exam_number'],
                '学段': member['school_stage'],
                '学科': member['subject'],
                '姓名': member['name'],
                '备注': member['notes']
            }
            # Add judges' scores
            for judge in judges:
                row[judge.username] = member['scores'].get(judge.username, 'N/A')
            row['平均分'] = member['average']
            all_data.append(row)

    df = pd.DataFrame(all_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='All_Scores')
    output.seek(0)
    return send_file(output, download_name="all_scores.xlsx", as_attachment=True)


@app.route('/admin/export_group_scores/<int:group_id>')
@login_required
def export_group_scores(group_id):
    if current_user.role != 'admin':
        flash('无权访问该功能', 'danger')
        return redirect(url_for('index'))
    
    group = Group.query.get_or_404(group_id)
    judges = group.users.filter_by(role='judge').all()
    judge_ids = [judge.id for judge in judges]
    members = group.members
    all_data = []
    
    for member in members:
        scores = Score.query.filter(
            Score.member_id == member.id,
            Score.judge_id.in_(judge_ids)
        ).all()
        judge_scores = {score.judge.username: score.score for score in scores}
        average = sum(judge_scores.values()) / len(judge_scores) if judge_scores else ''
        
        row = {
            '考号': member.exam_number,
            '学段': member.school_stage,
            '学科': member.subject,
            '姓名': member.name,
            '备注': member.notes
        }
        
        # 使用空字符串替代 'N/A'
        for judge in judges:
            row[judge.username] = judge_scores.get(judge.username, '')
        
        # 如果有平均分则保留两位小数，否则显示空白
        row['平均分'] = round(average, 2) if isinstance(average, (int, float)) else ''
        
        all_data.append(row)
    
    df = pd.DataFrame(all_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=f'{group.name}_Scores')
    output.seek(0)
    filename = f"{group.name}_scores.xlsx"
    return send_file(output, download_name=filename, as_attachment=True)


# ------------------ 主程序入口 ------------------

if __name__ == '__main__':
    # 初始化数据库并插入模拟数据
    with app.app_context():
        if not os.path.exists(os.path.join(app.root_path, 'ratings.db')):
            init_db()
    # 创建数据目录和模板文件目录（如果不存在）
    os.makedirs(os.path.join(app.root_path, 'data'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'static', 'templates_files'), exist_ok=True)
    # 运行Flask应用
    app.run(host='0.0.0.0', port=4262, debug=True)


# 在其他路由前添加
@app.route('/admin/check_username')
@login_required
def check_username():
    if current_user.role != 'admin':
        return jsonify({'available': False, 'error': '无权访问'}), 403
    
    username = request.args.get('username')
    user_id = request.args.get('user_id')  # 用于编辑时排除当前用户
    
    if not username:
        return jsonify({'available': False, 'error': '用户名不能为空'})
    
    query = User.query.filter_by(username=username)
    if user_id:  # 如果是编辑用户，排除当前用户
        query = query.filter(User.id != int(user_id))
    
    existing_user = query.first()
    return jsonify({'available': existing_user is None})


# JWT 配置
JWT_SECRET = os.environ.get('JWT_SECRET', 'generate-a-secure-random-key')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = timedelta(days=30)

def generate_token(user):
    """生成 JWT token"""
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token):
    """验证 JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def mp_login_required(f):
    """小程序接口的登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'code': 401, 'msg': '未登录'})
        
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'code': 401, 'msg': '登录已过期'})
        
        g.user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

# 添加小程序 API 接口
@app.route('/api/login', methods=['POST'])
def mp_login():
    """小程序登录接口"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and user.password == password and user.role == 'judge':
        token = generate_token(user)
        return jsonify({
            'code': 0,
            'msg': '登录成功',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'token': token
            }
        })
    return jsonify({'code': 1, 'msg': '用户名或密码错误'})

@app.route('/api/groups', methods=['GET'])
@token_required
def mp_get_groups():
    """获取评委可评分的组"""
    user = g.current_user
    if not user or user.role != 'judge':
        return jsonify({'code': 1, 'msg': '无权限'})
    
    groups_data = []
    for group in user.groups:
        total = len(group.members)
        scored = len([m for m in group.members if user.has_scored(m.id)])
        groups_data.append({
            'id': group.id,
            'name': group.name,
            'total': total,
            'scored': scored
        })
    
    return jsonify({
        'code': 0,
        'data': groups_data
    })

@app.route('/api/members/<int:group_id>', methods=['GET'])
@token_required
def mp_get_members(group_id):
    """获取指定组的待评成员"""
    user = g.current_user
    if not user or user.role != 'judge':
        return jsonify({'code': 1, 'msg': '无权限'})
    
    group = Group.query.get_or_404(group_id)
    if group not in user.groups:
        return jsonify({'code': 1, 'msg': '无权访问此分组'})
    
    members_data = []
    for member in group.members:
        score = user.get_score_for(member.id)
        members_data.append({
            'id': member.id,
            'exam_number': member.exam_number,
            'name': member.name,
            'school_stage': member.school_stage,
            'subject': member.subject,
            'score': score
        })
    
    return jsonify({
        'code': 0,
        'data': members_data
    })

@app.route('/api/score', methods=['POST'])
@token_required
def mp_submit_score():
    """提交评分"""
    user = g.current_user
    if not user or user.role != 'judge':
        return jsonify({'code': 1, 'msg': '无权限'})
    
    data = request.get_json()
    member_id = data.get('member_id')
    score_value = data.get('score')
    
    if not all([member_id, score_value]):
        return jsonify({'code': 1, 'msg': '参数不完整'})
    
    try:
        score_value = int(score_value)
        if not (0 <= score_value <= 100):
            return jsonify({'code': 1, 'msg': '分数必须在0-100之间'})
    except ValueError:
        return jsonify({'code': 1, 'msg': '分数必须为整数'})
    
    member = Member.query.get_or_404(member_id)
    if member.group not in user.groups:
        return jsonify({'code': 1, 'msg': '无权为此成员评分'})
    
    if user.has_scored(member_id):
        return jsonify({'code': 1, 'msg': '已经评过分了'})
    
    try:
        score = Score(judge_id=user.id, member_id=member_id, score=score_value)
        db.session.add(score)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '评分成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'评分失败: {str(e)}'})
