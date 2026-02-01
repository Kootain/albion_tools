from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
    QListWidget, QListWidgetItem, QGridLayout, QPushButton, QTabWidget,
    QSplitter, QFrame, QScrollArea, QAbstractItemView, QStyledItemDelegate,
    QSpinBox, QColorDialog, QDialog, QDialogButtonBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal, QEvent, QSize, QTimer
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPalette, QColor, QFont
from ui.platform_utils import press_key

class AutoCastConfigDialog(QDialog):
    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自动施法配置")
        self.resize(300, 250)
        self.config = config or {}
        
        layout = QVBoxLayout(self)
        
        # Enabled
        self.enabled_cb = QComboBox()
        self.enabled_cb.addItems(["禁用 (Disabled)", "启用 (Enabled)"])
        self.enabled_cb.setCurrentIndex(1 if self.config.get("enabled") else 0)
        layout.addWidget(QLabel("状态 (Status):"))
        layout.addWidget(self.enabled_cb)
        
        # Key
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("例如: F, Q, SPACE")
        self.key_edit.setText(self.config.get("key", ""))
        layout.addWidget(QLabel("按键 (Key):"))
        layout.addWidget(self.key_edit)
        
        # Delay
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 10000)
        self.delay_spin.setSuffix(" ms")
        self.delay_spin.setValue(self.config.get("delay", 0))
        layout.addWidget(QLabel("触发延迟 (Delay):"))
        layout.addWidget(self.delay_spin)
        
        # Count
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(self.config.get("count", 1))
        layout.addWidget(QLabel("按键次数 (Count):"))
        layout.addWidget(self.count_spin)
        
        # Interval
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(0, 5000)
        self.interval_spin.setSuffix(" ms")
        self.interval_spin.setValue(self.config.get("interval", 100))
        layout.addWidget(QLabel("按键间隔 (Interval):"))
        layout.addWidget(self.interval_spin)
        
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        
    def get_config(self):
        return {
            "enabled": self.enabled_cb.currentIndex() == 1,
            "key": self.key_edit.text().strip(),
            "delay": self.delay_spin.value(),
            "count": self.count_spin.value(),
            "interval": self.interval_spin.value()
        }

