"""
@File    : init_db.py
@Author  : Bobo
@Blog    : https://blog.csdn.net/chinagaobo
@Note    : This code is for learning and communication purposes only
"""

from app import app, db
from models import User, Group, Member, Score
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 1. 创建管理员账号
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

        try:
            # 2. 创建评委账号
            judges = [
                {'username': 'judge1', 'password': 'judge123', 'role': 'judge'},
                {'username': 'judge2', 'password': 'judge123', 'role': 'judge'},
                {'username': 'judge3', 'password': 'judge123', 'role': 'judge'},
                {'username': 'judge4', 'password': 'judge123', 'role': 'judge'},
                {'username': 'judge5', 'password': 'judge123', 'role': 'judge'}
            ]
            
            for judge_data in judges:
                if not User.query.filter_by(username=judge_data['username']).first():
                    judge = User(
                        username=judge_data['username'],
                        password=generate_password_hash(judge_data['password']),
                        role=judge_data['role']
                    )
                    db.session.add(judge)
            
            # 3. 创建分组
            groups = [
                '小学语文组',
                '小学数学组',
                '初中语文组',
                '初中数学组',
                '高中语文组',
                '高中数学组'
            ]
            
            for group_name in groups:
                if not Group.query.filter_by(name=group_name).first():
                    group = Group(name=group_name)
                    db.session.add(group)
            
            db.session.commit()
            
            # 4. 分配评委到分组
            judges = User.query.filter_by(role='judge').all()
            groups = Group.query.all()
            
            # 每个评委分配2-3个组
            for judge in judges:
                judge_groups = groups[:3] if judges.index(judge) < 2 else groups[3:]
                for group in judge_groups:
                    judge.groups.append(group)
            
            # 5. 创建成员
            school_stages = ['小学', '初中', '高中']
            subjects = ['语文', '数学']
            
            for group in groups:
                stage = next(s for s in school_stages if s in group.name)
                subject = next(s for s in subjects if s in group.name)
                
                # 每组添加10个成员
                for i in range(1, 11):
                    exam_number = f"{stage[0]}{subject[0]}{group.id:02d}{i:02d}"
                    member = Member(
                        exam_number=exam_number,
                        name=f"{stage}{subject}学生{i}",
                        school_stage=stage,
                        subject=subject,
                        group=group,
                        notes=f"{stage}{subject}测试成员"
                    )
                    db.session.add(member)
            
            db.session.commit()
            print("数据初始化成功！")
            
            # 6. 添加一些评分记录
            judges = User.query.filter_by(role='judge').all()
            for judge in judges:
                # 获取该评委可评分的所有成员
                for group in judge.groups:
                    members = Member.query.filter_by(group_id=group.id).all()
                    # 随机为一半的成员评分
                    for member in members[:5]:
                        score = Score(
                            judge_id=judge.id,
                            member_id=member.id,
                            score=75 + (member.id % 20)  # 75-94分
                        )
                        db.session.add(score)
            
            db.session.commit()
            print("评分记录添加成功！")
            
        except Exception as e:
            print(f"初始化数据时出错: {e}")
            db.session.rollback()

if __name__ == '__main__':
    init_db()


