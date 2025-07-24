from lark.bitable import LarkBitable
from lark.calendar import LarkCalendar
from time import sleep
from src.logger import logger

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

    # 解析任务表
    task_list = parse_task_table(task_table)
    for task in task_list:
        # 获取任务需求时段内的可用会议室列表
        start_time = task["start_time"]
        end_time = task["end_time"]
        room_list = [] # 非忙会议室列表
        for room in room_config_table:
            # 检查会议室忙闲状态
            room_id = room["fields"]["room_id"]
            busy_status = lark_calendar.get_meeting_room_busy_status(room_id, start_time, end_time)
            if busy_status:
                continue
            else:
                room_list.append(room_id)

            