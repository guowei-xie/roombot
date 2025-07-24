"""
飞书多维表格API模块
"""
from lark_oapi.api.bitable.v1 import *
from lark.base import LarkBase
import configparser
import json

class LarkBitable(LarkBase):
    """飞书多维表格操作类"""
    
    def __init__(self, log_level=None):
        """
        初始化飞书多维表格客户端
        
        参数:
            log_level: 日志级别，默认继承LarkBase的默认值
        """
        super().__init__(logger_name='lark_bitable')
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.bitable_token = config['BITABLE']['bitableToken']
        self.task_table_id = config['BITABLE']['taskTableId']
        self.room_config_table_id = config['BITABLE']['roomConfigTableId']
        self.wiki = config['BITABLE']['wiki']
        if self.wiki:
            self.wiki_node_space = self.get_wiki_node_space(self.bitable_token, 'wiki')
            self.bitable_token = self.wiki_node_space.data.node.obj_token

    def get_all_records(self, app_token=None, table_id=None, view_id=None, page_size=100):
        """
        获取多维表格中的所有记录
        
        参数:
            app_token: 多维表格的应用令牌，默认使用配置中的bitable_token
            table_id: 表格ID，默认为None
            view_id: 视图ID，默认为None
            page_size: 每页记录数，默认为100
            
        返回:
            包含所有记录的列表
        """
        app_token = app_token or self.bitable_token
        if not app_token:
            raise ValueError("必须提供app_token参数或在配置文件中设置bitableToken")
        if not table_id:
            raise ValueError("必须提供table_id参数")
            
        self.logger.debug(f"开始获取多维表格记录，表格ID: {table_id}")
        
        all_records = []
        page_token = None
        
        while True:
            # 获取一页记录
            records_page = self._get_records_page(app_token, table_id, view_id, page_token, page_size)
            
            # 添加当前页的记录到结果列表
            if records_page.data and records_page.data.items:
                all_records.extend(records_page.data.items)
                
            # 检查是否有更多页
            if not records_page.data or not records_page.data.has_more or not records_page.data.page_token:
                break
                
            # 更新页标记以获取下一页
            page_token = records_page.data.page_token
            self.logger.debug(f"获取下一页记录，页标记: {page_token}")
        
        self.logger.info(f"成功获取所有记录，共 {len(all_records)} 条")
        return all_records

    def get_all_records_json(self, app_token=None, table_id=None, view_id=None, page_size=100):
        """
        将获取到的全部记录转换为json格式
        
        参数:
            app_token: 多维表格的应用令牌，默认使用配置中的bitable_token
            table_id: 表格ID，默认为None
            view_id: 视图ID，默认为None
            page_size: 每页记录数，默认为100
            
        返回:
            JSON格式的记录数据
        """
        table_records = self.get_all_records(app_token, table_id, view_id, page_size)
        
        # 将 AppTableRecord 对象转换为可序列化的字典
        serializable_records = []
        for record in table_records:
            record_dict = {
                "record_id": record.record_id,
                "fields": record.fields
            }
            serializable_records.append(record_dict)
            
        return serializable_records
    
    def _get_records_page(self, app_token, table_id, view_id=None, page_token=None, page_size=100):
        """
        获取多维表格中的一页记录
        
        参数:
            app_token: 多维表格的应用令牌
            table_id: 表格ID
            view_id: 视图ID，默认为None
            page_token: 分页标记，默认为None
            page_size: 每页记录数，默认为100
            
        返回:
            包含一页记录的响应对象
        """
        # 构造请求对象
        request_builder = ListAppTableRecordRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .page_size(page_size)
            
        # 添加可选参数
        if view_id:
            request_builder.view_id(view_id)
        if page_token:
            request_builder.page_token(page_token)
            
        request = request_builder.build()
        
        # 发起请求
        response = self.client.bitable.v1.app_table_record.list(request)
        
        # 处理响应
        return self.handle_response(response, "获取多维表格记录")
    
    def get_task_table(self):
        """
        获取任务表中的记录（仅返回“任务状态”为“ON”的记录）
        """
        table_records = self.get_all_records_json(self.bitable_token, self.task_table_id)
        # 筛选“任务状态”为“ON”的记录
        table_records = [record for record in table_records if record["fields"]["任务状态"] == "ON"]
        return table_records
    
    def get_room_config_table(self):
        """
        获取会议室配置表中的记录（仅返回“room_status”为“ON”的记录）
        """
        table_records = self.get_all_records_json(self.bitable_token, self.room_config_table_id)
        # 筛选“room_status”为“ON”的记录
        table_records = [record for record in table_records if record["fields"]["room_status"] == "ON"]
        return table_records

    # 新增多维表记录
    def create_record(self, app_token, table_id, fields):
        """
        新增多维表格记录
        
        参数:
            app_token: 多维表格的应用令牌
            table_id: 表格ID
            fields: 记录字段数据，字典格式
            
        返回:
            新创建的记录信息
        """
        self.logger.debug(f"创建多维表格记录，表格ID: {table_id}")
        
        # 构造请求对象
        request = CreateAppTableRecordRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .request_body(AppTableRecord.builder()
                .fields(fields)
                .build()) \
            .build()
        
        response = self.client.bitable.v1.app_table_record.create(request)
        
        return self.handle_response(response, "创建多维表格记录")
    
    def batch_create_records(self, app_token, table_id, records_fields):
        """
        批量新增多维表格记录
        
        参数:
            app_token: 多维表格的应用令牌
            table_id: 表格ID
            records_fields: 记录字段数据列表，每项为一个字典
            
        返回:
            批量创建的记录信息
        """
        self.logger.debug(f"批量创建多维表格记录，表格ID: {table_id}，记录数: {len(records_fields)}")
        
        for fields in records_fields:
            self.create_record(app_token, table_id, fields)

    def extract_record_ids(self, json_data):
        """
        从fields中提取所有record_id
        
        参数:
            json_data: 包含记录数据的JSON列表，每个记录应有record_id字段
            
        返回:
            包含所有record_id的列表
        """
        record_ids = []
              
        for record in json_data:
            if isinstance(record, dict) and "record_id" in record:
                record_ids.append(record["record_id"])
        
        return record_ids

    def batch_delete_records(self, app_token, table_id):
        """
        批量删除多维表格记录
        """
        records = self.get_all_records_json(app_token, table_id)
        record_ids = self.extract_record_ids(records)

        if not record_ids:
            return
        
        request = BatchDeleteAppTableRecordRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .request_body(BatchDeleteAppTableRecordRequestBody.builder() \
                .records(record_ids) \
                .build()) \
            .build()
        
        response = self.client.bitable.v1.app_table_record.batch_delete(request)
        return self.handle_response(response, "批量删除多维表格记录")
    
    def update_room_config_table(self, list_dict):
        """
        更新会议室配置表中的记录
        """
        self.batch_delete_records(self.bitable_token, self.room_config_table_id)
        self.batch_create_records(self.bitable_token, self.room_config_table_id, list_dict)