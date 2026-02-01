# AlbionTools 开发文档

## 简介
- 目标：为 Albion Online 提供叠加层与数据解析，基于原始网络抓包识别 Photon 协议；事件分发到业务处理器与插件 UI；提供控制面板与插件化扩展能力。
- 环境：Windows，Python 3.x；需安装 Npcap。

## 技术栈
- 语言与运行时：Python 3.x
- GUI：PySide6（Qt，信号/槽、无边框窗口、面板栈）
- Windows API：pywin32（层级窗口、鼠标穿透、目标窗口跟随）
- 抓包与解析：pcapy-ng（基于 Npcap/Pcap），自研 Ethernet/IP/UDP 解析与 Photon 检测
- 配置与数据模型：pydantic（依赖列出，当前以自定义模型为主）
- 调试：ipdb

## 目录结构
- 入口：`main.py`（启动 UI、网络、总线与订阅）
- 框架层 `core/`
  - 抽象基类：`base/handler.py`、`base/provider.py`、`base/plugin.py`
  - 配置系统：`config/plugin_config.py`、`config/storage.py`
  - 事件总线与分发：`event_bus.py`、`handler_registry.py`、`packet_dispatcher.py`
- 网络层 `network/`
  - 门面：`manager.py`
  - 抓包实现：`providers/libpcap.py`
  - 分层解析器：`parsers/ethernet.py`、`parsers/ip.py`、`parsers/udp.py`
  - Photon 检测：`photon/detector.py`、`photon/constants.py`
- 业务处理器 `handlers/`
  - 示例：`raw_data_handler.py`、`item_handler.py`、`__init__.py`
- UI 层 `ui/`
  - 主叠加层：`master_overlay.py`
  - 控制面板：`control_dashboard.py`
  - 面板：`panels/log_panel.py`、`panels/general_settings.py`
  - 组件：`components/custom_title_bar.py`
- 插件层 `plugins/`
  - 示例插件：`fps_plugin/plugin.py`、`overlay_widget.py`、`config_widget.py`
  - 注册入口：`plugins/__init__.py`
- 依赖与文档：`requirements.txt`、`README.md`、`DEVELOPER_GUIDE.md`、`DEPRECATED.md`

## 运行与构建
- 安装依赖：`pip install -r e:\Code\AlbionTools\requirements.txt`
- 预置环境：安装 Npcap（`https://npcap.com/`）
- 启动应用：`python e:\Code\AlbionTools\main.py`
- 虚拟环境建议：在仓库根创建并激活 `.venv` 后安装依赖

