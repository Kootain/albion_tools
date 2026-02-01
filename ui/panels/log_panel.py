from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QHBoxLayout, QLineEdit, QComboBox, QPushButton, QDialog, QDialogButtonBox
from PySide6.QtCore import QTimer
from base.event_codes import EventType, EventCodes
import os
import json
import time
import datetime

class LogPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_mode = "whitelist"
        self.filter_types = set()
        self.filter_codes = set()
        self.filter_combos = []
        
        # Log buffering
        self._log_buffer = []
        self._log_file_timer = QTimer(self)
        self._log_file_timer.timeout.connect(self._flush_logs_to_file)
        self._log_file_timer.start(2000) # Flush every 2 seconds
        
        # Ensure log dir
        self._log_dir = os.path.join(os.getcwd(), "logs", "system")
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir, exist_ok=True)
            
        self.init_ui()
        self._load_filter_state()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("系统日志 (System Logs)")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        filter_bar = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["白名单", "黑名单"])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self.types_input = QLineEdit()
        self.types_input.setPlaceholderText("EventType 列表，逗号分隔，如: Event,Request,Response 或 1,2,3")
        self.types_input.setStyleSheet("background-color: #333; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 4px;")
        self.codes_input = QLineEdit()
        self.codes_input.setPlaceholderText("EventCode 列表，逗号分隔，如: Move,HealthUpdate 或 3,6")
        self.codes_input.setStyleSheet("background-color: #333; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 4px;")
        self.types_input.textChanged.connect(self._on_types_changed)
        self.codes_input.textChanged.connect(self._on_codes_changed)
        filter_bar.addWidget(QLabel("模式"))
        filter_bar.addWidget(self.mode_combo)
        filter_bar.addWidget(QLabel("类型"))
        filter_bar.addWidget(self.types_input)
        filter_bar.addWidget(QLabel("代码"))
        filter_bar.addWidget(self.codes_input)
        self.config_btn = QPushButton("过滤配置…")
        self.config_btn.clicked.connect(self._open_filter_dialog)
        filter_bar.addWidget(self.config_btn)
        layout.addLayout(filter_bar)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas;")
        # Optimization: Limit max blocks (lines)
        self.log_text.document().setMaximumBlockCount(500) 
        layout.addWidget(self.log_text)

    def append_log(self, message: str):
        self._add_to_log(message)

    def append_event(self, event):
        etype = getattr(event, "type", None)
        ecode = getattr(event, "code", None)
        if etype is None or ecode is None:
            return
            
        # Ensure ints
        try:
            etype_val = int(etype)
            ecode_val = int(ecode)
        except:
            return

        if not self._should_display(etype_val, ecode_val):
            return

        etype_name = str(etype)
        ecode_name = str(ecode)

        if etype == EventType.Event:
            try:
                # Try to get Enum name
                ecode_enum = EventCodes(ecode)
                ecode_name = ecode_enum.name
            except Exception:
                pass
                
        try:
            etype_enum = EventType(etype)
            etype_name = etype_enum.name
        except Exception:
            pass

        ts = time.strftime('%H:%M:%S', time.localtime(int(time.time())))
        msg = f"{ts} [{etype_name}] [{ecode_name} ({ecode})] {event.raw_data}"
        self._add_to_log(msg)

    def _add_to_log(self, message: str):
        # Update UI
        self.log_text.append(message)
        # Buffer to file
        self._log_buffer.append(message)

    def _flush_logs_to_file(self):
        if not self._log_buffer:
            return
        
        lines = list(self._log_buffer)
        self._log_buffer.clear()
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"system_log_{today}.log"
        filepath = os.path.join(self._log_dir, filename)
        
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                for line in lines:
                    f.write(line + "\n")
        except Exception:
            pass # Ignore write errors to prevent crash

    def _on_mode_changed(self, idx: int):
        self.filter_mode = "whitelist" if idx == 0 else "blacklist"
        self._save_filter_state()

    def _on_types_changed(self, text: str):
        self.filter_types = self._parse_enum_list(text, EventType)
        self._save_filter_state()

    def _on_codes_changed(self, text: str):
        self.filter_codes = self._parse_enum_list(text, EventCodes)
        self._save_filter_state()

    def _parse_enum_list(self, text: str, enum_cls):
        items = [t.strip() for t in text.split(",") if t.strip()]
        result = set()
        for item in items:
            try:
                if item.isdigit():
                    result.add(int(item))
                else:
                    # Get enum value
                    e = getattr(enum_cls, item)
                    result.add(e.value)
            except Exception:
                continue
        return result

    def _should_display(self, etype_val, ecode_val) -> bool:
        # Check combos first
        in_combos = False
        for types_set, codes_set in self.filter_combos:
            t_ok = (not types_set) or (etype_val in types_set)
            c_ok = (not codes_set) or (ecode_val in codes_set)
            if t_ok and c_ok:
                in_combos = True
                break

        if self.filter_mode == "whitelist":
            # If no filters at all, show everything
            if not self.filter_types and not self.filter_codes and not self.filter_combos:
                return True
            
            # Check basic filters (AND logic between Type and Code inputs)
            # Only effective if at least one is set
            has_basic = bool(self.filter_types or self.filter_codes)
            basic_match = False
            if has_basic:
                type_ok = (not self.filter_types) or (etype_val in self.filter_types)
                code_ok = (not self.filter_codes) or (ecode_val in self.filter_codes)
                basic_match = type_ok and code_ok
            
            return basic_match or in_combos
            
        else: # blacklist
            if not self.filter_types and not self.filter_codes and not self.filter_combos:
                return True
                
            # Basic filters: OR logic for blacklist (Block this Type OR Block this Code)
            if self.filter_types and etype_val in self.filter_types:
                return False
            if self.filter_codes and ecode_val in self.filter_codes:
                return False
                
            # Combos: Block specific combinations
            if in_combos:
                return False
                
            return True

    def _open_filter_dialog(self):
        dlg = FilterDialog(self)
        dlg.set_mode(self.filter_mode)
        dlg.set_combos(self.filter_combos)
        if dlg.exec() == QDialog.Accepted:
            self.filter_mode = dlg.get_mode()
            self.mode_combo.setCurrentIndex(0 if self.filter_mode == "whitelist" else 1)
            self.filter_combos = dlg.get_combos()
            self._save_filter_state()

    def _config_file_path(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        cfg_dir = os.path.join(base_dir, ".config")
        os.makedirs(cfg_dir, exist_ok=True)
        return os.path.join(cfg_dir, "log_panel.json")

    def _save_filter_state(self):
        data = {
            "mode": self.filter_mode,
            "types_text": self.types_input.text(),
            "codes_text": self.codes_input.text(),
            "combos_lines": [self._combo_to_line(tset, cset) for (tset, cset) in self.filter_combos],
        }
        try:
            with open(self._config_file_path(), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _load_filter_state(self):
        path = self._config_file_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            mode = data.get("mode")
            if mode in ("whitelist", "blacklist"):
                self.filter_mode = mode
                self.mode_combo.setCurrentIndex(0 if mode == "whitelist" else 1)
            types_text = data.get("types_text", "")
            codes_text = data.get("codes_text", "")
            self.types_input.setText(types_text)
            self.codes_input.setText(codes_text)
            combos_lines = data.get("combos_lines", [])
            self.filter_combos = self._parse_combos_lines(combos_lines)
        except Exception:
            pass

    def _combo_to_line(self, types_set, codes_set):
        types_txt = ",".join([str(int(t)) for t in types_set]) if types_set else ""
        codes_txt = ",".join([str(int(c)) for c in codes_set]) if codes_set else ""
        return f"types: {types_txt} | codes: {codes_txt}"

    def _parse_combos_lines(self, lines):
        combos = []
        for line in lines:
            parts = [p.strip() for p in str(line).split("|")]
            types_txt = ""
            codes_txt = ""
            for p in parts:
                if p.lower().startswith("types"):
                    _, _, val = p.partition(":")
                    types_txt = val.strip()
                elif p.lower().startswith("codes"):
                    _, _, val = p.partition(":")
                    codes_txt = val.strip()
            types_set = self._parse_enum_list(types_txt, EventType)
            codes_set = self._parse_enum_list(codes_txt, EventCodes)
            combos.append((types_set, codes_set))
        return combos


class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("过滤配置")
        self.mode_combo = QComboBox(self)
        self.mode_combo.addItems(["白名单", "黑名单"])
        self.combos_edit = QTextEdit(self)
        self.combos_edit.setPlaceholderText(
            "每行一个组合：types: Event,Request | codes: Move,HealthUpdate\n"
            "类型或代码留空表示通配；也支持数值，例如 types: 1 | codes: 3,6"
        )
        self.combos_edit.setStyleSheet("background-color: #333; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 6px;")
        layout = QVBoxLayout(self)
        hl = QHBoxLayout()
        hl.addWidget(QLabel("模式"))
        hl.addWidget(self.mode_combo)
        layout.addLayout(hl)
        layout.addWidget(QLabel("组合列表"))
        layout.addWidget(self.combos_edit)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def set_mode(self, mode: str):
        self.mode_combo.setCurrentIndex(0 if mode == "whitelist" else 1)

    def get_mode(self) -> str:
        return "whitelist" if self.mode_combo.currentIndex() == 0 else "blacklist"

    def set_combos(self, combos):
        lines = []
        for types_set, codes_set in combos:
            types_txt = ",".join([str(int(t)) for t in types_set]) if types_set else ""
            codes_txt = ",".join([str(int(c)) for c in codes_set]) if codes_set else ""
            lines.append(f"types: {types_txt} | codes: {codes_txt}")
        self.combos_edit.setText("\n".join(lines))

    def get_combos(self):
        lines = [l.strip() for l in self.combos_edit.toPlainText().splitlines() if l.strip()]
        combos = []
        for line in lines:
            parts = [p.strip() for p in line.split("|")]
            types_txt = ""
            codes_txt = ""
            for p in parts:
                if p.lower().startswith("types"):
                    _, _, val = p.partition(":")
                    types_txt = val.strip()
                elif p.lower().startswith("codes"):
                    _, _, val = p.partition(":")
                    codes_txt = val.strip()
            types_set = self._parse_enum_list(types_txt, EventType)
            codes_set = self._parse_enum_list(codes_txt, EventCodes)
            combos.append((types_set, codes_set))
        return combos

    def _parse_enum_list(self, text: str, enum_cls):
        items = [t.strip() for t in text.split(",") if t.strip()]
        result = set()
        for item in items:
            try:
                if item.isdigit():
                    result.add(enum_cls(int(item)))
                else:
                    result.add(getattr(enum_cls, item))
            except Exception:
                continue
        return result
