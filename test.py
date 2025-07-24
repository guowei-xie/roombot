import configparser
import lark_oapi as lark
from lark.calendar import LarkCalendar
from src.utils import convert_date_to_timestamp, convert_timestamp_to_rfc3339
from lark.bitable import LarkBitable

# 读取配置文件config.ini
# config = configparser.ConfigParser()
# config.read('config.ini')

# 获取飞书配置项
# appId = config['LARK']['appId']
# appSecret = config['LARK']['appSecret']
# logLevel = config['LARK']['logLevel']

# logLevel = {
#     'DEBUG': lark.LogLevel.DEBUG,
#     'INFO': lark.LogLevel.INFO,
#     'WARNING': lark.LogLevel.WARNING,
#     'ERROR': lark.LogLevel.ERROR
# }.get(logLevel, lark.LogLevel.INFO)


# lark_calendar = LarkCalendar()
# events = lark_calendar.get_calendar_events_list()
# print(events)

# start_time = '2025-07-16 15:00:00'
# end_time = '2025-07-16 19:00:00'
# start_time_timestamp = convert_date_to_timestamp(start_time)
# end_time_timestamp = convert_date_to_timestamp(end_time)

# print(start_time_timestamp, end_time_timestamp)

# lark_calendar.create_calendar_event("测试日程3", start_time_timestamp, end_time_timestamp)

# rooms = lark_calendar.get_meeting_room_list()


# room_levels = lark_calendar.get_meeting_room_level_list()
# print(rooms)

# room_id = 'omm_dc8b0dae81055b94161f790e37427d1f'
# busy_status = lark_calendar.get_meeting_room_busy_status(room_id, start_time_timestamp, end_time_timestamp)
# print(busy_status)

# bitable = LarkBitable()
# print(bitable.get_room_config_table())

# # 测试列表转fields
# if __name__ == "__main__":
#     list_dict = [
#         {'room_id': 'omm_dc8b0dae81055b94161f790e37427d1f', 'room_name': 'ABAP-5层'},
#         {'room_id': 'omm_aaa303b2d610e7894ac66878f1debce4', 'room_name': 'APEX-5层'},
#         {'room_id': 'omm_00a501530e217816bb9006af79efa712', 'room_name': 'AWK-5层'},
#     ]
#     bitable = LarkBitable()
#     fields = bitable.list_to_fields(list_dict)
#     print(fields)


# 示例使用

lark_bitable = LarkBitable()

# list_dict = [
#         {'room_id': 'omm_dc8b0dae81055b94161f790e37427d1f', 'room_name': 'ABAP-5层'},
#         {'room_id': 'omm_aaa303b2d610e7894ac66878f1debce4', 'room_name': 'APEX-5层'},
#         {'room_id': 'omm_00a501530e217816bb9006af79efa712', 'room_name': 'AWK-5层'},
#     ]

# lark_bitable.update_room_config_table(list_dict)

# 获取任务表
task_table = lark_bitable.get_task_table()
print(task_table)
# room_config_table = lark_bitable.get_room_config_table()
# print(room_config_table)

# res = convert_timestamp_to_rfc3339(1752591600000)
# print(res)
