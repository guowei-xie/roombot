import configparser
import lark_oapi as lark
from lark.calendar import LarkCalendar
from src.utils import convert_date_to_timestamp, convert_date_to_rfc3339
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
# print(rooms)

# room_id = 'omm_dc8b0dae81055b94161f790e37427d1f'
# busy_status = lark_calendar.get_meeting_room_busy_status(room_id, start_time_timestamp, end_time_timestamp)
# print(busy_status)

bitable = LarkBitable()
print(bitable.get_room_config_table())