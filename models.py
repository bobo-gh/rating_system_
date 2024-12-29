# models.py

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# 关联表：用户与组的多对多关系
user_groups = db.Table('user_groups',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    groups = db.relationship('Group', 
                           secondary=user_groups, 
                           lazy='dynamic',
                           backref=db.backref('users', lazy='dynamic'))
    scores = db.relationship('Score', backref='judge', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
        
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role
        }

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_judge(self):
        return self.role == 'judge'

    @property
    def scored_count(self):
        """返回该评��已评分的数量"""
        if not self.is_judge:
            return 0
        # 使用 Score 表直接查询数量
        return Score.query.filter_by(judge_id=self.id).count()

    @property
    def total_to_score(self):
        """返回该评委需要评分的总数"""
        if not self.is_judge:
            return 0
        total = 0
        # 计算所有分配组的成员总数
        for group in self.groups:
            total += Member.query.filter_by(group_id=group.id).count()
        return total

    @property
    def scoring_progress(self):
        """返回评分进度百分比"""
        total = self.total_to_score
        if total == 0:
            return 0
        return round(self.scored_count / total * 100)

    def can_delete(self):
        """检查用户是否可以被删除"""
        return self.username != 'admin' and not self.scores

    def has_scored(self, member_id):
        """检查是否已对某成员评分"""
        return any(score.member_id == member_id for score in self.scores)

    def get_score_for(self, member_id):
        """获取对某成员的评分"""
        score = next((s for s in self.scores if s.member_id == member_id), None)
        return score.score if score else None

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)

    # 关联的成员
    members = db.relationship('Member', backref='group', lazy=True)

class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    exam_number = db.Column(db.String(50), unique=True, nullable=False)  # 考号
    school_stage = db.Column(db.String(50), nullable=False)  # 学段
    subject = db.Column(db.String(100), nullable=False)  # 学科
    name = db.Column(db.String(150), nullable=False)  # 姓名
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)  # 所属组别
    notes = db.Column(db.Text, nullable=True)  # 备注

    # 关联的评分记录
    scores = db.relationship('Score', backref='member', lazy=True)

class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    judge_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    # 设置每个评委对每个成员只能有一个评分记录
    __table_args__ = (db.UniqueConstraint('judge_id', 'member_id', name='_judge_member_uc'),)
