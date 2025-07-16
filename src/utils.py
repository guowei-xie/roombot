import time
from datetime import datetime
from src.logger import logger

# 转换日期时间字符串为时间戳
def convert_date_to_timestamp(date_str):
    """
    将日期时间字符串转换为时间戳
    
    Args:
        date_str: 日期时间字符串，格式为"%Y-%m-%d %H:%M:%S"
        
    Returns:
        int: 时间戳
    """
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(date.timetuple()))
        logger.debug(f"日期转换成功: {date_str} -> {timestamp}")
        return timestamp
    except Exception as e:
        logger.error(f"日期转换失败: {date_str}, 错误: {str(e)}")
        raise

# 转换日期时间字符串为RFC3339格式
# 如：2025-07-16 13:00:00 -> 示例：2025-07-16T13:00:00+08:00
def convert_date_to_rfc3339(date_str):
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        rfc3339 = date.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        logger.debug(f"日期转换成功: {date_str} -> {rfc3339}")
        return rfc3339
    except Exception as e:
        logger.error(f"日期转换失败: {date_str}, 错误: {str(e)}")
        raise

# 转换时间戳为日期时间字符串
def convert_timestamp_to_date_str(timestamp):
    """
    将时间戳转换为日期时间字符串
    
    Args:
        timestamp: 时间戳
        
    Returns:
        str: 日期时间字符串，格式为"%Y-%m-%d %H:%M:%S"
    """
    try:
        date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        logger.debug(f"时间戳转换成功: {timestamp} -> {date_str}")
        return date_str
    except Exception as e:
        logger.error(f"时间戳转换失败: {timestamp}, 错误: {str(e)}")
        raise

# 转换时间戳为RFC3339格式
# 如：1721136000 -> 2025-07-16T13:00:00+08:00
def convert_timestamp_to_rfc3339(timestamp):
    """
    将时间戳转换为RFC3339格式
    
    Args:
        timestamp: 时间戳
        
    Returns:
        str: RFC3339格式的时间字符串
    """
    try:
        date = datetime.fromtimestamp(timestamp)
        rfc3339 = date.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        logger.debug(f"时间戳转换成功: {timestamp} -> {rfc3339}")
        return rfc3339
    except Exception as e:
        logger.error(f"时间戳转换失败: {timestamp}, 错误: {str(e)}")
        raise
