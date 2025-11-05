## RoomHunter —— 飞书会议室神抢手

这是一个基于飞书开放平台的自动化机器人，按预设规则从飞书多维表格读取任务，查询会议室忙闲并自动创建日程、添加会议室与参会人，支持持续后台运行抢订。

### 功能特性
- 自动读取“任务表”（开启状态）并计算下一次需要预约的时间段（支持每X周循环、7天窗口限制）
- 批量查询会议室忙闲状态，按偏好优先级与是否允许备选规则自动选择会议室
- 创建日程、邀请预订人、添加会议室资源
- 记录“已完成任务”明细便于追踪
- 一键初始化会议室配置表
- 支持日志滚动输出，便于问题定位

### 目录结构（核心）
- `main.py`：主循环逻辑，按自定义配置频率轮询
- `initialize.py`：初始化会议室配置表
- `lark/`：飞书 API 封装（Calendar、Bitable、Base）
- `src/helper.py`：任务解析、选择策略与ID映射
- `src/utils.py`：时间与字符串工具
- `src/logger.py`：日志配置
- `config.example.ini`：配置示例

---

## 前置条件
1. Python 版本：建议 3.10+
2. 已在飞书开放平台创建“企业自建应用”，并具备以下权限（根据实际最小权限配置）：
   - 日历：读写日程、读写参与人
   - 视频会议/会议室：查询会议室和忙闲
   - 多维表格：读写表数据
3. 获取应用凭据：`App ID` 与 `App Secret`
4. 准备三张多维表格：任务表、会议室配置表、已完成任务表（表结构见下）
- [三表结构示例（飞书多维表格）](https://wrpnn3mat2.feishu.cn/wiki/Ud2Dw5PDDiJjBukdqr4cZYccnMg?table=tblkResuW1lX97IY&view=vewzS9J9Pv)

---

## 安装与运行

### 1) 克隆项目并进入目录
```bash
git clone <repo-url>
cd roombot
```

### 2) 创建虚拟环境并安装依赖
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) 配置应用
将 `config.example.ini` 复制为 `config.ini` 并按需修改：

```ini
[LOGGER]
logLevel = INFO
logFile = logs/roombot.log

[APP]
appId = <你的AppID>
appSecret = <你的AppSecret>
logLevel = INFO

[BITABLE]
bitableToken = <你的飞书多维表格Token>
wiki = <是否在wiki空间内，TRUE-是、FALSE-否>
taskTableId = <任务表ID>
roomConfigTableId = <会议室配置表ID>
completedTaskTableId = <已完成任务表ID>

[ROOM]
roomLevelId = ["<room_level_id_1>", "<room_level_id_2>"]
```

提示：
- `bitableToken` 如表位于知识库（Wiki）中，需配合 `wiki=True`，程序会自动解析为空间对象 token。
- `roomLevelId` 可通过调用“查询会议室列表”接口 [详见API文档](https://open.feishu.cn/document/server-docs/vc-v1/room/list) 返回的 `room_level_id` 获取，并支持配置多个。

### 4) 初始化会议室配置表
首次运行前建议初始化会议室配置表：
```bash
python initialize.py
```
执行后会将可查询到的会议室写入“会议室配置表”，字段包含：`room_id`、`room_name`、`room_status`（默认 ON）。你可在表中按需将部分会议室改为 `OFF`。

### 5) 启动机器人
```bash
python main.py
```
程序会按配置频率轮询：读取任务表 → 解析即将到期任务 → 查询可用会议室 → 创建日程并写“已完成任务”。

---

## 多维表格表结构说明

为保证机器人正常运行，请确保表字段命名与类型一致（字段名区分大小写）。下述为最低要求字段：

### 1) 任务表（`taskTableId`）
- `任务ID`：文本（唯一标识）
- `任务状态`：单选（ON/OFF），仅 ON 会被执行
- `循环周期`：文本，如“每1周”、“每2周”
- `日程标题`：文本
- `日程开始时间`：时间（毫秒时间戳，或你的来源写入为毫秒整型）
- `日程结束时间`：时间（毫秒时间戳）
- `预订人`：人员（需能取到 `id`/open_id）
- 可选：`优先预定偏好会议室`：多选文本（会议室名称）
- 可选：`允许预定非偏好会议室`：文本（YES/NO）

机器人会基于“首次日程时间 + 循环周期”推算下一次预约时间，且仅处理距离当前日期 ≤7 天、且在当前时间之后的时间段。

### 2) 会议室配置表（`roomConfigTableId`）
- `room_id`：文本
- `room_name`：文本
- `room_status`：单选（ON/OFF），ON 表示可用于自动预约

该表由 `initialize.py` 一键生成，可按需手动禁用部分会议室。

### 3) 已完成任务表（`completedTaskTableId`）
- `任务ID`、`日程ID`、`日程标题`
- `日程开始时间`、`日程结束时间`
- `会议室名称`、`会议室ID`
- `预订人名称`、`预订人ID`

---

## 运行机制与关键策略
- 轮询周期：`main.py` 中默认 `sleep(600)`（10 分钟）
- 时间处理：统一以毫秒时间戳为主，必要时转换为 RFC3339（Asia/Shanghai）
- 会议室选择：
  - 若允许备选（YES）：优先匹配偏好列表中的空闲会议室，否则使用其他空闲会议室
  - 若不允许备选（NO）：仅在偏好列表有空闲会议室时选择，否则跳过

---

## 日志
- 默认输出到 `logs/roombot_YYYYMMDD.log`，可在 `config.ini` 的 `[LOGGER]` 区块调整：
  - `logLevel`、`logFile`、`addDateToFilename`、`logFormat`、`maxBytes`、`backupCount`

---

## 常见问题（FAQ）

1) 程序启动报错“会议室配置表为空，请先运行initialize.py初始化会议室配置表!”
- 先执行 `python initialize.py`，然后再运行 `python main.py`。

2) 创建日程失败或参与人/会议室添加失败
- 检查飞书应用权限是否完整；
- 确认 `appId/appSecret` 正确；
- 查看日志文件具体的 `code/msg/log_id` 定位接口错误。

3) 表 Token/空间 Token 如何配置？
- 若表位于 Wiki 中，将 `wiki=True` 并将 `bitableToken` 配置为 Wiki 节点 token，程序会自动解析为空间 token。

---

## 开发与调试建议
- 在 `config.ini` 的 `[LOGGER]` 与 `[APP]` 中将 `logLevel` 调为 `DEBUG` 便于排查
- 使用小范围的测试会议室与短周期任务验证流程
- 留意 `Asia/Shanghai` 时区设置及毫秒/秒时间戳差异

---

