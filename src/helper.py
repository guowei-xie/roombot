from datetime import datetime

def parse_task_table(task_table):
    """
    解析任务表，转换为可具体执行的任务清单
    计算下个预定任务的开始和结束时间，计算规则：
    按循环周期（每X周）和首次日程预定时间计算下一次预定的开始和结束时间(因系统限制只能预定7天内，例如：本周一最多可以预定下周一的日程)
    但有特殊情况，如果当前日期是预定日期，且当前时间仍然早于预定开始时间，则需要返回两个预定时间，一个是今日的，一个是最近周期的
    task_table入参示例：
    List[{'record_id': 'recKUulP4I', 'fields': {'任务ID': 'ID0011', '任务状态': 'ON', '优先预定偏好会议室': ['ABAP-5层'], '允许预定非偏好会议室': 'YES', '循环周期': '每1周', '日程开始时间': 1753354800000, '日程标题': '测试日程2', '日程结束时间': 1753358400000, '预订人': {'email': 'xieguowei@hetao101.com', 'en_name': '谢国伟', 'id': 'ou_8f488557edeea80bf46d88f74b13b7c6', 'name': '谢国伟'}}}, {'record_id': 'recfwgojze', 'fields': {'任务ID': 'ID0012', '任务状态': 'ON', '循环周期': '每1周', '日程开始时间': 1753356600000, '日程标题': '测试日程3', '日程结束时间': 1753358400000, '预订人': {'email': 'xieguowei@hetao101.com', 'en_name': '谢国伟', 'id': 'ou_8f488557edeea80bf46d88f74b13b7c6', 'name': '谢国伟'}}}]
    """
    if not task_table:
        return []
    
    task_list = []
    for task in task_table:
        task_start_time = task["fields"]["日程开始时间"]
        task_end_time = task["fields"]["日程结束时间"]
        task_cycle = task["fields"]["循环周期"]
        task_cycle_num = int(task_cycle.split("每")[1][:-1])

        task_duration = task_end_time - task_start_time
        task_start_date = datetime.fromtimestamp(task_start_time / 1000).date()

        # 当前时间
        current_time = datetime.now().timestamp() * 1000 # 当前时间戳毫秒
        current_date = datetime.fromtimestamp(current_time / 1000).date() # 当前日期

        # 计算从第一次日程到当前时间经过了多少个完整的循环周期（考虑当前日期可能在首次预定之前）
        if current_time < task_start_time:
            cycle_count = 0
        else:
            # 计算从第一次日程到当前日期经过了多少个完整的循环周期
            cycle_count = (current_date - task_start_date).days // (task_cycle_num * 7)

        # 计算下个预定任务的开始和结束时间
        next_task_start_time_t0 = task_start_time + cycle_count * task_cycle_num * 7 * 24 * 60 * 60 * 1000
        next_task_end_time_t0 = next_task_start_time_t0 + task_duration
        next_task_start_date_t0 = datetime.fromtimestamp(next_task_start_time_t0 / 1000).date()
        next_task_start_time_t1 = task_start_time + (cycle_count + 1) * task_cycle_num * 7 * 24 * 60 * 60 * 1000
        next_task_end_time_t1 = next_task_start_time_t1 + task_duration
        next_task_start_date_t1 = datetime.fromtimestamp(next_task_start_time_t1 / 1000).date()

        # 分别计算t0和t1的开始时间与当前日期的天数差
        t0_days_diff = (next_task_start_date_t0 - current_date).days
        t1_days_diff = (next_task_start_date_t1 - current_date).days

        # 判断t0和t1的开始时间晚于当前时间，如果早于则无需预定，如果晚于则需要预定(注意数据类型一致)
        is_t0_later_than_current = next_task_start_time_t0 > int(current_time)
        is_t1_later_than_current = next_task_start_time_t1 > int(current_time)

        # 返回晚于当前时间的，且距离天数<=7天的任务信息
        if is_t0_later_than_current and t0_days_diff <= 7:
            task_list.append({
                "task_id": task["fields"]["任务ID"],
                "task_name": task["fields"]["日程标题"],
                "task_start_time": next_task_start_time_t0,
                "task_end_time": next_task_end_time_t0,
                "preferred_room_ids": task["fields"].get("优先预定偏好会议室", []),
                "allow_backup_room": task["fields"].get("允许预定非偏好会议室", "YES")
            })

        if is_t1_later_than_current and t1_days_diff <= 7:
            task_list.append({
                "task_id": task["fields"]["任务ID"],
                "task_name": task["fields"]["日程标题"],
                "task_start_time": next_task_start_time_t1,
                "task_end_time": next_task_end_time_t1,
                "preferred_room_ids": task["fields"].get("优先预定偏好会议室", []),
                "allow_backup_room": task["fields"].get("允许预定非偏好会议室", "YES")
            })

    return task_list
    
    
def remove_completed_task(task_list, completed_task_list):
    """
    移除已完成的任务
    已完成任务表中，以任务ID、开始时间、结束时间 为唯一标识，如果任务表中存在相同标识的记录，则移除任务表中的记录
    """
    for task in task_list:
        for completed_task in completed_task_list:
            if task["task_id"] == completed_task["fields"]["任务ID"] and task["task_start_time"] == completed_task["fields"]["日程开始时间"] and task["task_end_time"] == completed_task["fields"]["日程结束时间"]:
                task_list.remove(task)
                break
    return task_list


    
    
    

def preference_selection(room_list, preference_room_list, allow_backup_room=True):
    """
    根据可用会议室列表和偏好会议室列表以及是否允许偏好外的预定，选择出最优会议室，并返回会议室ID
    """
    pass
