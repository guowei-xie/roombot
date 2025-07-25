from src.helper import parse_task_table
from lark.bitable import LarkBitable

task_table = [
    {
        "record_id": "recKUulP4I",
        "fields": {
            "任务ID": "ID0011",
            "任务状态": "ON",
            "优先预定偏好会议室": ["ABAP-5层"],
            "允许预定非偏好会议室": "YES",
            "循环周期": "每1周",    
            "日程开始时间": 1753354800000,
            "日程结束时间": 1753358400000,
            "日程标题": "测试日程2",
        }
    },
    {
        "record_id": "recfwgojze",
        "fields": {
            "任务ID": "ID0012", 
            "任务状态": "ON",
            "循环周期": "每1周",
            "日程开始时间": 1753356600000,
            "日程结束时间": 1753358400000,
            "日程标题": "测试日程3",
        }
    }
]

print(parse_task_table(task_table)) 

lark_bitable = LarkBitable()
print(lark_bitable.get_completed_task_list())