"""
飞书日历API模块
"""
import lark_oapi as lark
from lark_oapi.api.calendar.v4 import *
from lark_oapi.api.vc.v1 import *
import time
import json
from datetime import datetime
from src.utils import convert_timestamp_to_date_str
from src.logger import get_logger

# 初始化日志记录器
logger = get_logger('lark_calendar')

class LarkCalendar:
    """飞书日历操作类"""
    
    def __init__(self, app_id, app_secret, log_level=lark.LogLevel.INFO):
        """初始化飞书日历客户端"""
        logger.info(f"初始化飞书日历客户端，日志级别: {log_level}")
        self.client = lark.Client.builder() \
            .app_id(app_id) \
            .app_secret(app_secret) \
            .log_level(log_level) \
            .build()
        
        self.calendar_id = self.get_primary_calendar_id()

    def get_primary_calendar(self):
        """获取主日历信息"""
        logger.debug("获取主日历信息")
        request = PrimaryCalendarRequest.builder().build()
        response = self.client.calendar.v4.calendar.primary(request)

        if not response.success():
            error_msg = f"获取主日历失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        logger.debug("成功获取主日历信息")
        return response

    def get_primary_calendar_id(self):
        """提取主日历ID"""
        response = self.get_primary_calendar()
        calendar_id = response.data.calendars[0].calendar.calendar_id
        logger.info(f"获取主日历ID: {calendar_id}")
        return calendar_id

    def get_calendar_events(self, start_time, end_time):
        """获取日程列表"""
        start_time_str = convert_timestamp_to_date_str(start_time)
        end_time_str = convert_timestamp_to_date_str(end_time)
        logger.debug(f"获取日程列表: {start_time_str} - {end_time_str}")
        
        request = ListCalendarEventRequest.builder() \
            .calendar_id(self.calendar_id) \
            .start_time(start_time) \
            .end_time(end_time) \
            .build()
        
        response = self.client.calendar.v4.calendar_event.list(request)

        if not response.success():
            error_msg = f"获取日程列表失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
            logger.error(error_msg)
            raise Exception(error_msg)

        logger.debug(f"成功获取日程列表")
        return response

    def get_calendar_events_list(self, start_time=None, end_time=None):
        """提取日程列表中的重要字段"""
        # 如果没有填写时间，默认前后1周
        if start_time is None:
            start_time = int(time.time()) - 7 * 24 * 60 * 60 
        if end_time is None:
            end_time = int(time.time()) + 7 * 24 * 60 * 60 

        response = self.get_calendar_events(start_time, end_time)
        events = []
        if response.data and response.data.items:
            for item in response.data.items:
                events.append({
                    "event_id": item.event_id,
                    "organizer_calendar_id": item.organizer_calendar_id,
                    "summary": item.summary,
                    "start_time": item.start_time.timestamp,
                    "end_time": item.end_time.timestamp,
                })

        start_time_str = convert_timestamp_to_date_str(start_time)
        end_time_str = convert_timestamp_to_date_str(end_time)
        logger.info(f"提取日程列表: {start_time_str} - {end_time_str}, 共{len(events)}条日程")

        return events

    def create_calendar_event(self, title, start_time, end_time):
        """创建日程"""
        start_time_str = convert_timestamp_to_date_str(start_time)
        end_time_str = convert_timestamp_to_date_str(end_time)
        logger.info(f"创建日程: {title}, 时间: {start_time_str} - {end_time_str}")
        
        request = CreateCalendarEventRequest.builder() \
            .calendar_id(self.calendar_id) \
            .request_body(CalendarEvent.builder() \
                .summary(title) \
                .start_time(TimeInfo.builder() \
                    .timestamp(start_time) \
                    .timezone("Asia/Shanghai") \
                    .build()) \
                .end_time(TimeInfo.builder() \
                    .timestamp(end_time) \
                    .timezone("Asia/Shanghai") \
                    .build()) \
                .visibility("default") \
                .attendee_ability("can_modify_event") \
                .free_busy_status("busy") \
                .build()) \
            .build()

        response = self.client.calendar.v4.calendar_event.create(request)

        if not response.success():
            error_msg = f"创建日程失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
            logger.error(error_msg)
            raise Exception(error_msg)

        logger.info(f"成功创建日程，ID: {response.data.event.event_id}, 标题: {response.data.event.summary}, 时间: {start_time_str} - {end_time_str}")
        return response.data.event.event_id

    def get_meeting_room_list(self):
        """获取会议室列表"""
        request = ListRoomRequest.builder() \
            .page_size(100) \
            .room_level_id("omb_2a0a8a9abede15fb3c69405c7053e742") \
            .build()
        response = self.client.vc.v1.room.list(request)
        if not response.success():
            error_msg = f"获取会议室列表失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
            logger.error(error_msg)
            raise Exception(error_msg)

        rooms = [] 
        if response.data and response.data.rooms:
            for room in response.data.rooms:
                rooms.append({
                    "room_id": room.room_id,
                    "room_name": room.name
                })
        logger.info(f"成功获取会议室列表, 共{len(rooms)}个会议室")
        return rooms

    # 查询会议室忙闲状态
    def get_meeting_room_busy_status(self, room_id, time_min, time_max):
        """查询会议室忙闲状态

    
    def add_calendar_event_user(self, event_id, user_id):
        """添加日程参与人"""
        request = CreateCalendarEventAttendeeRequest.builder() \
            .calendar_id(self.calendar_id) \
            .event_id(event_id) \
            .user_id_type("open_id") \
            .request_body(CreateCalendarEventAttendeeRequestBody.builder() \
                .attendees([CalendarEventAttendee.builder() \
                    .type("user") \
                    .is_optional(True) \
                    .user_id(user_id) \
                    .need_notification(True) \
                    .build()) \
            .build()
        response = self.client.calendar.v4.calendar_event_attendee.create(request)
        if not response.success():
            error_msg = f"添加日程参与人失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
            logger.error(error_msg)
            raise Exception(error_msg)

        logger.info(f"成功添加日程参与人, 用户ID: {user_id}, 日程ID: {event_id}")
        
    def add_calendar_event_room(self, event_id, room_id):
        """添加日程会议室"""
        request = CreateCalendarEventAttendeeRequest.builder() \
            .calendar_id(self.calendar_id) \
            .event_id(event_id) \
            .user_id_type("open_id") \
            .request_body(CreateCalendarEventAttendeeRequestBody.builder() \
                .attendees([CalendarEventAttendee.builder() \
                    .type("resource") \
                    .room_id(room_id) \
                    .approval_reason("该预订审批自动发出，如有异常，请联系 @商业智能-谢国伟") \
                    .build()) \
            .build()
        response = self.client.calendar.v4.calendar_event_attendee.create(request)
        if not response.success():
            error_msg = f"添加日程会议室失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
            logger.error(error_msg)
            raise Exception(error_msg)

        logger.info(f"成功添加日程会议室, 会议室ID: {room_id}, 日程ID: {event_id}")
            
                    