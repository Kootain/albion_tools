好的，我将为您输出一份完整的、整合了所有设计思路和实现细节的系统设计文档。

-----

# 📚 游戏插件系统设计文档
查看开发文档: [docs/AlbionTools-开发文档.md](docs/AlbionTools-开发文档.md)

## 🎯 1. 目标与设计原则

本系统旨在为游戏提供一个高性能、高扩展性的屏幕蒙层（Overlay）和数据分析框架。核心设计围绕 **性能**、**模块化** 和 **用户体验** 三大原则。

| 设计原则 | 描述 | 关键技术实现 |
| :--- | :--- | :--- |
| **高性能** | 避免多个 OS 窗口带来的性能损耗和 Z-Order 冲突，确保游戏帧率不受影响。 | **单一 Master Canvas** 架构，Win32 API 穿透。 |
| **高扩展性** | 允许开发者独立编写插件模块（逻辑和 UI），系统能够动态加载和管理。 | **集中式 EventBus**，Plugin Manager 框架。 |
| **高可用性** | 提供简单且灵活的用户界面布局编辑功能。 | **可拖拽容器 (`DraggableContainer`)**，热键模式切换。 |
| **数据实时性** | 确保网络数据采集在独立线程中高效运行，不阻塞 UI。 | **多线程 Sniffer Worker** (基于 Npcap)。 |

-----

## 🏗️ 2. 核心架构概览

本系统采用 **“单一画布 + 事件驱动”** 的双核架构。

### 2.1 架构图

```mermaid
graph TD
    subgraph Data Flow (Backend)
        SNIFFER[Sniffer Worker (QThread, Npcap)] --> |Raw Packet Data| EVENTBUS
        EVENTBUS((EventBus))
        PLGLOGIC[Plugin Logic Modules] --> EVENTBUS
    end
    
    subgraph UI/Frontend
        MASTER[Master Overlay (Canvas)]
        DRAGCONTAINER1(Draggable Container A)
        DRAGCONTAINER2(Draggable Container B)
        DASHBOARD[Control Dashboard (StackedWidget)]
    end
    
    EVENTBUS --> PLGLOGIC
    PLGLOGIC --> DRAGCONTAINER1
    PLGLOGIC --> DRAGCONTAINER2
    MASTER -- 绝对定位布局 --> DRAGCONTAINER1
    MASTER -- 统一管理 --> DRAGCONTAINER2
    MASTER -- 状态信号 --> DASHBOARD
    DASHBOARD -- UI编辑控制 --> MASTER

    style SNIFFER fill:#f9f,stroke:#333
    style EVENTBUS fill:#ccf,stroke:#333
    style MASTER fill:#cfc,stroke:#333
```

### 2.2 两大核心支柱

#### A. 单一 Master Canvas (UI)

  * **实现方式:** 一个全屏或与游戏窗口等大的 PySide6 `QMainWindow` (`MasterOverlay`)。
  * **职责:** 它是所有插件 UI 的唯一容器。所有插件 UI 都是这个窗口上的 `QFrame` 子组件，通过绝对定位进行布局 (`setLayout(None)`)。
  * **Win32 集成:** 利用 `pywin32` 库实现鼠标穿透 (`WS_EX_TRANSPARENT`) 和窗口跟随 (`GetWindowRect`/`FindWindow`)。

#### B. 集中式 EventBus (数据)
| **编辑模式** | **关闭** | 半透明遮罩 (提示用户) | UI 边框高亮，可点击/拖拽。 | 热键 (F2) / Dashboard 按钮 |

-----

## 🎨 4. Control Dashboard (控制中心) UI 设计

控制面板采用现代 **深色扁平化设计**，通过 QSS 实现统一的视觉风格。

### 4.1 结构细节

| 区域 | PySide6 组件 | 目的 |
| :--- | :--- | :--- |
| **左侧导航** | `QListWidget` | 菜单栏，用于切换不同的配置视图。菜单项包括：系统总览、各插件配置、系统日志。 |
| **右侧内容** | `QStackedWidget` | 容器，根据左侧导航的选择，动态显示对应的配置面板。 |
| **配置面板** | `GeneralSettingsPanel`, `FPSPluginConfigPanel` | 独立的配置模块，确保配置项之间的隔离。总配置面板包含 Overlay 模式切换按钮。 |

### 4.2 现代化样式 (QSS)

使用统一的深色主题：背景色 `#202020`，内容区背景 `#2E2E2E`，高亮色为 `#00A3DA` (蓝色)，提供视觉上的专业感和易读性。

-----

## 🔁 5. 数据流和事件处理

数据从硬件到屏幕的完整流程如下：

1.  **采集 (Workers):** `SnifferWorker` 线程通过 Npcap 捕获目标端口数据。
2.  **标准化 (Workers/Logic):** 原始数据被初步解析并封装为统一的 `GameEvent(type, payload)` 结构。
3.  **分发 (Core):** `SnifferWorker` 将 `GameEvent` 通过 `global_event_bus.publish()` 发射给主线程。
4.  **消费 (Plugins):** 插件逻辑模块订阅总线，接收到相关事件后，更新自身的内部状态。
5.  **渲染 (UI):** 插件状态变化后，其 UI 组件（如 `QLabel`）实时更新显示内容。

此设计确保了数据采集的 I/O 阻塞不会影响 UI 的流畅性。

-----

## ⚙️ 6. 技术栈

| 类别 | 库/工具 | 目的 |
| :--- | :--- | :--- |
| **主语言** | Python 3.x | 核心开发语言。 |
| **GUI 框架** | PySide6 (Qt) | UI 界面、多线程 (QThread) 和信号槽机制 (QObject/Signal)。 |
| **系统交互** | `pywin32` | Windows API 调用，用于窗口跟随和鼠标穿透。 |
| **网络采集** | `pcapy`, `dpkt` | Python 绑定 Npcap 驱动，用于高性能实时抓包和数据解析。 |
| **打包部署** | `requirements.txt` | 依赖管理。 |