## 配置系统
- 持久化目录：`e:\Code\AlbionTools\.config\`（按插件 `plugin_id` 生成 JSON）
- 示例：`.config\fps_plugin.json`（由 `core\config\storage.py` 自动读写）
- 配置模型：`core\config\plugin_config.py`（位置、尺寸、透明度、插件自定义项）
- 运行参数（位于 `main.py`）：
  - `GAME_WINDOW_TITLE` 默认 `Albion Online Client`
  - `GAME_PORT` 默认 `5056`

## 架构总览
- 事件总线：`core/event_bus.py` 定义 `PacketType` 与 `GameEvent`，使用 Qt `Signal` 实现跨线程发布/订阅，全局单例 `global_event_bus`
- 处理器注册：`core/handler_registry.py` 管理 `BasePacketHandler`，按 `priority` 降序分发，隔离处理器内部异常
- 分发桥接：`core/packet_dispatcher.py` 连接总线信号到处理器分发入口
- 网络门面：`network/manager.py` 启动/停止抓包、注册处理器、统一接口
- 抓包实现：`network/providers/libpcap.py` 打开设备、BPF 过滤、解析与 Photon 检测，发布 `RAW_GAME_DATA`
- UI与插件：`ui/master_overlay.py` 主叠加层；`ui/control_dashboard.py` 控制面板与日志展示；`plugins/fps_plugin` 提供 overlay 与 config 两种 UI

## 数据流
- 抓包（`LibpcapProvider`）→ 分层解析（L2/L3/L4）→ Photon 识别 → 构造 `GameEvent(PacketType.RAW_GAME_DATA)` → `global_event_bus.publish` → `PacketDispatcher` → `HandlerRegistry` → 匹配的 `Handler.handle`
- `main.py` 订阅 `RAW_GAME_DATA`，将简要日志推送到控制面板的日志视图

## 网络层细节
- 设备锁定：避免多网卡混淆；多设备打开与锁定策略
- BPF 过滤：按目标端口过滤（加速与降噪）
- 线程模型：工作线程轮询抓包与解析，异常捕获并继续循环
- Photon 识别：结合端口集合与特征字节（`network/photon/detector.py`）

## 事件与处理器
- 抽象接口：`core/base/handler.py`（处理器接口与 `priority`）
- 注册/分发：`core/handler_registry.py`（优先级执行、异常隔离）
- 示例处理器：`handlers/raw_data_handler.py`（原始包统计）、`handlers/item_handler.py`（物品相关事件）
- 参考：`e:\Code\AlbionTools\network\manager.py:45` 调用 `self.registry.register(handler)` 注册处理器

## UI 与插件
- 主叠加层：`ui/master_overlay.py` 支持编辑模式（切换鼠标穿透）、跟随游戏窗口几何、拖拽容器 `DraggableContainer`
- 控制面板：`ui/control_dashboard.py` 侧栏导航、内容栈、日志与通用设置面板，统一样式
- 插件体系：`core/base/plugin.py` 定义插件通用接口（配置管理、位置/透明度更新、事件处理钩子）；示例 `plugins/fps_plugin` 提供 overlay 与 config 两种 UI

## 日志与错误处理
- 日志输出：以 `print` 为主；UI `LogPanel` 展示事件日志（由 `main.py` 转发）
- 错误处理：抓包/线程异常捕获并打印；处理器分发隔离异常；配置读写失败回退默认或返回失败标志

## 测试与 CI
- 当前未包含测试用例与 CI 配置
- 建议：为解析器/Photon 检测添加单元测试；对事件分发与 UI 插件进行集成测试；引入 CI（GitHub Actions）

## 开发规范与约定
- 插件 `plugin_id` 唯一，配置 JSON 按 `plugin_id` 存取
- 事件类型枚举化，跨线程通过 Qt 信号传递
- 叠加层窗口遵循“编辑模式/穿透模式”切换，不在穿透模式下捕获鼠标
- 处理器优先级合理分配，避免耗时操作阻塞分发
- 网络线程保持无阻塞；解析失败不影响循环

## 常见开发任务
- 新增业务处理器：
  - 在 `handlers/` 新建 `xxx_handler.py`，继承 `BasePacketHandler`
  - 在 `handlers/__init__.py` 注册到默认处理器列表，并设置 `priority`
- 新增 UI 插件：
  - 在 `plugins/<your_plugin>/` 新建 `plugin.py`、`overlay_widget.py`、`config_widget.py`
  - 继承 `BasePlugin`，实现 `plugin_id`、`load_config`/`save_config`、`create_overlay`/`create_config_widget`
  - 在 `plugins/__init__.py` 注册插件工厂
- 订阅事件总线：在相应模块使用 `global_event_bus.subscribe(PacketType.XXX, callback)`
- 持久化插件配置：使用 `core/config/storage.py` 的 API 根据 `plugin_id` 读写配置 JSON

## 后续演进建议
- 日志库：引入结构化日志（`loguru` 或 `logging`），替代散落的 `print`
- 打包发布：增加 `PyInstaller` 或 Qt 部署脚本生成可执行
- 测试体系：完善解析器/分发/插件测试；引入 CI
- 性能监控：捕获包率、处理延迟、UI 刷新耗时指标
- 配置增强：统一 schema 校验与迁移策略，完善 `.config` 生命周期
- 热插拔：运行期加载/卸载插件与处理器

## 关键路径与文件
- 入口：`e:\Code\AlbionTools\main.py`
- 框架核心：`e:\Code\AlbionTools\core\event_bus.py`、`core\handler_registry.py`、`core\packet_dispatcher.py`
- 抽象基类：`e:\Code\AlbionTools\core\base\handler.py`、`core\base\provider.py`、`core\base\plugin.py`
- 配置系统：`e:\Code\AlbionTools\core\config\storage.py`、`core\config\plugin_config.py`、`e:\Code\AlbionTools\.config\fps_plugin.json`
- 网络层：`e:\Code\AlbionTools\network\manager.py`、`network\providers\libpcap.py`、`network\parsers\ethernet.py`、`network\parsers\ip.py`、`network\parsers\udp.py`、`network\photon\detector.py`
- UI 层：`e:\Code\AlbionTools\ui\master_overlay.py`、`ui\control_dashboard.py`、`ui\panels\log_panel.py`、`ui\panels\general_settings.py`、`ui\components\custom_title_bar.py`
- 插件示例：`e:\Code\AlbionTools\plugins\fps_plugin\plugin.py`、`plugins\fps_plugin\overlay_widget.py`、`plugins\fps_plugin\config_widget.py`
- 依赖：`e:\Code\AlbionTools\requirements.txt`
- 文档：`e:\Code\AlbionTools\README.md`、`DEVELOPER_GUIDE.md`、`DEPRECATED.md`

## 变更记录（占位）
- 2025-11：整理并新增本开发文档，同步近期重构后的架构说明。