class AlertBlock(QFrame):
    config_changed = Signal() # Emit when config changes

    def __init__(self, block_id, parent=None):
        super().__init__(parent)
        self.block_id = block_id
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet(f"""
            AlertBlock {{
                background-color: #2d2d2d;
                border: 2px solid #444;
                border-radius: 4px;
            }}
        """)
        
        self.default_color = QColor("#2d2d2d")
        self.alert_color = QColor("#ff0000")
        self.duration = 1.0 # seconds
        
        self.setup_ui()
        
    def set_config(self, color, duration):
        self.alert_color = color
        self.duration = duration
        self._update_color_indicator()

    def highlight_skill(self, skill_name):
        # Highlight matching items in history list
        count = self.history_list.count()
        for i in range(count):
            item = self.history_list.item(i)
            if skill_name in item.text():
                item.setBackground(QColor("#555500")) # Yellowish highlight
            else:
                item.setBackground(Qt.NoBrush)

    def clear_highlight(self):
        count = self.history_list.count()
        for i in range(count):
            item = self.history_list.item(i)
            item.setBackground(Qt.NoBrush)

    def setup_ui(self):
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.reset_alert)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header: ID and Config Button
        header_layout = QHBoxLayout()
        self.id_label = QLabel(f"区域 {self.block_id}")
        self.id_label.setStyleSheet("font-weight: bold; color: #aaa;")
        header_layout.addWidget(self.id_label)
        header_layout.addStretch()
        
        self.config_btn = QPushButton("⚙")
        self.config_btn.setFixedSize(24, 24)
        self.config_btn.setStyleSheet("background: transparent; border: none; color: #888;")
        self.config_btn.clicked.connect(self.open_config)
        header_layout.addWidget(self.config_btn)
        
        layout.addLayout(header_layout)
        
        # Trigger Info
        self.trigger_info = QLabel("等待触发...")
        self.trigger_info.setAlignment(Qt.AlignCenter)
        self.trigger_info.setStyleSheet("font-size: 14px; font-weight: bold; color: #fff; margin: 10px 0;")
        layout.addWidget(self.trigger_info)
        
        # History List
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #222;
                border: 1px solid #333;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 2px;
                color: #ccc;
            }
        """)
        self.history_list.setFixedHeight(80) # Limit height
        layout.addWidget(self.history_list)
        
        self._update_color_indicator()

    def _update_color_indicator(self):
        # Update header ID label to show color dot
        self.id_label.setText(f"区域 {self.block_id}  ●")
        self.id_label.setStyleSheet(f"font-weight: bold; color: {self.alert_color.name()};")

    def trigger(self, player_name, skill_name):
        self.setStyleSheet(f"""
            AlertBlock {{
                background-color: {self.alert_color.name()};
                border: 2px solid #fff;
                border-radius: 4px;
            }}
            QLabel {{
                background-color: transparent;
                color: #ffffff;
            }}
        """)
        
        text = f"{player_name}\n{skill_name}"
        self.trigger_info.setText(text)
        
        # Add to history
        import time
        ts = time.strftime("%H:%M:%S")
        item = QListWidgetItem(f"[{ts}] {text}")
        self.history_list.insertItem(0, item) # Add to top
        
        # Highlight logic (optional, list widget handles selection or we can color item)
        item.setBackground(QColor("#444"))
        
        self.timer.start(int(self.duration * 1000))
        
    def reset_alert(self):
        self.setStyleSheet(f"""
            AlertBlock {{
                background-color: {self.default_color.name()};
                border: 2px solid #444;
                border-radius: 4px;
            }}
            QLabel {{
                background-color: transparent;
                color: #e0e0e0;
            }}
        """)
        self.trigger_info.setText("等待触发...")

    def open_config(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(f"配置区域 {self.block_id}")
        layout = QVBoxLayout(dlg)
        
        # Color
        color_btn = QPushButton("选择报警颜色")
        color_btn.clicked.connect(lambda: self._pick_color(color_btn))
        layout.addWidget(color_btn)
        
        # Duration
        dur_spin = QSpinBox()
        dur_spin.setRange(1, 10)
        dur_spin.setValue(int(self.duration))
        dur_spin.setSuffix(" 秒")
        layout.addWidget(QLabel("持续时间:"))
        layout.addWidget(dur_spin)
        
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)
        
        if dlg.exec() == QDialog.Accepted:
            self.duration = dur_spin.value()
            self.config_changed.emit()

    # Refined _pick_color to be more robust
    def _pick_color(self, btn):
        c = QColorDialog.getColor(self.alert_color, self, "选择报警颜色")
        if c.isValid():
            self.alert_color = c
            self._update_color_indicator()
            
class SkillMappingDialog(QDialog):
    def __init__(self, player_data, blocks, current_mapping, autocast_configs, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"技能映射 - {player_data.get('name')}")
        self.resize(500, 600)
        self.mapping = current_mapping.copy() # Initialize with current mapping
        self.autocast_configs = autocast_configs.copy() # {skill_id: config_dict}
        self.blocks = blocks # Dictionary of block_id -> AlertBlock widget to get colors
        
        layout = QVBoxLayout(self)
        
        # Helper to create row
        def create_row(part_name, item_key):
            group = QGroupBox(part_name)
            g_layout = QVBoxLayout(group)
            
            item = player_data.get("equipment", {}).get(item_key)
            if not item:
                g_layout.addWidget(QLabel("无装备"))
                layout.addWidget(group)
                return

            spells = item.get("spells", [])
            if not spells:
                g_layout.addWidget(QLabel("无技能"))
            
            for idx, (spell_id, spell_name) in enumerate(spells):
                row = QHBoxLayout()
                row.addWidget(QLabel(spell_name))
                
                combo = QComboBox()
                combo.addItem("无 (None)", None)
                for bid in self.blocks.keys():
                    combo.addItem(f"区域 {bid}", bid)
                
                # Load existing mapping
                cur_val = current_mapping.get(spell_id)
                if cur_val:
                    idx_combo = combo.findData(cur_val)
                    if idx_combo >= 0:
                        combo.setCurrentIndex(idx_combo)
                
                # Color indicator
                color_lbl = QLabel("●")
                self._update_combo_color(combo, color_lbl)
                
                combo.currentIndexChanged.connect(lambda i, s=spell_id, c=combo, l=color_lbl: self._on_map_change(s, c, l))
                
                row.addWidget(combo)
                row.addWidget(color_lbl)
                
                # AutoCast Config Button
                ac_btn = QPushButton("+")
                ac_btn.setFixedSize(24, 24)
                ac_config = self.autocast_configs.get(spell_id, {})
                self._update_ac_btn_style(ac_btn, ac_config)
                ac_btn.clicked.connect(lambda checked=False, s=spell_id, b=ac_btn: self._open_ac_config(s, b))
                row.addWidget(ac_btn)
                
                g_layout.addLayout(row)
                
            layout.addWidget(group)

        create_row("主手 (Main Hand)", "main_hand")
        create_row("头盔 (Head)", "head")
        create_row("胸甲 (Armor)", "armor")
        create_row("鞋子 (Shoes)", "shoes")
        
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        
    def _open_ac_config(self, skill_id, btn):
        current_config = self.autocast_configs.get(skill_id, {})
        dlg = AutoCastConfigDialog(current_config, self)
        if dlg.exec() == QDialog.Accepted:
            new_config = dlg.get_config()
            self.autocast_configs[skill_id] = new_config
            self._update_ac_btn_style(btn, new_config)

    def _update_ac_btn_style(self, btn, config):
        if config.get("enabled"):
            btn.setStyleSheet("background-color: #388e3c; color: white; border-radius: 12px;")
            btn.setToolTip(f"AutoCast: {config.get('key')} (Delay: {config.get('delay')}ms)")
        else:
            btn.setStyleSheet("background-color: #555; color: #aaa; border-radius: 12px;")
            btn.setToolTip("AutoCast Disabled")

    def _on_map_change(self, skill_id, combo, color_lbl):
        val = combo.currentData()
        if val is None:
            if skill_id in self.mapping:
                del self.mapping[skill_id]
        else:
            self.mapping[skill_id] = val
        self._update_combo_color(combo, color_lbl)
            
    def _update_combo_color(self, combo, label):
        val = combo.currentData()
        if val and val in self.blocks:
            block = self.blocks[val]
            color = block.alert_color.name()
            label.setStyleSheet(f"color: {color}; font-size: 16px;")
        else:
            label.setStyleSheet("color: transparent;")
            
    def get_mapping(self):
        return self.mapping
        
    def get_autocast_configs(self):
        return self.autocast_configs

class CheckableComboBox(QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handle_item_pressed)
        self.setModel(QStandardItemModel(self))
        self.view().setAlternatingRowColors(True)

    def handle_item_pressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        self._update_text()

    def checked_items(self):
        checked_items = []
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            if item.checkState() == Qt.Checked:
                checked_items.append(item.text())
        return checked_items
    
    def checked_data(self):
        checked_data = []
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            if item.checkState() == Qt.Checked:
                checked_data.append(item.data())
        return checked_data

    def set_checked_data(self, data_list):
        if not data_list:
            return
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            if item.data() in data_list:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
        self._update_text()

    def add_item(self, text, data=None):
        item = QStandardItem(text)
        item.setCheckable(True)
        item.setCheckState(Qt.Unchecked)
        if data is not None:
            item.setData(data)
        self.model().appendRow(item)
        self._update_text()
    
    def _update_text(self):
        items = self.checked_items()
        if not items:
            self.setEditText("未选择") # None selected
            self.setCurrentText("未选择")
        else:
            text = ", ".join(items)
            self.setEditText(text)
            self.setCurrentText(text)

    def hidePopup(self):
        # Prevent hiding when clicking items, only hide when clicking outside
        # But for standard QComboBox, simple way is to keep it open or handle events.
        # For simplicity in this env, we let standard behavior but we need to ensure state is kept.
        # Actually standard combobox closes on click. We might need to override this.
        # A simple workaround for multi-select combo is often complex.
        # Let's try a simpler approach: Re-show if the click was on an item?
        # Or just use the standard behavior where it closes, user has to re-open. 
        # For better UX, let's just let it close for now, as implementing a persistent popup is involved.
        super().hidePopup()

class PlayerMonitorPanel(QWidget):
    save_requested = Signal(dict) # Emit config dict when save is requested

    def __init__(self, parent=None):
        super().__init__(parent)
        self._players = {} # Store player data: name -> player_info
        self._filtered_players = []
        self._monitoring_list = set()
        
        # Skill Monitor Data
        self._skill_mappings = {} # (player_name, skill_id) -> block_id
        self._autocast_configs = {} # (player_name, skill_id) -> config_dict
        self._alert_blocks = {} # block_id -> AlertBlock widget
        self._monitor_list_data = [] # List of names in monitor list
        
        self.init_ui()

    def init_ui(self):
        # Apply dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: "Segoe UI", sans-serif;
            }
            QLineEdit {
                background-color: #333;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 4px;
            }
            QComboBox {
                background-color: #333;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 4px;
            }
            QComboBox QLineEdit {
                background-color: #333;
                color: #ffffff;
                border: none;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #333;
                color: #ffffff;
                selection-background-color: #555;
                selection-color: #ffffff;
                outline: none;
            }
            QListWidget {
                background-color: #252526;
                border: 1px solid #333;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #37373d;
            }
            QTabWidget::pane {
                border: 1px solid #333;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ccc;
                padding: 8px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: #fff;
                font-weight: bold;
            }
            QSplitter::handle {
                background-color: #333;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_monitor_tab(), "监控配置 (Monitor Config)")
        self.tabs.addTab(self._create_skill_monitor_tab(), "技能监控 (Skill Monitor)")
        
        main_layout.addWidget(self.tabs)
        

    def _create_monitor_tab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Splitter for resizable layout
        splitter = QSplitter(Qt.Horizontal)
        
        # --- Left Side: List & Filters ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Filters
        filter_group = QWidget()
        filter_layout = QVBoxLayout(filter_group)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索玩家名称 (Search Name)...")
        self.search_input.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(QLabel("搜索 (Search):"))
        filter_layout.addWidget(self.search_input)
        
        # Guild Filter
        self.guild_combo = CheckableComboBox()
        self.guild_combo.setPlaceholderText("选择公会 (Guilds)")
        # self.guild_combo.model().itemChanged.connect(self._apply_filters) # Connect signal
        # Since we use custom handling, we might need to hook into hidePopup or create a signal
        self.guild_combo.view().pressed.connect(lambda: self._apply_filters()) 
        filter_layout.addWidget(QLabel("公会 (Guild):"))
        filter_layout.addWidget(self.guild_combo)
        
        # Alliance Filter
        self.alliance_combo = CheckableComboBox()
        self.alliance_combo.setPlaceholderText("选择联盟 (Alliances)")
        self.alliance_combo.view().pressed.connect(lambda: self._apply_filters())
        filter_layout.addWidget(QLabel("联盟 (Alliance):"))
        filter_layout.addWidget(self.alliance_combo)
        
        # Clear Player List Button
        clear_list_btn = QPushButton("清空玩家列表 (Clear List)")
        clear_list_btn.setStyleSheet("background-color: #d32f2f; color: white; margin-top: 10px;")
        clear_list_btn.clicked.connect(self._clear_player_list)
        filter_layout.addWidget(clear_list_btn)
        
        left_layout.addWidget(filter_group)
        
        # Player List
        self.player_list = QListWidget()
        self.player_list.currentItemChanged.connect(self._on_player_selected)
        left_layout.addWidget(self.player_list)
        
        splitter.addWidget(left_widget)
        
        # --- Right Side: Details ---
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)
        
        # Info Header
        self.info_header = QLabel("请选择玩家 (Select a player)")
        self.info_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.details_layout.addWidget(self.info_header)
        
        # Equipment Grid (3x3)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        
        # Slots definitions
        # Row 1: Bag, Head, Cape
        # Row 2: MainHand, Armor, OffHand
        # Row 3: Potion, Shoes, Food
        self.slots = {
            "bag": (0, 0), "head": (0, 1), "cape": (0, 2),
            "main_hand": (1, 0), "armor": (1, 1), "off_hand": (1, 2),
            "potion": (2, 0), "shoes": (2, 1), "food": (2, 2)
        }
        
        self.slot_widgets = {}
        
        for key, (row, col) in self.slots.items():
            frame = QFrame()
            frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
            frame.setFixedSize(80, 80)
            frame.setStyleSheet("""
                QFrame {
                    background-color: #2d2d2d; 
                    border: 1px solid #444; 
                    border-radius: 4px;
                }
                QLabel {
                    border: none;
                    background: transparent;
                }
            """)
            
            flayout = QVBoxLayout(frame)
            flayout.setContentsMargins(0, 0, 0, 0)
            flayout.setSpacing(0)
            
            lbl_item = QLabel("空")
            lbl_item.setAlignment(Qt.AlignCenter)
            lbl_item.setWordWrap(True)
            lbl_item.setStyleSheet("color: #666; font-size: 12px;")
            
            flayout.addWidget(lbl_item)
            
            self.grid_layout.addWidget(frame, row, col)
            self.slot_widgets[key] = lbl_item
            
        self.details_layout.addWidget(self.grid_widget)
        
        # Skills Info
        self.skills_label = QLabel("技能信息 (Skills)")
        self.skills_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.details_layout.addWidget(self.skills_label)
        
        self.skills_text = QLabel("暂无技能信息")
        self.skills_text.setWordWrap(True)
        self.skills_text.setStyleSheet("background-color: #222; padding: 10px; border-radius: 5px;")
        self.details_layout.addWidget(self.skills_text)
        
        # Monitor Button
        self.monitor_btn = QPushButton("加入监控 (Add to Monitor)")
        self.monitor_btn.clicked.connect(self._toggle_monitor)
        self.monitor_btn.setEnabled(False)
        self.details_layout.addWidget(self.monitor_btn)
        
        self.details_layout.addStretch()
        
        splitter.addWidget(self.details_widget)
        splitter.setStretchFactor(1, 2) # Right side wider
        
        layout.addWidget(splitter)
        return widget

    def _create_skill_monitor_tab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # --- Left: Monitor List ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_layout.addWidget(QLabel("监控列表 (Monitor List)"))
        
        self.monitor_list_widget = QListWidget()
        self.monitor_list_widget.itemClicked.connect(self._on_monitor_item_clicked)
        self.monitor_list_widget.itemDoubleClicked.connect(self._on_monitor_item_double_clicked)
        left_layout.addWidget(self.monitor_list_widget)
        
        btn_layout = QHBoxLayout()
        self.remove_btn = QPushButton("移除")
        self.remove_btn.clicked.connect(self._remove_from_monitor)
        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self._clear_monitor)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.clear_btn)
        left_layout.addLayout(btn_layout)
        
        splitter.addWidget(left_widget)
        
        # --- Right: Alert Grid ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Grid Config
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("网格设置 (Grid):"))
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 5)
        self.rows_spin.setValue(1)
        self.rows_spin.valueChanged.connect(self._update_alert_grid)
        config_layout.addWidget(QLabel("行"))
        config_layout.addWidget(self.rows_spin)
        
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 5)
        self.cols_spin.setValue(3)
        self.cols_spin.valueChanged.connect(self._update_alert_grid)
        config_layout.addWidget(QLabel("列"))
        config_layout.addWidget(self.cols_spin)
        
        save_btn = QPushButton("保存配置 (Save Config)")
        save_btn.clicked.connect(self._save_config)
        config_layout.addWidget(save_btn)
        
        config_layout.addStretch()
        
        right_layout.addLayout(config_layout)
        
        # Alert Grid Area
        self.alert_area = QScrollArea()
        self.alert_area.setWidgetResizable(True)
        self.alert_grid_container = QWidget()
        self.alert_grid_layout = QGridLayout(self.alert_grid_container)
        self.alert_area.setWidget(self.alert_grid_container)
        
        right_layout.addWidget(self.alert_area)
        
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 3)
        
        layout.addWidget(splitter)
        
        # Init grid
        self._update_alert_grid()
        
        return widget

    def _update_alert_grid(self):
        # Clear existing
        # Note: Ideally we should preserve state if resizing, but for simplicity we recreate.
        # OR better: reuse existing widgets if possible.
        # Recreating is safer to ensure correct layout.
        
        # Remove old widgets
        for i in reversed(range(self.alert_grid_layout.count())): 
            w = self.alert_grid_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        
        self._alert_blocks.clear()
        
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        
        # Default Palette (High distinctiveness)
        palette = [
            "#FF0000", # Red
            "#00FF00", # Green
            "#0000FF", # Blue
            "#FFFF00", # Yellow
            "#FF00FF", # Magenta
            "#00FFFF", # Cyan
            "#FF8000", # Orange
            "#800080", # Purple
            "#008080"  # Teal
        ]
        
        count = 1
        for r in range(rows):
            for c in range(cols):
                block = AlertBlock(count)
                
                # Apply default color from palette if available
                color_idx = (count - 1) % len(palette)
                block.set_config(QColor(palette[color_idx]), 1.0)
                block.config_changed.connect(self._save_config) # Auto save on block config change? Or manual. 
                # User asked to save after modification. Manual save button added.
                # But we can also auto-save or just rely on save button.
                # Let's rely on save button for now, but update internal state?
                # AlertBlock state is internal to it.
                
                self.alert_grid_layout.addWidget(block, r, c)
                self._alert_blocks[count] = block
                count += 1

    def _save_config(self):
        config_data = {
            "rows": self.rows_spin.value(),
            "cols": self.cols_spin.value(),
            "blocks": {},
            "mappings": [],
            "autocast": []
        }
        
        # Save block configs
        for bid, block in self._alert_blocks.items():
            config_data["blocks"][str(bid)] = {
                "color": block.alert_color.name(),
                "duration": block.duration
            }
            
        # Save mappings
        for (p_name, s_id), b_id in self._skill_mappings.items():
            config_data["mappings"].append({
                "player": p_name,
                "skill_id": s_id,
                "block_id": b_id
            })

        # Save autocast configs
        for (p_name, s_id), cfg in self._autocast_configs.items():
            config_data["autocast"].append({
                "player": p_name,
                "skill_id": s_id,
                "config": cfg
            })
        
        self.save_requested.emit(config_data)
        print("[PlayerMonitorPanel] Config save requested.")

    def load_config(self, config_data):
        if not config_data:
            return
            
        # Apply Grid Config
        rows = config_data.get("rows", 1)
        cols = config_data.get("cols", 3)
        
        # Block signals to avoid recreation spam if values change
        self.rows_spin.blockSignals(True)
        self.cols_spin.blockSignals(True)
        self.rows_spin.setValue(rows)
        self.cols_spin.setValue(cols)
        self.rows_spin.blockSignals(False)
        self.cols_spin.blockSignals(False)
        
        # Recreate grid
        self._update_alert_grid()
        
        # Apply Block Configs
        blocks_data = config_data.get("blocks", {})
        for bid_str, data in blocks_data.items():
            bid = int(bid_str)
            if bid in self._alert_blocks:
                block = self._alert_blocks[bid]
                color = QColor(data.get("color", "#ff0000"))
                duration = data.get("duration", 1.0)
                block.set_config(color, duration)

        # Load mappings
        self._skill_mappings.clear()
        mappings = config_data.get("mappings", [])
        for m in mappings:
            p_name = m.get("player")
            s_id = m.get("skill_id")
            b_id = m.get("block_id")
            if p_name and s_id is not None and b_id:
                self._skill_mappings[(p_name, s_id)] = b_id
                
        # Load autocast configs
        self._autocast_configs.clear()
        autocast_list = config_data.get("autocast", [])
        for ac in autocast_list:
            p_name = ac.get("player")
            s_id = ac.get("skill_id")
            cfg = ac.get("config")
            if p_name and s_id is not None and cfg:
                self._autocast_configs[(p_name, s_id)] = cfg
                
    def _on_monitor_item_clicked(self, item):
        name = item.data(Qt.UserRole)
        # Highlight logic: Find mapped skills for this player
        # and tell AlertBlocks to highlight them
        
        # First clear all highlights
        for block in self._alert_blocks.values():
            block.clear_highlight()
            
        player = self._players.get(name)
        if not player:
            return
        
        player_name = player.get("name")
        if not player_name:
            return

        # Find mapped skills
        for (p_name, s_id), b_id in self._skill_mappings.items():
            if p_name == player_name:
                block = self._alert_blocks.get(b_id)
                if block:
                    # Find skill name from equipment
                    skill_name = self._find_skill_name(player, s_id)
                    if skill_name:
                        block.highlight_skill(skill_name)

    def _find_skill_name(self, player, skill_id):
        equip = player.get("equipment", {})
        for item in equip.values():
            if not item: continue
            spells = item.get("spells", [])
            # Spells is now list of (id, name)
            for sid, sname in spells:
                if sid == skill_id:
                    return sname
        return None

    def _on_monitor_item_double_clicked(self, item):
        name = item.data(Qt.UserRole)
        player = self._players.get(name)
        if not player:
            return
            
        player_name = player.get("name")
        if not player_name:
            return

        # Get existing mapping for this player
        current_mapping = {}
        for (p_name, s_id), b_id in self._skill_mappings.items():
            if p_name == player_name:
                current_mapping[s_id] = b_id # Key is skill_id
        
        # Get existing autocast config for this player
        current_ac_configs = {}
        for (p_name, s_id), cfg in self._autocast_configs.items():
            if p_name == player_name:
                current_ac_configs[s_id] = cfg
        
        dlg = SkillMappingDialog(player, self._alert_blocks, current_mapping, current_ac_configs, self)
        if dlg.exec() == QDialog.Accepted:
            new_mapping = dlg.get_mapping() # Returns {skill_id: block_id}
            new_ac_configs = dlg.get_autocast_configs() # Returns {skill_id: config}
            
            # Update global mapping
            # First remove old entries for this player
            keys_to_remove = [k for k in self._skill_mappings if k[0] == player_name]
            for k in keys_to_remove:
                del self._skill_mappings[k]
            
            # Add new
            for s_id, b_id in new_mapping.items():
                self._skill_mappings[(player_name, s_id)] = b_id
                
            # Update global autocast config
            # Remove old
            keys_to_remove_ac = [k for k in self._autocast_configs if k[0] == player_name]
            for k in keys_to_remove_ac:
                del self._autocast_configs[k]
            
            # Add new autocast
            for s_id, cfg in new_ac_configs.items():
                if cfg: # Save even if disabled, user might want to keep settings
                    self._autocast_configs[(player_name, s_id)] = cfg
            
            # Re-highlight
            self._on_monitor_item_clicked(item)

    def _clear_player_list(self):
        # Clear data
        self._players.clear()
        self._monitoring_list.clear()
        self._skill_mappings.clear()
        self._autocast_configs.clear()
        
        # Clear UI
        self.player_list.clear()
        self.monitor_list_widget.clear()
        self.guild_combo.model().clear() # Clear filters
        self.alliance_combo.model().clear()
        self.search_input.clear()
        
        # Reset Details
        self.info_header.setText("请选择玩家 (Select a player)")
        for widget in self.slot_widgets.values():
            widget.setText("空")
            widget.setToolTip("")
        self.skills_text.setText("暂无技能信息")
        self.monitor_btn.setEnabled(False)
        self.monitor_btn.setText("加入监控 (Add to Monitor)")
        self.monitor_btn.setStyleSheet("")
        
        # Clear Alert Highlights
        for block in self._alert_blocks.values():
            block.clear_highlight()

    def _remove_from_monitor(self):
        row = self.monitor_list_widget.currentRow()
        if row >= 0:
            item = self.monitor_list_widget.takeItem(row)
            name = item.data(Qt.UserRole)
            if name in self._monitoring_list:
                self._monitoring_list.remove(name)
                
                # Remove mappings for this player
                keys_to_remove = [k for k in self._skill_mappings if k[0] == name]
                for k in keys_to_remove:
                    del self._skill_mappings[k]

                keys_to_remove_ac = [k for k in self._autocast_configs if k[0] == name]
                for k in keys_to_remove_ac:
                    del self._autocast_configs[k]

                # Sync config tab button state if selected
                current = self.player_list.currentItem()
                if current and current.data(Qt.UserRole) == name:
                    self._update_details(self._players.get(name))
            self._update_monitor_list_ui()

    def _clear_monitor(self):
        self._monitoring_list.clear()
        self._skill_mappings.clear()
        self._autocast_configs.clear()
        self.monitor_list_widget.clear()
        
        # Refresh details if needed
        current = self.player_list.currentItem()
        if current:
            self._update_details(self._players.get(current.data(Qt.UserRole)))

    def _update_monitor_list_ui(self):
        # Sync list widget with _monitoring_list set
        # Rebuilding is easiest
        self.monitor_list_widget.clear()
        for name in self._monitoring_list:
            player = self._players.get(name)
            if player:
                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, name)
                self.monitor_list_widget.addItem(item)

    def trigger_skill_alert(self, player_name, skill_id, skill_name):
        # Called by plugin
        
        # Check if player is monitored
        if player_name not in self._monitoring_list:
            return

        # Resolve player data
        player = self._players.get(player_name)
        if not player:
            return
            
        # Check mapping using (player_name, skill_id)
        block_id = self._skill_mappings.get((player_name, skill_id))
        
        if block_id:
            block = self._alert_blocks.get(block_id)
            if block:
                block.trigger(player_name, skill_name)
        
        # Auto Cast Logic
        ac_config = self._autocast_configs.get((player_name, skill_id))
        if ac_config and ac_config.get("enabled"):
            key = ac_config.get("key")
            if key:
                delay = ac_config.get("delay", 0)
                count = ac_config.get("count", 1)
                interval = ac_config.get("interval", 100)
                
                # Execute in QTimer to not block UI
                if delay > 0:
                    QTimer.singleShot(delay, lambda: self._execute_autocast(key, count, interval))
                else:
                    self._execute_autocast(key, count, interval)

    def _execute_autocast(self, key, count, interval):
        if count <= 0:
            return
        press_key(key)
        if count > 1:
            QTimer.singleShot(interval, lambda: self._execute_autocast(key, count - 1, interval))

    def add_player(self, player_data):
        """
        Add or update player data.
        player_data format expectation:
        {
            "oid": int,
            "name": str,
            ...
        }
        """
        raw_name = player_data.get("name")
        if not raw_name:
            return
            
        name = str(raw_name).strip()
        player_data["name"] = name # Ensure clean name in data
            
        self._players[name] = player_data
        
        # Update filters options if new guild/alliance
        guild = player_data.get("guild")
        if guild:
            self._add_filter_option(self.guild_combo, guild)
            
        alliance = player_data.get("alliance")
        if alliance:
            self._add_filter_option(self.alliance_combo, alliance)
            
        self._apply_filters()

    def _add_filter_option(self, combo: CheckableComboBox, text: str):
        # Check if exists
        model = combo.model()
        items = [model.item(i).text() for i in range(model.rowCount())]
        if text not in items:
            combo.add_item(text)

    def _apply_filters(self):
        search_text = self.search_input.text().lower()
        selected_guilds = set(self.guild_combo.checked_items())
        selected_alliances = set(self.alliance_combo.checked_items())
        
        self.player_list.clear()
        
        for name, p in self._players.items():
            guild = p.get("guild", "")
            alliance = p.get("alliance", "")
            
            # 1. Search filter
            if search_text:
                equipment = p.get("equipment") or {}
                main_hand = equipment.get("main_hand") or {}
                main_hand_name = main_hand.get("name", "").lower()
                
                if (search_text not in name.lower()) and (search_text not in main_hand_name):
                    continue
                
            # 2. Guild filter
            if selected_guilds and guild not in selected_guilds:
                continue
                
            # 3. Alliance filter
            if selected_alliances and alliance not in selected_alliances:
                continue
                
            # Determine Armor Type & Main Hand
            equip = p.get("equipment") or {}
            main_hand_data = equip.get("main_hand") or {}
            main_hand = main_hand_data.get("name", "None")
            
            armor_data = equip.get("armor") or {}
            armor_type = self._get_armor_type(armor_data.get("unique_name", ""))
            
            display_text = f"{name} | {main_hand} | {armor_type}"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, name)
            self.player_list.addItem(item)

    def _get_armor_type(self, unique_name):
        if not unique_name:
            return "Unknown"
        if "ARMOR_PLATE" in unique_name:
            return "板甲 (Plate)"
        elif "ARMOR_CLOTH" in unique_name:
            return "布甲 (Cloth)"
        elif "ARMOR_LEATHER" in unique_name:
            return "皮甲 (Leather)"
        return "Unknown"

    def _on_player_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        if not current:
            return
            
        name = current.data(Qt.UserRole)
        player = self._players.get(name)
        if not player:
            return
            
        self._update_details(player)

    def _update_details(self, player):
        name = player.get("name")
        self.info_header.setText(f"{name} [{player.get('guild', '')}]")
        
        equip = player.get("equipment") or {}
        
        # Update Grid
        for key, widget in self.slot_widgets.items():
            item_data = equip.get(key)
            if item_data:
                name_item = item_data.get("name", "Unknown")
                widget.setText(name_item)
                widget.setToolTip(name_item)
                widget.setStyleSheet("color: #e0e0e0; font-weight: bold; font-size: 12px;")
            else:
                widget.setText("空")
                widget.setToolTip("")
                widget.setStyleSheet("color: #666; font-size: 12px;")
                
        # Update Skills
        skills_text = []
        
        def format_skills(part_name, item_key, active_count, passive_count):
            item = equip.get(item_key)
            if not item:
                return
            spells = item.get("spells", [])
            # Assuming spells list contains (id, name) tuples now
            if spells:
                # Extract names for display
                spell_names = [s[1] for s in spells]
                skills_text.append(f"<b>{part_name} ({item.get('name')})</b>: {', '.join(spell_names)}")
        
        format_skills("主手 (Main Hand)", "main_hand", 3, 1)
        format_skills("头盔 (Head)", "head", 1, 1)
        format_skills("胸甲 (Armor)", "armor", 1, 2)
        format_skills("鞋子 (Shoes)", "shoes", 1, 1)
        
        if not skills_text:
            self.skills_text.setText("无技能信息")
        else:
            self.skills_text.setText("<br>".join(skills_text))
            
        # Update Button
        self.monitor_btn.setEnabled(True)
        if name in self._monitoring_list:
            self.monitor_btn.setText("取消监控 (Cancel Monitor)")
            self.monitor_btn.setStyleSheet("background-color: #d32f2f;")
        else:
            self.monitor_btn.setText("加入监控 (Add to Monitor)")
            self.monitor_btn.setStyleSheet("background-color: #388e3c;")

    def _toggle_monitor(self):
        current = self.player_list.currentItem()
        if not current:
            return
        name = current.data(Qt.UserRole)
        
        if name in self._monitoring_list:
            self._monitoring_list.remove(name)
        else:
            self._monitoring_list.add(name)
            
        self._update_monitor_list_ui() # Sync Skill Monitor Tab
            
        # Refresh button state
        player = self._players.get(name)
        self._update_details(player)
