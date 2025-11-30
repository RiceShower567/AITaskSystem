from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.task import RegularTask, DynamicTask, TaskType, RepeatType, PriorityType
from backend.app import db
from datetime import datetime

bp = Blueprint('tasks', __name__)

# 常规任务相关路由
@bp.route('/regular', methods=['POST'])
@jwt_required()
def create_regular_task():
    """创建常规任务"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        task = RegularTask(
            user_id=user_id,
            title=data['title'],
            task_type=TaskType[data['task_type'].upper()] if 'task_type' in data else TaskType.OTHER,
            location=data.get('location'),
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            repeat_type=RepeatType[data['repeat_type'].upper()] if 'repeat_type' in data else RepeatType.SINGLE,
            repeat_details=data.get('repeat_details')
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({"msg": "常规任务创建成功", "task_id": task.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "创建任务失败", "error": str(e)}), 400

@bp.route('/regular', methods=['GET'])
@jwt_required()
def get_regular_tasks():
    """获取用户的所有常规任务"""
    user_id = get_jwt_identity()
    
    # 支持按日期筛选
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = RegularTask.query.filter_by(user_id=user_id)
    
    if start_date:
        query = query.filter(RegularTask.start_time >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(RegularTask.end_time <= datetime.fromisoformat(end_date))
    
    tasks = query.all()
    
    result = []
    for task in tasks:
        result.append({
            'id': task.id,
            'title': task.title,
            'task_type': task.task_type.value,
            'location': task.location,
            'start_time': task.start_time.isoformat(),
            'end_time': task.end_time.isoformat(),
            'repeat_type': task.repeat_type.value,
            'repeat_details': task.repeat_details,
            'created_at': task.created_at.isoformat()
        })
    
    return jsonify(result), 200

@bp.route('/regular/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_regular_task(task_id):
    """更新常规任务"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    task = RegularTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({"msg": "任务不存在或无权限修改"}), 404
    
    try:
        if 'title' in data:
            task.title = data['title']
        if 'task_type' in data:
            task.task_type = TaskType[data['task_type'].upper()]
        if 'location' in data:
            task.location = data['location']
        if 'start_time' in data:
            task.start_time = datetime.fromisoformat(data['start_time'])
        if 'end_time' in data:
            task.end_time = datetime.fromisoformat(data['end_time'])
        if 'repeat_type' in data:
            task.repeat_type = RepeatType[data['repeat_type'].upper()]
        if 'repeat_details' in data:
            task.repeat_details = data['repeat_details']
        
        db.session.commit()
        return jsonify({"msg": "任务更新成功"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "更新任务失败", "error": str(e)}), 400

@bp.route('/regular/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_regular_task(task_id):
    """删除常规任务"""
    user_id = get_jwt_identity()
    
    task = RegularTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({"msg": "任务不存在或无权限删除"}), 404
    
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"msg": "任务删除成功"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "删除任务失败", "error": str(e)}), 400

# 动态任务相关路由
@bp.route('/dynamic', methods=['POST'])
@jwt_required()
def create_dynamic_task():
    """创建动态任务"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        task = DynamicTask(
            user_id=user_id,
            title=data['title'],
            description=data.get('description'),
            priority=PriorityType[data['priority'].upper()] if 'priority' in data else PriorityType.MEDIUM,
            estimated_time=data.get('estimated_time'),
            deadline=datetime.fromisoformat(data['deadline']) if 'deadline' in data else None,
            tags=data.get('tags')
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({"msg": "动态任务创建成功", "task_id": task.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "创建任务失败", "error": str(e)}), 400

@bp.route('/dynamic', methods=['GET'])
@jwt_required()
def get_dynamic_tasks():
    """获取用户的所有动态任务"""
    user_id = get_jwt_identity()
    
    # 支持筛选和排序
    completed = request.args.get('completed')
    priority = request.args.get('priority')
    sort_by = request.args.get('sort_by', 'deadline')  # 默认按截止日期排序
    
    query = DynamicTask.query.filter_by(user_id=user_id)
    
    if completed is not None:
        query = query.filter(DynamicTask.is_completed == (completed.lower() == 'true'))
    if priority:
        query = query.filter(DynamicTask.priority == PriorityType[priority.upper()])
    
    # 排序
    if sort_by == 'deadline':
        query = query.order_by(DynamicTask.deadline.asc() if DynamicTask.deadline is not None else db.nullslast)
    elif sort_by == 'priority':
        query = query.order_by(DynamicTask.priority)
    elif sort_by == 'created_at':
        query = query.order_by(DynamicTask.created_at.desc())
    
    tasks = query.all()
    
    result = []
    for task in tasks:
        result.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority.value,
            'estimated_time': task.estimated_time,
            'deadline': task.deadline.isoformat() if task.deadline else None,
            'tags': task.tags,
            'is_completed': task.is_completed,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        })
    
    return jsonify(result), 200

@bp.route('/dynamic/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_dynamic_task(task_id):
    """更新动态任务"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    task = DynamicTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({"msg": "任务不存在或无权限修改"}), 404
    
    try:
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'priority' in data:
            task.priority = PriorityType[data['priority'].upper()]
        if 'estimated_time' in data:
            task.estimated_time = data['estimated_time']
        if 'deadline' in data:
            task.deadline = datetime.fromisoformat(data['deadline']) if data['deadline'] else None
        if 'tags' in data:
            task.tags = data['tags']
        if 'is_completed' in data:
            task.is_completed = data['is_completed']
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"msg": "任务更新成功"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "更新任务失败", "error": str(e)}), 400

@bp.route('/dynamic/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_dynamic_task(task_id):
    """删除动态任务"""
    user_id = get_jwt_identity()
    
    task = DynamicTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({"msg": "任务不存在或无权限删除"}), 404
    
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"msg": "任务删除成功"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "删除任务失败", "error": str(e)}), 400

@bp.route('/dynamic/<int:task_id>/complete', methods=['PATCH'])
@jwt_required()
def complete_dynamic_task(task_id):
    """标记动态任务为完成状态"""
    user_id = get_jwt_identity()
    
    task = DynamicTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({"msg": "任务不存在或无权限修改"}), 404
    
    try:
        task.is_completed = True
        task.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"msg": "任务已标记为完成"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "操作失败", "error": str(e)}), 400

@bp.route('/dynamic/batch', methods=['POST'])
@jwt_required()
def batch_create_dynamic_tasks():
    """批量创建动态任务"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not isinstance(data, list):
        return jsonify({"msg": "请求数据必须是任务列表"}), 400
    
    created_tasks = []
    try:
        for task_data in data:
            task = DynamicTask(
                user_id=user_id,
                title=task_data['title'],
                description=task_data.get('description'),
                priority=PriorityType[task_data['priority'].upper()] if 'priority' in task_data else PriorityType.MEDIUM,
                estimated_time=task_data.get('estimated_time'),
                deadline=datetime.fromisoformat(task_data['deadline']) if 'deadline' in task_data else None,
                tags=task_data.get('tags')
            )
            db.session.add(task)
            created_tasks.append(task.id)
        
        db.session.commit()
        return jsonify({"msg": "批量创建成功", "created_ids": created_tasks}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "批量创建失败", "error": str(e)}), 400