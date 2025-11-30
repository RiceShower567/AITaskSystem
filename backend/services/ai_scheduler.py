import os
import json
import openai
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import pytz

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

# 时区设置
DEFAULT_TIMEZONE = pytz.timezone('Asia/Shanghai')
class Task(BaseModel):
    id: int
    title: str
    type: str = Field(..., description="任务类型: 'regular'(常规) 或 'dynamic'(动态)")
    priority: Optional[str] = Field(None, description="优先级: 'high', 'medium', 'low'")
    estimated_time: Optional[int] = Field(None, description="预计完成时间(分钟)")
    deadline: Optional[str] = Field(None, description="截止日期时间")
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    location: Optional[str] = Field(None, description="任务地点")
    repeat_rule: Optional[str] = Field(None, description="重复规则: 'once', 'daily', 'weekly'")
    completed: bool = Field(False, description="任务是否已完成")
    tags: Optional[List[str]] = Field(None, description="任务标签")
    created_at: Optional[str] = Field(None, description="任务创建时间")
    completed_at: Optional[str] = Field(None, description="任务完成时间")

class ScheduleItem(BaseModel):
    task_id: int
    title: str
    start_time: str
    end_time: str
    priority_score: float
    confidence: float

class AIScheduler:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OPENAI_API_KEY environment variable not set. Some AI features may not work.")
        
        # 设置默认参数
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.3
        self.timeout = 10  # API调用超时时间（秒）
        
    def calculate_priority_score(self, task: Task, date: str) -> float:
        """计算任务优先级分数"""
        try:
            score = 0.0
            
            # 解析日期并添加时区
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date_obj = DEFAULT_TIMEZONE.localize(date_obj)
            
            # 已完成任务分数为0
            if task.completed:
                return 0.0
            
            # 根据任务类型计算分数
            if task.type == "dynamic":
                # 动态任务基础分数
                priority_scores = {
                    "high": 100,
                    "medium": 60,
                    "low": 30
                }
                score += priority_scores.get(task.priority, 30)
            elif task.type == "regular":
                # 常规任务基础分数
                score += 80
            
            # 截止时间权重
            if task.deadline:
                try:
                    # 处理不同格式的截止时间
                    if 'T' in task.deadline:
                        deadline_obj = datetime.strptime(task.deadline, "%Y-%m-%dT%H:%M:%S")
                    else:
                        deadline_obj = datetime.strptime(task.deadline, "%Y-%m-%d")
                    
                    # 添加时区信息
                    if deadline_obj.tzinfo is None:
                        deadline_obj = DEFAULT_TIMEZONE.localize(deadline_obj)
                    
                    days_until_deadline = (deadline_obj - date_obj).days
                    
                    if days_until_deadline <= 0:
                        score += 150  # 今天或已过期
                    elif days_until_deadline == 1:
                        score += 100  # 明天到期
                    elif days_until_deadline <= 3:
                        score += 50   # 3天内到期
                    elif days_until_deadline <= 7:
                        score += 20   # 一周内到期
                except ValueError as e:
                    logger.warning(f"无效的截止时间格式: {task.deadline}, 错误: {e}")
            
            # 任务耗时权重
            if task.estimated_time:
                if task.estimated_time <= 30:
                    score += 20  # 短时间任务更容易安排
                elif task.estimated_time <= 60:
                    score += 10
                elif task.estimated_time > 180:
                    score -= 10  # 耗时过长的任务减分
            
            # 任务标签权重
            if task.tags:
                # 特殊标签加成
                important_tags = ['assignment', 'exam', 'meeting', 'urgent']
                for tag in task.tags:
                    if tag.lower() in important_tags:
                        score += 15
                        break
            
            logger.debug(f"任务 '{task.title}' 优先级分数: {score:.2f}")
            return score
        except Exception as e:
            logger.error(f"计算任务优先级失败: {e}")
            return 0.0
    
    def find_available_time_slots(self, regular_tasks: List[Task], date: str, 
                                min_duration: int = 30, 
                                working_hours_start: int = 9, 
                                working_hours_end: int = 22) -> List[Dict[str, Any]]:
        """找出指定日期的可用时间槽"""
        try:
            # 解析日期并添加时区
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date_obj = DEFAULT_TIMEZONE.localize(date_obj)
            
            # 获取当天的常规任务
            day_tasks = []
            for task in regular_tasks:
                if task.type == "regular" and not task.completed and self._is_task_on_date(task, date):
                    if task.start_time and task.end_time:
                        try:
                            start_dt = datetime.strptime(task.start_time, "%Y-%m-%dT%H:%M:%S")
                            end_dt = datetime.strptime(task.end_time, "%Y-%m-%dT%H:%M:%S")
                            
                            # 添加时区信息
                            if start_dt.tzinfo is None:
                                start_dt = DEFAULT_TIMEZONE.localize(start_dt)
                            if end_dt.tzinfo is None:
                                end_dt = DEFAULT_TIMEZONE.localize(end_dt)
                            
                            day_tasks.append({
                                "start": start_dt,
                                "end": end_dt,
                                "title": task.title,
                                "id": task.id
                            })
                        except ValueError as e:
                            logger.warning(f"无效的时间格式: 任务'{task.title}', 错误: {e}")
            
            # 按开始时间排序
            day_tasks.sort(key=lambda x: x["start"])
            
            # 定义工作时间范围
            work_start = DEFAULT_TIMEZONE.localize(datetime(date_obj.year, date_obj.month, date_obj.day, working_hours_start, 0))
            work_end = DEFAULT_TIMEZONE.localize(datetime(date_obj.year, date_obj.month, date_obj.day, working_hours_end, 0))
            
            available_slots = []
            current_time = work_start
            
            # 检查每个常规任务之间的空隙
            for task in day_tasks:
                if task["start"] > current_time:
                    # 计算空隙持续时间（分钟）
                    gap_duration = (task["start"] - current_time).total_seconds() / 60
                    if gap_duration >= min_duration:
                        available_slots.append({
                            "start": current_time.strftime("%Y-%m-%dT%H:%M:%S"),
                            "end": task["start"].strftime("%Y-%m-%dT%H:%M:%S"),
                            "duration": gap_duration,
                            "available_for": "dynamic_tasks"
                        })
                current_time = max(current_time, task["end"])
            
            # 检查最后一个任务到工作结束时间的空隙
            if work_end > current_time:
                gap_duration = (work_end - current_time).total_seconds() / 60
                if gap_duration >= min_duration:
                    available_slots.append({
                        "start": current_time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "end": work_end.strftime("%Y-%m-%dT%H:%M:%S"),
                        "duration": gap_duration,
                        "available_for": "dynamic_tasks"
                    })
            
            logger.info(f"为日期 {date} 找到 {len(available_slots)} 个可用时间槽")
            return available_slots
        except Exception as e:
            logger.error(f"查找可用时间槽失败: {e}")
            return []
    
    def _is_task_on_date(self, task: Task, date: str) -> bool:
        """检查任务是否在指定日期发生"""
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        
        if task.repeat_rule == "once" and task.start_time:
            task_date = datetime.strptime(task.start_time.split('T')[0], "%Y-%m-%d")
            return task_date.date() == date_obj.date()
        elif task.repeat_rule == "daily":
            return True
        elif task.repeat_rule == "weekly" and task.start_time:
            task_date = datetime.strptime(task.start_time.split('T')[0], "%Y-%m-%d")
            return task_date.weekday() == date_obj.weekday()
        
        return False
    
    def generate_daily_schedule(self, regular_tasks: List[Task], 
                              dynamic_tasks: List[Task], 
                              date: str) -> List[ScheduleItem]:
        """生成每日日程表"""
        # 过滤出未完成的动态任务
        pending_dynamic_tasks = [task for task in dynamic_tasks 
                                if not task.completed and task.type == "dynamic"]
        
        # 计算优先级分数
        tasks_with_score = [(task, self.calculate_priority_score(task, date)) 
                          for task in pending_dynamic_tasks]
        
        # 按优先级排序
        tasks_with_score.sort(key=lambda x: x[1], reverse=True)
        
        # 找出可用时间槽
        available_slots = self.find_available_time_slots(regular_tasks, date)
        
        # 安排任务
        schedule = []
        
        for task, score in tasks_with_score:
            # 跳过没有预计时间的任务
            if not task.estimated_time:
                continue
            
            # 尝试找到合适的时间槽
            for slot_idx, slot in enumerate(available_slots):
                slot_duration = slot["duration"]
                
                # 检查是否能放入此时间槽
                if slot_duration >= task.estimated_time:
                    # 安排任务在时间槽的开始
                    start_time = datetime.strptime(slot["start"], "%Y-%m-%dT%H:%M:%S")
                    end_time = start_time + timedelta(minutes=task.estimated_time)
                    
                    # 添加到日程
                    schedule.append(ScheduleItem(
                        task_id=task.id,
                        title=task.title,
                        start_time=start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                        end_time=end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                        priority_score=score,
                        confidence=min(1.0, score / 300)  # 归一化置信度
                    ))
                    
                    # 更新可用时间槽
                    if end_time < datetime.strptime(slot["end"], "%Y-%m-%dT%H:%M:%S"):
                        # 时间槽分割为两部分
                        new_slot = {
                            "start": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                            "end": slot["end"],
                            "duration": slot_duration - task.estimated_time
                        }
                        available_slots[slot_idx] = new_slot
                    else:
                        # 时间槽完全占用，移除
                        available_slots.pop(slot_idx)
                    
                    break
        
        # 合并常规任务到最终日程
        all_tasks = schedule.copy()
        
        # 添加常规任务
        for task in regular_tasks:
            if self._is_task_on_date(task, date) and task.start_time and task.end_time:
                all_tasks.append(ScheduleItem(
                    task_id=task.id,
                    title=task.title,
                    start_time=task.start_time,
                    end_time=task.end_time,
                    priority_score=1000,  # 常规任务优先级最高
                    confidence=1.0
                ))
        
        # 按开始时间排序
        all_tasks.sort(key=lambda x: x.start_time)
        
        return all_tasks
    
    async def get_ai_recommendations(self, schedule: List[ScheduleItem], 
                                   tasks: List[Task], 
                                   date: str) -> Dict[str, Any]:
        """通过AI获取日程优化建议"""
        try:
            # 检查API密钥是否设置
            if not self.api_key:
                logger.warning("未设置OpenAI API密钥，返回默认建议")
                return {
                    "success": True,
                    "recommendations": "建议在高优先级任务之间安排短暂休息，保持高效工作状态。优先完成截止日期临近的任务，合理安排工作与休息时间。",
                    "is_default": True
                }
            
            # 准备简化的任务数据以减少token使用
            scheduled_tasks = []
            for item in schedule[:10]:  # 只取前10个任务
                item_dict = item.dict()
                scheduled_tasks.append({
                    "title": item_dict.get("title"),
                    "start_time": item_dict.get("start_time"),
                    "end_time": item_dict.get("end_time"),
                    "priority_score": item_dict.get("priority_score")
                })
            
            # 找出未安排的重要任务
            scheduled_ids = {item.task_id for item in schedule}
            pending_tasks = []
            for task in tasks[:10]:  # 限制数量
                if task.id not in scheduled_ids and not task.completed and task.priority in ["high", "medium"]:
                    task_dict = task.dict()
                    pending_tasks.append({
                        "title": task_dict.get("title"),
                        "priority": task_dict.get("priority"),
                        "estimated_time": task_dict.get("estimated_time"),
                        "deadline": task_dict.get("deadline")
                    })
            
            # 准备精简的提示词
            prompt = f"""
            你是一位高效的日程规划助手。请针对用户的日程提供简洁的优化建议。
            
            日期: {date}
            
            已安排的日程 ({len(schedule)} 个任务):
            {json.dumps(scheduled_tasks, ensure_ascii=False)}
            
            未安排的重要任务 ({len(pending_tasks)} 个):
            {json.dumps(pending_tasks, ensure_ascii=False)}
            
            请提供:
            1. 对当前日程的简要评价
            2. 2-3条具体优化建议
            3. 工作效率提升的小技巧
            
            回答请保持简洁明了，建议要具体可行。
            """
            
            # 调用OpenAI API，添加超时处理
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一位专业的日程规划和时间管理专家。请直接提供建议，不要添加额外的开场白和结束语。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=800,
                    timeout=self.timeout
                )
                
                # 解析响应
                recommendations = response.choices[0].message.content.strip()
                
                logger.info(f"成功获取AI日程建议")
                return {
                    "success": True,
                    "recommendations": recommendations,
                    "is_default": False
                }
                
            except (openai.error.OpenAIError, TimeoutError) as api_error:
                logger.error(f"OpenAI API调用失败: {api_error}")
                return {
                    "success": False,
                    "error": str(api_error),
                    "recommendations": "建议保持工作与休息的平衡，优先处理高优先级任务，避免任务堆积。",
                    "is_default": True
                }
                
        except Exception as e:
            logger.error(f"获取AI建议过程中发生错误: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": "无法获取AI建议，请稍后重试",
                "is_default": True
            }
    
    def analyze_work_patterns(self, tasks: List[Task], days: int = 7) -> Dict[str, Any]:
        """分析用户的工作模式"""
        try:
            now = datetime.now(DEFAULT_TIMEZONE)
            start_date = now - timedelta(days=days)
            
            # 初始化统计数据
            stats = {
                "analysis_period": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": now.strftime("%Y-%m-%d"),
                    "days_analyzed": days
                },
                "total_tasks": len(tasks),
                "total_completed": 0,
                "completion_rate": 0.0,
                "tasks_by_priority": {"high": 0, "medium": 0, "low": 0},
                "tasks_by_type": {"regular": 0, "dynamic": 0},
                "average_completion_time": None,
                "preferred_time_slots": {},
                "weekly_pattern": {},
                "insights": [],
                "suggestions": []
            }
            
            # 过滤时间范围内的任务
            recent_tasks = []
            for task in tasks:
                try:
                    # 尝试根据创建时间过滤
                    if task.created_at:
                        created_dt = datetime.strptime(task.created_at, "%Y-%m-%dT%H:%M:%S")
                        if created_dt.tzinfo is None:
                            created_dt = DEFAULT_TIMEZONE.localize(created_dt)
                        if created_dt >= start_date:
                            recent_tasks.append(task)
                except Exception:
                    # 如果无法解析时间，仍然包含该任务用于基本统计
                    recent_tasks.append(task)
            
            # 分析任务
            completed_tasks = [task for task in recent_tasks if task.completed]
            stats["total_completed"] = len(completed_tasks)
            stats["total_tasks"] = len(recent_tasks)
            
            if recent_tasks:
                stats["completion_rate"] = round(len(completed_tasks) / len(recent_tasks) * 100, 2)
            
            # 按优先级和类型统计
            for task in recent_tasks:
                if task.priority in stats["tasks_by_priority"]:
                    stats["tasks_by_priority"][task.priority] += 1
                if task.type in stats["tasks_by_type"]:
                    stats["tasks_by_type"][task.type] += 1
            
            # 分析完成时间
            completion_times = []
            for task in completed_tasks:
                if task.created_at and task.completed_at:
                    try:
                        created_dt = datetime.strptime(task.created_at, "%Y-%m-%dT%H:%M:%S")
                        completed_dt = datetime.strptime(task.completed_at, "%Y-%m-%dT%H:%M:%S")
                        
                        if created_dt.tzinfo is None:
                            created_dt = DEFAULT_TIMEZONE.localize(created_dt)
                        if completed_dt.tzinfo is None:
                            completed_dt = DEFAULT_TIMEZONE.localize(completed_dt)
                        
                        # 计算完成时间（小时）
                        if completed_dt > created_dt:
                            hours_taken = (completed_dt - created_dt).total_seconds() / 3600
                            completion_times.append(hours_taken)
                    except Exception as e:
                        logger.warning(f"解析任务时间失败: {e}")
            
            if completion_times:
                avg_time = sum(completion_times) / len(completion_times)
                stats["average_completion_time"] = round(avg_time, 2)
            
            # 分析时间偏好
            for task in completed_tasks:
                if task.completed_at:
                    try:
                        task_time = datetime.strptime(task.completed_at, "%Y-%m-%dT%H:%M:%S")
                        if task_time.tzinfo is None:
                            task_time = DEFAULT_TIMEZONE.localize(task_time)
                        
                        # 按小时统计
                        hour = task_time.hour
                        stats["preferred_time_slots"][hour] = stats["preferred_time_slots"].get(hour, 0) + 1
                        
                        # 按星期几统计
                        weekday = task_time.strftime('%A')  # 英文星期
                        # 转换为中文星期
                        weekday_map = {
                            'Monday': '周一', 'Tuesday': '周二', 'Wednesday': '周三',
                            'Thursday': '周四', 'Friday': '周五', 'Saturday': '周六', 'Sunday': '周日'
                        }
                        weekday_cn = weekday_map.get(weekday, weekday)
                        stats["weekly_pattern"][weekday_cn] = stats["weekly_pattern"].get(weekday_cn, 0) + 1
                    except Exception as e:
                        logger.warning(f"解析任务时间失败: {e}")
            
            # 生成洞察
            if stats["completion_rate"] >= 80:
                stats["insights"].append("您的任务完成率很高，继续保持！")
            elif stats["completion_rate"] < 50:
                stats["insights"].append("任务完成率偏低，建议优化任务管理策略")
                stats["suggestions"].append("尝试设置更合理的任务截止日期，避免过度承诺")
            
            if stats["tasks_by_priority"].get("high", 0) > stats["tasks_by_priority"].get("medium", 0):
                stats["insights"].append("您有较多高优先级任务，注意工作压力管理")
                stats["suggestions"].append("考虑合理分配任务优先级，避免所有任务都设为高优先级")
            
            # 找出最高产的时间段
            if stats["preferred_time_slots"]:
                most_active_hour = max(stats["preferred_time_slots"], key=stats["preferred_time_slots"].get)
                stats["insights"].append(f"您在{most_active_hour}:00左右工作效率最高")
                stats["suggestions"].append(f"建议在{most_active_hour}:00左右安排重要或需要专注的任务")
            
            # 工作模式建议
            stats["suggestions"].append("建议定期回顾任务完成情况，调整工作计划")
            stats["suggestions"].append("在任务之间安排适当休息，保持长期工作效率")
            
            logger.info(f"完成工作模式分析，分析了{len(recent_tasks)}个任务")
            return stats
        except Exception as e:
            logger.error(f"分析工作模式失败: {e}")
            return {
                "error": str(e),
                "message": "工作模式分析失败，请稍后重试",
                "suggestions": ["确保任务数据包含完整的创建时间和完成时间信息"]
            }

# 导出单例实例
scheduler = AIScheduler()
