import logging
import os
import configparser
from logging.handlers import RotatingFileHandler
from datetime import datetime

def get_logger(name='roombot', config_file='config.ini'):
    """
    获取配置好的日志记录器
    
    Args:
        name: 日志记录器名称
        config_file: 配置文件路径
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    
    # 获取日志配置
    log_level_str = config.get('LOGGER', 'logLevel', fallback='INFO')
    log_file_template = config.get('LOGGER', 'logFile', fallback='logs/roombot.log')
    add_date = config.getboolean('LOGGER', 'addDateToFilename', fallback=True)
    log_format_type = config.get('LOGGER', 'logFormat', fallback='default')
    max_bytes = config.getint('LOGGER', 'maxBytes', fallback=10*1024*1024)  # 默认10MB
    backup_count = config.getint('LOGGER', 'backupCount', fallback=5)
    
    # 在日志文件名中添加日期（如果配置为True）
    log_file = log_file_template
    if add_date:
        log_date = datetime.now().strftime("%Y%m%d")
        log_file_parts = os.path.splitext(log_file_template)
        log_file = f"{log_file_parts[0]}_{log_date}{log_file_parts[1]}"
    
    # 定义日志格式
    log_formats = {
        'default': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'simple': '%(levelname)s: %(message)s',
        'detailed': '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'
    }
    log_format = log_formats.get(log_format_type, log_formats['default'])
    
    # 转换日志级别
    log_level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    log_level = log_level_map.get(log_level_str.upper(), logging.INFO)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 清除已有的处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建格式化器
    formatter = logging.Formatter(log_format)
    
    # 确保日志目录存在
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 添加文件处理器(支持日志轮转)
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# 创建默认日志记录器
logger = get_logger() 