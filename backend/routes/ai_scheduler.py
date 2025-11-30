from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from typing import List

from models.task import RegularTask, DynamicTask
from models.user import User
from services.ai_scheduler import scheduler, Task as SchedulerTask

# 创建蓝图
ai_scheduler_bp = Blueprint('ai_scheduler', __name__)

def convert_to_scheduler_task(task, task_type):
    """将数据库模型转换为调度器任务模型"""
    task_dict = {
        "id": task.id,
        "title": task.title,
        "type": task_type,
        "completed": getattr(task, 'completed', False)
    }
    
    if task_type == "dynamic":
        task_dict["priority"] = task.priority
        task_dict["estimated_time"] = task.estimated_time
        task_dict["deadline"] = task.deadline
        task_dict["tags"] = task.tags
    else:  # regular
        task_dict["start_time"] = task.start_time
        task_dict["end_time"] = task.end_time
        task_dict["location"] = task.location
        task_dict["repeat_rule"] = task.repeat_rule
    
    return SchedulerTask(**task_dict)

@ai_scheduler_bp.route('/generate-schedule', methods=['POST'])
@jwt_required()
def generate_schedule():
    """生成每日日程表"""
    try:
        # 获取用户ID
        user_id = get_jwt_identity()
        
        # 获取请求参数
        data = request.get_json()
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # 验证日期格式
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "日期格式无效，请使用YYYY-MM-DD格式"}), 400
        
        # 获取用户的所有任务
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "用户不存在"}), 404
        
        # 转换任务格式
        regular_tasks = [
            convert_to_scheduler_task(task, "regular") 
            for task in RegularTask.query.filter_by(user_id=user_id).all()
        ]
        
        dynamic_tasks = [
            convert_to_scheduler_task(task, "dynamic") 
            for task in DynamicTask.query.filter_by(user_id=user_id).all()
        ]
        
        # 生成日程
        schedule = scheduler.generate_daily_schedule(regular_tasks, dynamic_tasks, date)
        
        # 转换为JSON可序列化的格式
        schedule_data = [
            {
                "task_id": item.task_id,
                "title": item.title,
                "start_time": item.start_time,
                "end_time": item.end_time,
                "priority_score": item.priority_score,
                "confidence": item.confidence
            }
            for item in schedule
        ]
        
        return jsonify({
            "success": True,
            "date": date,
            "schedule": schedule_data,
            "total_tasks": len(schedule)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_scheduler_bp.route('/get-recommendations', methods=['POST'])
@jwt_required()
async def get_recommendations():
    """获取AI日程优化建议"""
    try:
        # 获取用户ID
        user_id = get_jwt_identity()
        
        # 获取请求参数
        data = request.get_json()
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # 验证日期格式
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "日期格式无效，请使用YYYY-MM-DD格式"}), 400
        
        # 获取用户的所有任务
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "用户不存在"}), 404
        
        # 转换任务格式
        regular_tasks = [
            convert_to_scheduler_task(task, "regular") 
            for task in RegularTask.query.filter_by(user_id=user_id).all()
        ]
        
        dynamic_tasks = [
            convert_to_scheduler_task(task, "dynamic") 
            for task in DynamicTask.query.filter_by(user_id=user_id).all()
        ]
        
        # 生成日程
        schedule = scheduler.generate_daily_schedule(regular_tasks, dynamic_tasks, date)
        
        # 获取所有任务
        all_tasks = regular_tasks + dynamic_tasks
        
        # 获取AI建议
        recommendations = await scheduler.get_ai_recommendations(schedule, all_tasks, date)
        
        return jsonify({
            "success": True,
            "date": date,
            "recommendations": recommendations.get("recommendations", ""),
            "ai_success": recommendations.get("success", False)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_scheduler_bp.route('/analyze-work-patterns', methods=['GET'])
@jwt_required()
def analyze_work_patterns():
    """分析用户工作模式"""
    try:
        # 获取用户ID
        user_id = get_jwt_identity()
        
        # 获取用户的所有任务
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "用户不存在"}), 404
        
        # 转换任务格式
        regular_tasks = [
            convert_to_scheduler_task(task, "regular") 
            for task in RegularTask.query.filter_by(user_id=user_id).all()
        ]
        
        dynamic_tasks = [
            convert_to_scheduler_task(task, "dynamic") 
            for task in DynamicTask.query.filter_by(user_id=user_id).all()
        ]
        
        all_tasks = regular_tasks + dynamic_tasks
        
        # 分析工作模式
        patterns = scheduler.analyze_work_patterns(all_tasks, days=14)  # 分析最近14天
        
        return jsonify({
            "success": True,
            "patterns": patterns
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_scheduler_bp.route('/get-weekly-schedule', methods=['POST'])
@jwt_required()
def get_weekly_schedule():
    """获取周计划"""
    try:
        # 获取用户ID
        user_id = get_jwt_identity()
        
        # 获取请求参数
        data = request.get_json()
        start_date_str = data.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        
        # 验证日期格式
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "日期格式无效，请使用YYYY-MM-DD格式"}), 400
        
        # 获取用户的所有任务
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "用户不存在"}), 404
        
        # 转换任务格式
        regular_tasks = [
            convert_to_scheduler_task(task, "regular") 
            for task in RegularTask.query.filter_by(user_id=user_id).all()
        ]
        
        dynamic_tasks = [
            convert_to_scheduler_task(task, "dynamic") 
            for task in DynamicTask.query.filter_by(user_id=user_id).all()
        ]
        
        # 生成一周的日程
        weekly_schedule = {}
        total_tasks = 0
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            
            schedule = scheduler.generate_daily_schedule(regular_tasks, dynamic_tasks, date_str)
            total_tasks += len(schedule)
            
            # 转换为JSON可序列化的格式
            schedule_data = [
                {
                    "task_id": item.task_id,
                    "title": item.title,
                    "start_time": item.start_time,
                    "end_time": item.end_time,
                    "priority_score": item.priority_score,
                    "confidence": item.confidence
                }
                for item in schedule
            ]
            
            weekly_schedule[date_str] = schedule_data
        
        return jsonify({
            "success": True,
            "start_date": start_date_str,
            "end_date": (start_date + timedelta(days=6)).strftime('%Y-%m-%d'),
            "weekly_schedule": weekly_schedule,
            "total_tasks": total_tasks
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
