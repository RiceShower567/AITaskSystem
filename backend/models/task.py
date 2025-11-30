from backend.app import db
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Enum

class TaskType(PyEnum):
    COURSE = 'course'
    MEETING = 'meeting'
    PERSONAL = 'personal'
    OTHER = 'other'

class RepeatType(PyEnum):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    SINGLE = 'single'

class PriorityType(PyEnum):
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

class RegularTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    task_type = db.Column(Enum(TaskType), default=TaskType.OTHER)
    location = db.Column(db.String(200))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    repeat_type = db.Column(Enum(RepeatType), default=RepeatType.SINGLE)
    repeat_details = db.Column(db.String(500))  # 存储重复规则的详细信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DynamicTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(Enum(PriorityType), default=PriorityType.MEDIUM)
    estimated_time = db.Column(db.Integer)  # 预计耗时（分钟）
    deadline = db.Column(db.DateTime)
    tags = db.Column(db.String(500))  # 用逗号分隔的标签
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)