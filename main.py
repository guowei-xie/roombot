from lark.bitable import LarkBitable
from lark.calendar import LarkCalendar
from time import sleep
from src.logger import logger
from src.helper import parse_task_table, remove_completed_task, preference_selection, room_name_to_room_id

lark_bitable = LarkBitable()
lark_calendar = LarkCalendar()

while True:
    # 获取任务表
    task_table = lark_bitable.get_task_table()
    if not task_table:
        sleep(600)
        continue

    # 获取会议室配置表
    room_config_table = lark_bitable.get_room_config_table()
    if not room_config_table:
        logger.error("会议室配置表为空，请先运行initialize.py初始化会议室配置表!")
        exit()
    
    room_ids = [room["fields"]["room_id"] for room in room_config_table]

    # 解析任务表
    task_list = parse_task_table(task_table)

    # 检查是否有已完成执行的任务，若有则从task_list中移除
    completed_task_list = lark_bitable.get_completed_task_list()
    task_list = remove_completed_task(task_list, completed_task_list)

    # 遍历执行任务
    for task in task_list:
        # 获取任务需求时段内的可用会议室列表
        start_time = task["task_start_time"]
        end_time = task["task_end_time"]
        # 校验时间“结束时间”晚于“开始时间”
        if end_time <= start_time:
            logger.error(f"任务{task['task_id']}的结束时间晚于开始时间，跳过")
            continue

        available_room_ids = lark_calendar.get_meeting_room_available_list(room_ids, start_time, end_time)
        if not available_room_ids:
            continue

        # 会议室选择机制
        preferred_room_ids = room_name_to_room_id(task["preferred_room_ids"], room_config_table)
        selected_room_id = preference_selection(available_room_ids, preferred_room_ids, task["allow_backup_room"])
        if not selected_room_id:
            continue

        # 创建日程
        event_id = lark_calendar.create_calendar_event(task["task_name"], start_time, end_time)
        if not event_id:
            continue

        # 添加会议室
        if not lark_calendar.add_calendar_event_room(event_id, selected_room_id):
            continue

        # 邀请参与人
        lark_calendar.add_calendar_event_user(event_id, task["task_booker_id"])

        # 任务完成记录
        lark_bitable.create_completed_task_record(task, selected_room_id, event_id, room_config_table)
    
    sleep(600)

