"""
初始化会议室配置表
"""

from lark.calendar import LarkCalendar
from lark.bitable import LarkBitable

lark_calendar = LarkCalendar()
lark_bitable = LarkBitable()

rooms = lark_calendar.get_meeting_room_list()
lark_bitable.update_room_config_table(rooms)
print("会议室配置表初始化完成, 请前往多维表格查看调整可用范围（ON-可用，OFF-禁用）")
