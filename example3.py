import json

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *


# SDK 使用说明: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development
# 以下示例代码默认根据文档示例值填充，如果存在代码问题，请在 API 调试台填上相关必要参数后再复制代码使用
# 复制该 Demo 后, 需要将 "YOUR_APP_ID", "YOUR_APP_SECRET" 替换为自己应用的 APP_ID, APP_SECRET.
def main():
    # 创建client
    client = lark.Client.builder() \
        .app_id("YOUR_APP_ID") \
        .app_secret("YOUR_APP_SECRET") \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: BatchCreateAppTableRecordRequest = BatchCreateAppTableRecordRequest.builder() \
        .app_token("appbcbWCzen6D8dezhoCH2RpMAh") \
        .table_id("tblsRc9GRRXKqhvW") \
        .user_id_type("open_id") \
        .client_token("fe599b60-450f-46ff-b2ef-9f6675625b97") \
        .ignore_consistency_check(true) \
        .request_body(BatchCreateAppTableRecordRequestBody.builder()
            .records([AppTableRecord.builder()
                .fields({"人员":[{"id":"ou_2910013f1e6456f16a0ce75ede950a0a"},{"id":"ou_e04138c9633dd0d2ea166d79f548ab5d"}],"单向关联":["recHTLvO7x","recbS8zb2m"],"单选":"选项1","双向关联":["recHTLvO7x","recbS8zb2m"],"地理位置":"116.397755,39.903179","复选框":true,"多选":["选项1","选项2"],"数字":100,"文本":"文本内容","日期":1674206443000,"条码":"qawqe","电话号码":"13026162666","群组":[{"id":"oc_cd07f55f14d6f4a4f1b51504e7e97f48"}],"评分":3,"货币":3,"超链接":{"link":"https://www.feishu.cn/product/base","text":"飞书多维表格官网"},"进度":0.25,"附件":[{"file_token":"Vl3FbVkvnowlgpxpqsAbBrtFcrd"}]})
                .build(), 
                AppTableRecord.builder()
                .fields({"文本":"文本内容2"})
                .build()
                ])
            .build()) \
        .build()

    # 发起请求
    response: BatchCreateAppTableRecordResponse = client.bitable.v1.app_table_record.batch_create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.bitable.v1.app_table_record.batch_create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    main()


# 响应体示例
{
  "code": 0,
  "data": {
    "records": [
      {
        "fields": {
          "任务名称": "维护客户关系",
          "创建日期": 1674206443000,
          "截止日期": 1674206443000
        },
        "id": "recusyQbB0fVL5",
        "record_id": "recusyQbB0fVL5"
      },
      {
        "fields": {
          "任务名称": "跟进与谈判",
          "创建日期": 1674206443000,
          "截止日期": 1674206443000
        },
        "id": "recusyQbB0CJjX",
        "record_id": "recusyQbB0CJjX"
      }
    ]
  },
  "msg": "success"
}