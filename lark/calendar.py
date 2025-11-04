"""
飞书日历API模块
"""
from lark_oapi.api.calendar.v4 import *
from lark_oapi.api.vc.v1 import *
import time
from src.utils import convert_timestamp_to_date_str, convert_timestamp_to_rfc3339, str_to_list
from lark.base import LarkBase
import configparser

class LarkCalendar(LarkBase):
    """飞书日历操作类"""
    
    def __init__(self, log_level=None):
        """
        初始化飞书日历客户端
        
        参数:
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
            log_level: 日志级别，默认继承LarkBase的默认值
        """
        super().__init__(logger_name='lark_calendar')
        self.calendar_id = self.get_primary_calendar_id()
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.room_level_id = str_to_list(config['ROOM']['roomLevelId'])

    def get_primary_calendar(self):
        """
        获取主日历信息
        
        返回:
            主日历信息响应对象
        """
        self.logger.debug("获取主日历信息")
        request = PrimaryCalendarRequest.builder().build()
        response = self.client.calendar.v4.calendar.primary(request)
        return self.handle_response(response, "获取主日历")

    def get_primary_calendar_id(self):
        """
        提取主日历ID
        
        返回:
            str: 主日历ID
        """
        response = self.get_primary_calendar()
        calendar_id = response.data.calendars[0].calendar.calendar_id
        self.logger.info(f"获取主日历ID: {calendar_id}")
        return calendar_id

    def get_calendar_events(self, start_time, end_time):
        """
        获取日程列表
        
        参数:
            start_time: 开始时间戳
            end_time: 结束时间戳
            
        返回:
            日程列表响应对象
        """
        start_time_str = convert_timestamp_to_date_str(start_time)
        end_time_str = convert_timestamp_to_date_str(end_time)
        self.logger.debug(f"获取日程列表: {start_time_str} - {end_time_str}")
        
        request = ListCalendarEventRequest.builder() \
            .calendar_id(self.calendar_id) \
            .start_time(start_time) \
            .end_time(end_time) \
            .build()
        
        response = self.client.calendar.v4.calendar_event.list(request)
        return self.handle_response(response, "获取日程列表")

    def get_calendar_events_list(self, start_time=None, end_time=None):
        """
        提取日程列表中的重要字段
        
        参数:
            start_time: 开始时间戳，默认为当前时间前一周
            end_time: 结束时间戳，默认为当前时间后一周
            
        返回:
            list: 日程列表，每个元素包含event_id、organizer_calendar_id、summary、start_time、end_time
        """
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
        self.logger.info(f"提取日程列表: {start_time_str} - {end_time_str}, 共{len(events)}条日程")

        return events

    def create_calendar_event(self, title, start_time, end_time):
        """
        创建日程
        
        参数:
            title: 日程标题
            start_time: 开始时间戳
            end_time: 结束时间戳
            
        返回:
            str: 创建的日程ID
        """
        start_time_str = convert_timestamp_to_date_str(start_time)
        end_time_str = convert_timestamp_to_date_str(end_time)
        self.logger.info(f"创建日程: {title}, 时间: {start_time_str} - {end_time_str}")

        start_time = str(int(start_time/1000))
        end_time = str(int(end_time/1000))
        
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
        self.handle_response(response, "创建日程")
        
        self.logger.info(f"成功创建日程，ID: {response.data.event.event_id}, 标题: {response.data.event.summary}, 时间: {start_time_str} - {end_time_str}")
        return response.data.event.event_id


    def get_meeting_room_list(self, default_status="ON"):
        """
        获取会议室列表

        返回:
            list: 会议室列表，每个元素包含room_id和room_name
        """
        rooms = []
        if isinstance(self.room_level_id, list):
            room_level_ids = self.room_level_id
        else:
            room_level_ids = [self.room_level_id]
        
        for level_id in room_level_ids:
            request = ListRoomRequest.builder() \
                .page_size(100) \
                .room_level_id(level_id) \
                .build()
            response = self.client.vc.v1.room.list(request)
            self.handle_response(response, f"获取会议室列表 (room_level_id: {level_id})")
            if response.data and response.data.rooms:
                for room in response.data.rooms:
                    rooms.append({
                        "room_id": room.room_id,
                        "room_name": room.name,
                        "room_status": default_status
                    })
        self.logger.debug(f"成功获取会议室列表, 共{len(rooms)}个会议室")
        return rooms

    def get_meeting_room_busy_periods(self, room_id, time_min, time_max):
        """
        查询会议室忙闲时间段
        
        参数:
            room_id: 会议室ID
            time_min: 开始时间戳
            time_max: 结束时间戳
            
        返回:
            list: 会议室忙碌时间段列表，每个元素包含start_time和end_time
        """
        self.logger.debug(f"查询会议室忙闲状态: 会议室ID {room_id}, 时间: {convert_timestamp_to_date_str(time_min)} - {convert_timestamp_to_date_str(time_max)}")
        time_min = convert_timestamp_to_rfc3339(time_min)
        time_max = convert_timestamp_to_rfc3339(time_max)

        request = ListFreebusyRequest.builder() \
            .user_id_type("open_id") \
            .request_body(ListFreebusyRequestBody.builder() \
                .room_id(room_id) \
                .time_min(time_min) \
                .time_max(time_max) \
                .only_busy(True) \
                .build()) \
            .build()
            
        # 发送请求
        response = self.client.calendar.v4.freebusy.list(request)
        self.handle_response(response, "查询会议室忙闲状态")
        
        # 处理响应结果
        busy_periods = []
        if response.data and response.data.freebusy_list:
            for freebusy in response.data.freebusy_list:
                busy_periods.append({
                    "start_time": freebusy.start_time,
                    "end_time": freebusy.end_time
                })
                    
        self.logger.debug(f"会议室 {room_id} 在指定时间段内有 {len(busy_periods)} 个忙碌时段")
        return busy_periods
    
    def get_meeting_room_busy_status(self, room_id, time_min, time_max):
        """
        判断会议室忙闲状态
        
        参数:
            room_id: 会议室ID
            time_min: 开始时间戳
            time_max: 结束时间戳
            
        返回:
            bool: True表示忙碌，False表示空闲
        """
        busy_periods = self.get_meeting_room_busy_periods(room_id, time_min, time_max)
        return len(busy_periods) > 0
    
    def get_meeting_room_available_list(self, room_ids, time_min, time_max):
        """
        批量检查会议室忙闲状态，并返回仅可用会议室ID列表

        参数:
            room_ids: 会议室ID列表
            time_min: 开始时间戳
            time_max: 结束时间戳

        返回:
            list: 仅可用会议室ID列表
        """
        available_room_ids = []
        for room_id in room_ids:
            busy_status = self.get_meeting_room_busy_status(room_id, time_min, time_max)
            if not busy_status:
                available_room_ids.append(room_id)
        return available_room_ids
        

    def add_calendar_event_user(self, event_id, user_id):
        """
        添加日程参与人
        
        参数:
            event_id: 日程ID
            user_id: 用户ID(open_id)
        """
        request = CreateCalendarEventAttendeeRequest.builder() \
            .calendar_id(self.calendar_id) \
            .event_id(event_id) \
            .user_id_type("open_id") \
            .request_body(
                CreateCalendarEventAttendeeRequestBody.builder()
                .attendees([
                    CalendarEventAttendee.builder()
                    .type("user")
                    .is_optional(True)
                    .user_id(user_id)
                    # 可选字段：如chat_id/room_id/third_party_email/operate_id/approval_reason/resource_customization等，视需要补充
                    .build()
                ])
                .need_notification(True)  # 控制是否通知参与人
                .build()
            ) \
            .build()
        response = self.client.calendar.v4.calendar_event_attendee.create(request)
        self.handle_response(response, "添加日程参与人")
        if response.msg != "success":
            self.logger.error(f"添加日程参与人失败, 用户ID: {user_id}, 日程ID: {event_id}, 错误信息: {response.msg}")
            return False
        self.logger.info(f"成功添加日程参与人, 用户ID: {user_id}, 日程ID: {event_id}")
        
    def add_calendar_event_room(self, event_id, room_id):
        """
        添加日程会议室
        
        参数:
            event_id: 日程ID
            room_id: 会议室ID
        """
        try:
            request = CreateCalendarEventAttendeeRequest.builder() \
                .calendar_id(self.calendar_id) \
                .event_id(event_id) \
                .user_id_type("open_id") \
                .request_body(CreateCalendarEventAttendeeRequestBody.builder() \
                    .attendees([CalendarEventAttendee.builder() \
                        .type("resource") \
                        .room_id(room_id) \
                        .approval_reason("该预订审批自动发出，如有异常，请联系 @商业智能-谢国伟") \
                        .build()]) \
                    .build()) \
                .build()
            response = self.client.calendar.v4.calendar_event_attendee.create(request)
            self.handle_response(response, "添加日程会议室")
            if response.msg != "success":
                self.logger.error(f"添加日程会议室失败, 会议室ID: {room_id}, 日程ID: {event_id}, 错误信息: {response.msg}")
                return False
            self.logger.info(f"成功添加日程会议室, 会议室ID: {room_id}, 日程ID: {event_id}")
        except Exception as e:
            self.logger.error(f"添加日程会议室失败, 会议室ID: {room_id}, 日程ID: {event_id}, 错误信息: {e}")
            return False
        return True