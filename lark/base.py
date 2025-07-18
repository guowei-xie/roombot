"""
飞书API基类模块
"""
import lark_oapi as lark
from src.logger import get_logger
import configparser

class LarkBase:
    """飞书API基类，提供通用的客户端初始化和错误处理功能"""
    
    def __init__(self, logger_name='lark_base'):
        """
        初始化飞书客户端
        
        参数:
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
            log_level: 日志级别，默认为INFO
            logger_name: 日志记录器名称，默认为'lark_base'
        """
        # 初始化日志记录器
        self.logger = get_logger(logger_name)
        self.logger.debug(f"初始化飞书客户端")

        # 读取配置文件
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.app_id = config['APP']['appId']
        self.app_secret = config['APP']['appSecret']
        self.log_level = {
            'DEBUG': lark.LogLevel.DEBUG,
            'INFO': lark.LogLevel.INFO,
            'WARNING': lark.LogLevel.WARNING,
            'ERROR': lark.LogLevel.ERROR
        }.get(config['APP']['logLevel'], lark.LogLevel.INFO)

        # 初始化客户端
        self.client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .log_level(self.log_level) \
            .build()
    
    def handle_response(self, response, operation_name):
        """
        处理API响应，检查是否成功，记录日志并在失败时抛出异常
        
        参数:
            response: API响应对象
            operation_name: 操作名称，用于日志记录
            
        返回:
            成功时返回响应对象
            
        异常:
            失败时抛出Exception异常
        """
        if not response.success():
            error_msg = f"{operation_name}失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        
        self.logger.debug(f"成功{operation_name}")
        return response
    
    def get_wiki_node_space(self, token, obj_type):
        """
        获取Wiki节点所在的空间信息
        
        参数:
            token: 节点token，如文档token
            obj_type: 对象类型，如'docx'、'sheet'等
            
        返回:
            成功时返回节点空间信息
            
        异常:
            失败时抛出Exception异常
        """
        from lark_oapi.api.wiki.v2 import GetNodeSpaceRequest
        
        self.logger.debug(f"获取Wiki节点空间信息，token: {token}, obj_type: {obj_type}")
        
        # 构造请求对象
        request = GetNodeSpaceRequest.builder() \
            .token(token) \
            .obj_type(obj_type) \
            .build()
        
        # 发起请求
        response = self.client.wiki.v2.space.get_node(request)
        
        # 处理响应
        return self.handle_response(response, "获取Wiki节点空间信息")
