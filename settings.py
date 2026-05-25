import os
import sys
import ctypes
import tempfile
import winreg

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QComboBox, QCheckBox, QPushButton, QLineEdit, QFileDialog,
    QFrame, QScrollArea, QMessageBox, QStackedWidget, QButtonGroup
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
)
from PyQt6.QtGui import QKeyEvent

import config
import dsr


# ===== 主题 / 系统外观 =====

def _is_dark_mode() -> bool:
    try:
        k = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        v, _ = winreg.QueryValueEx(k, "AppsUseLightTheme")
        return v == 0
    except Exception:
        return False


def _is_win11() -> bool:
    try:
        v = sys.getwindowsversion()
        return v.major == 10 and v.build >= 22000
    except Exception:
        return False


def _enable_mica(hwnd: int, dark: bool):
    dwm = ctypes.windll.dwmapi
    try:
        v = ctypes.c_int(1 if dark else 0)
        dwm.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(v), ctypes.sizeof(v))
    except Exception:
        pass
    if _is_win11():
        try:
            v = ctypes.c_int(2)  # DWMSBT_MAINWINDOW
            dwm.DwmSetWindowAttribute(hwnd, 38, ctypes.byref(v), ctypes.sizeof(v))
        except Exception:
            pass


def _check_icon_path() -> str:
    path = os.path.join(tempfile.gettempdir(), "_supershot_check.svg")
    if not os.path.exists(path):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
               '<path d="M3.5 8.5L6.5 11.5L12.5 5.5" stroke="white" '
               'stroke-width="2.2" fill="none" stroke-linecap="round" '
               'stroke-linejoin="round"/></svg>')
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
    return path.replace("\\", "/")


def _qss(dark: bool) -> str:
    accent       = "#0067c0"
    accent_hover = "#1f7ec9"
    accent_press = "#005ba8"
    accent_tint  = "rgba(0, 103, 192, 0.12)"

    if dark:
        bg_root      = "transparent"
        sidebar_bg   = "transparent"
        text         = "#f3f3f3"
        text_sub     = "#c4c4c4"
        text_hint    = "#a0a0a0"
        card_bg      = "rgba(255, 255, 255, 0.05)"
        card_border  = "rgba(255, 255, 255, 0.08)"
        ctrl_bg      = "rgba(255, 255, 255, 0.06)"
        ctrl_hover   = "rgba(255, 255, 255, 0.10)"
        ctrl_focus   = "rgba(255, 255, 255, 0.15)"
        ctrl_border  = "rgba(255, 255, 255, 0.10)"
        chk_border   = "#a0a0a0"
        list_bg      = "#2b2b2b"
        list_border  = "rgba(255, 255, 255, 0.10)"
        nav_hover    = "rgba(255, 255, 255, 0.08)"
        bottom_bg    = "transparent"
        bottom_brd   = "rgba(255, 255, 255, 0.08)"
    else:
        bg_root      = "#f3f3f3"           # Win11 设置浅色背景
        sidebar_bg   = "#fafafa"           # 侧边栏比内容区略浅
        text         = "#1a1a1a"
        text_sub     = "#424242"
        text_hint    = "#707070"
        card_bg      = "#ffffff"
        card_border  = "rgba(0, 0, 0, 0.08)"
        ctrl_bg      = "#ffffff"
        ctrl_hover   = "#f5f5f5"
        ctrl_focus   = "#ffffff"
        ctrl_border  = "rgba(0, 0, 0, 0.12)"
        chk_border   = "#8a8a8a"
        list_bg      = "#ffffff"
        list_border  = "rgba(0, 0, 0, 0.12)"
        nav_hover    = "rgba(0, 0, 0, 0.05)"
        bottom_bg    = "#fafafa"
        bottom_brd   = "rgba(0, 0, 0, 0.08)"

    check_url = _check_icon_path()

    return f"""
    QWidget#root {{ background: {bg_root}; }}
    QWidget {{ color: {text}; font-family: "Segoe UI Variable", "Segoe UI"; font-size: 13px; }}

    QFrame#sidebar {{
        background-color: {sidebar_bg};
        border-right: 1px solid {card_border};
    }}
    QFrame#bottomBar {{
        background-color: {bottom_bg};
        border-top: 1px solid {bottom_brd};
    }}

    QLabel#appTitle {{ font-size: 18px; font-weight: 600; color: {text}; }}
    QLabel#appSubtitle {{ color: {text_hint}; font-size: 11px; }}
    QLabel#pageTitle {{ font-size: 22px; font-weight: 600; color: {text}; }}
    QLabel#pageSubtitle {{ color: {text_hint}; font-size: 12px; padding-bottom: 8px; }}
    QLabel#cardTitle {{ font-size: 14px; font-weight: 600; color: {text}; padding-bottom: 6px; }}
    QLabel#fieldLabel {{ color: {text_sub}; font-size: 13px; }}
    QLabel#hint {{ color: {text_hint}; font-size: 11px; }}
    QLabel#info {{ color: {text}; font-size: 13px; font-weight: 500; }}

    QFrame#card {{
        background-color: {card_bg};
        border: 1px solid {card_border};
        border-radius: 8px;
    }}

    QPushButton#nav {{
        background-color: transparent;
        border: 0px solid transparent;
        outline: 0;
        border-radius: 6px;
        text-align: left;
        padding: 9px 14px;
        color: {text};
        font-size: 13px;
        min-height: 20px;
    }}
    QPushButton#nav:hover {{ background-color: {nav_hover}; border: 0px solid transparent; }}
    QPushButton#nav:checked {{
        background-color: {accent_tint};
        color: {accent};
        font-weight: 600;
        border: 0px solid transparent;
    }}
    QPushButton#nav:focus {{ outline: 0; border: 0px solid transparent; }}

    QPushButton#hotkey {{
        background-color: {ctrl_bg};
        border: 1px solid {ctrl_border};
        border-radius: 6px;
        padding: 9px 14px;
        color: {text};
        font-size: 13px;
        text-align: left;
        font-family: "Segoe UI Variable", "Segoe UI", Consolas;
        min-height: 20px;
    }}
    QPushButton#hotkey:hover {{ background-color: {ctrl_hover}; border-color: {accent}; }}
    QPushButton#hotkey[recording="true"] {{
        background-color: rgba(0, 103, 192, 0.10);
        border: 1.5px solid {accent};
        color: {accent};
        font-weight: 600;
    }}

    QPushButton {{
        background-color: {ctrl_bg};
        border: 1px solid {ctrl_border};
        border-radius: 6px;
        padding: 8px 18px;
        color: {text};
        font-size: 13px;
        min-height: 18px;
    }}
    QPushButton:hover {{ background-color: {ctrl_hover}; }}
    QPushButton:pressed {{ background-color: {ctrl_focus}; }}

    QPushButton#primary {{
        background-color: {accent};
        color: white;
        border: 1px solid {accent};
        font-weight: 600;
    }}
    QPushButton#primary:hover {{ background-color: {accent_hover}; border-color: {accent_hover}; }}
    QPushButton#primary:pressed {{ background-color: {accent_press}; border-color: {accent_press}; }}

    QComboBox, QLineEdit {{
        background-color: {ctrl_bg};
        border: 1px solid {ctrl_border};
        border-radius: 6px;
        padding: 7px 12px;
        color: {text};
        font-size: 13px;
        min-height: 18px;
        selection-background-color: {accent};
    }}
    QComboBox:hover, QLineEdit:hover {{ background-color: {ctrl_hover}; }}
    QComboBox:focus, QLineEdit:focus {{
        border: 1px solid {accent};
        background-color: {ctrl_focus};
    }}
    QComboBox::drop-down {{ border: none; width: 28px; }}
    QComboBox::down-arrow {{ width: 10px; height: 10px; }}
    QComboBox QAbstractItemView {{
        background-color: {list_bg};
        border: 1px solid {list_border};
        border-radius: 6px;
        padding: 4px;
        outline: 0;
        selection-background-color: {accent_tint};
        selection-color: {text};
    }}

    QCheckBox {{ spacing: 10px; color: {text}; font-size: 13px; padding: 6px 0; }}
    QCheckBox::indicator {{
        width: 18px; height: 18px;
        border: 1.5px solid {chk_border};
        border-radius: 4px;
        background-color: transparent;
    }}
    QCheckBox::indicator:hover {{ border-color: {accent}; }}
    QCheckBox::indicator:checked {{
        background-color: {accent};
        border-color: {accent};
        image: url({check_url});
    }}

    QScrollArea {{ border: none; background: transparent; }}
    QScrollBar:vertical {{ background: transparent; width: 8px; margin: 4px 2px; }}
    QScrollBar::handle:vertical {{
        background: rgba(128, 128, 128, 0.5);
        border-radius: 3px; min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{ background: rgba(128, 128, 128, 0.8); }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none; background: none; height: 0;
    }}
    """


# ===== 快捷键采集器 =====

class HotkeyCapture(QPushButton):
    """点击进入录入模式，按下任意按键组合即记录。"""

    changed = pyqtSignal(str)

    _SPECIAL = {
        Qt.Key.Key_Space: "space",
        Qt.Key.Key_Return: "enter",
        Qt.Key.Key_Enter: "enter",
        Qt.Key.Key_Tab: "tab",
        Qt.Key.Key_Backspace: "backspace",
        Qt.Key.Key_Delete: "delete",
        Qt.Key.Key_Home: "home",
        Qt.Key.Key_End: "end",
        Qt.Key.Key_PageUp: "page up",
        Qt.Key.Key_PageDown: "page down",
        Qt.Key.Key_Insert: "insert",
        Qt.Key.Key_Print: "print screen",
        Qt.Key.Key_ScrollLock: "scroll lock",
        Qt.Key.Key_Pause: "pause",
        Qt.Key.Key_Left: "left",
        Qt.Key.Key_Right: "right",
        Qt.Key.Key_Up: "up",
        Qt.Key.Key_Down: "down",
    }

    _DISPLAY = {
        "ctrl": "Ctrl", "shift": "Shift", "alt": "Alt",
        "windows": "Win", "win": "Win", "cmd": "Cmd",
        "space": "Space", "enter": "Enter", "tab": "Tab",
        "backspace": "Backspace", "delete": "Delete",
        "home": "Home", "end": "End",
        "page up": "Page Up", "page down": "Page Down",
        "insert": "Insert", "print screen": "Print Screen",
        "scroll lock": "Scroll Lock", "pause": "Pause",
        "left": "←", "right": "→", "up": "↑", "down": "↓",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._capturing = False
        self._hotkey = ""
        self.setObjectName("hotkey")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.clicked.connect(self._start_capture)

    def hotkey(self) -> str:
        return self._hotkey

    def setHotkey(self, hk: str):
        self._hotkey = hk or ""
        self._refresh_text()

    def _refresh_text(self):
        if not self._hotkey:
            self.setText("未设置  ·  点击录入")
            return
        parts = self._hotkey.split("+")
        pretty = " + ".join(self._DISPLAY.get(p.lower(), p.upper()) for p in parts)
        self.setText(pretty)

    def _start_capture(self):
        self._capturing = True
        self.setProperty("recording", True)
        self.style().unpolish(self)
        self.style().polish(self)
        self.setText("按下快捷键…  (Esc 取消)")

    def _end_capture(self):
        self._capturing = False
        self.setProperty("recording", False)
        self.style().unpolish(self)
        self.style().polish(self)
        self._refresh_text()

    def keyPressEvent(self, e: QKeyEvent):
        if not self._capturing:
            super().keyPressEvent(e)
            return

        key = e.key()
        mods = e.modifiers()

        if key == Qt.Key.Key_Escape:
            self._end_capture()
            return

        # 跳过单独按下的修饰键
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift,
                   Qt.Key.Key_Alt, Qt.Key.Key_Meta, Qt.Key.Key_AltGr):
            return

        # 组装
        parts = []
        if mods & Qt.KeyboardModifier.ControlModifier: parts.append("ctrl")
        if mods & Qt.KeyboardModifier.AltModifier:     parts.append("alt")
        if mods & Qt.KeyboardModifier.ShiftModifier:   parts.append("shift")
        if mods & Qt.KeyboardModifier.MetaModifier:    parts.append("windows")

        main = self._key_str(key, e.text())
        if main is None:
            return  # 不识别的键，等下一次按

        parts.append(main)
        new = "+".join(parts)
        self._hotkey = new
        self._end_capture()
        self.changed.emit(new)

    def _key_str(self, key, text):
        if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            return chr(key).lower()
        if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            return chr(key)
        if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F24:
            return f"f{key - Qt.Key.Key_F1 + 1}"
        if key in self._SPECIAL:
            return self._SPECIAL[key]
        if text and len(text) == 1 and text.isprintable():
            return text.lower()
        return None

    def focusOutEvent(self, e):
        if self._capturing:
            self._end_capture()
        super().focusOutEvent(e)


# ===== 组件辅助 =====

def _card(title: str | None = None) -> tuple[QFrame, QVBoxLayout]:
    f = QFrame()
    f.setObjectName("card")
    layout = QVBoxLayout(f)
    layout.setContentsMargins(20, 16, 20, 16)
    layout.setSpacing(8)
    if title:
        t = QLabel(title)
        t.setObjectName("cardTitle")
        layout.addWidget(t)
    return f, layout


def _field(label_text: str, widget: QWidget, hint: str = "") -> QWidget:
    box = QWidget()
    v = QVBoxLayout(box)
    v.setContentsMargins(0, 4, 0, 4)
    v.setSpacing(4)
    lbl = QLabel(label_text); lbl.setObjectName("fieldLabel")
    v.addWidget(lbl)
    v.addWidget(widget)
    if hint:
        h = QLabel(hint); h.setObjectName("hint")
        v.addWidget(h)
    return box


def _page_wrap(title: str, subtitle: str) -> tuple[QScrollArea, QVBoxLayout]:
    """每个内容页的统一外壳：滚动 + 标题 + 副标题。"""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    inner = QWidget()
    scroll.setWidget(inner)
    v = QVBoxLayout(inner)
    v.setContentsMargins(28, 24, 28, 24)
    v.setSpacing(12)
    t = QLabel(title); t.setObjectName("pageTitle")
    v.addWidget(t)
    if subtitle:
        s = QLabel(subtitle); s.setObjectName("pageSubtitle")
        v.addWidget(s)
    return scroll, v


# ===== 主窗口 =====

class SettingsWindow(QWidget):
    saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setObjectName("root")
        self.setWindowTitle("超分截图  ·  设置")
        self.resize(960, 560)
        self.setMinimumSize(820, 460)

        # 强制浅色主题，不用 Mica（避免某些系统下变全黑）
        self._dark = False
        self.setStyleSheet(_qss(self._dark))

        self._build_ui()
        self._load_values()

        self.setWindowOpacity(0.0)
        self._fade = QPropertyAnimation(self, b"windowOpacity")
        self._fade.setDuration(90)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.setEasingCurve(QEasingCurve.Type.OutCubic)

    def showEvent(self, e):
        super().showEvent(e)
        self._fade.start()

    # --- 顶层布局 ---
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 左侧栏
        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        # 右侧（堆叠内容 + 底部按钮栏）
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._page_system())
        self.stack.addWidget(self._page_capture())
        self.stack.addWidget(self._page_file())
        self.stack.addWidget(self._page_hotkey())
        rv.addWidget(self.stack, 1)
        rv.addWidget(self._build_bottom_bar())

        root.addWidget(right, 1)

    # --- 侧边栏 ---
    def _build_sidebar(self) -> QFrame:
        side = QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth(220)
        v = QVBoxLayout(side)
        v.setContentsMargins(16, 22, 16, 16)
        v.setSpacing(4)

        # 标题区
        title = QLabel("超分截图")
        title.setObjectName("appTitle")
        v.addWidget(title)
        sub = QLabel("基于 DSR / VSR 的原生超分")
        sub.setObjectName("appSubtitle")
        sub.setWordWrap(True)
        v.addWidget(sub)
        v.addSpacing(20)

        # 导航按钮
        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)
        self._nav_group.buttonClicked.connect(
            lambda btn: self.stack.setCurrentIndex(btn.property("page"))
        )
        for idx, label in enumerate(["系统信息", "截图", "文件", "热键"]):
            b = QPushButton(label)
            b.setObjectName("nav")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setProperty("page", idx)
            self._nav_group.addButton(b, idx)
            v.addWidget(b)
            if idx == 0:
                b.setChecked(True)

        v.addStretch()
        return side

    # --- 内容页 ---
    def _page_system(self) -> QScrollArea:
        scroll, v = _page_wrap("系统信息", "当前显卡与显示模式信息。")

        adapter = dsr.get_adapter_name()
        vendor = dsr.detect_vendor()
        cur = dsr._current()
        tech_map = {
            "NVIDIA": "DSR · Dynamic Super Resolution",
            "AMD":    "VSR · Virtual Super Resolution",
            "Intel":  "无（Intel 集显不支持）",
            "Other":  "未知",
        }

        card, c = _card()
        grid = QGridLayout()
        grid.setHorizontalSpacing(28)
        grid.setVerticalSpacing(12)

        def row(r, k, val):
            kl = QLabel(k); kl.setObjectName("fieldLabel")
            vl = QLabel(val); vl.setObjectName("info")
            vl.setWordWrap(True)
            grid.addWidget(kl, r, 0, Qt.AlignmentFlag.AlignTop)
            grid.addWidget(vl, r, 1)

        row(0, "显卡", adapter)
        row(1, "厂商", vendor)
        row(2, "超分技术", tech_map.get(vendor, "未知"))
        row(3, "当前分辨率",
            f"{cur.dmPelsWidth} × {cur.dmPelsHeight}  @ {cur.dmDisplayFrequency} Hz")
        target_ok = dsr.find_mode(config.TARGET_WIDTH, config.TARGET_HEIGHT) is not None
        row(4, "目标可用",
            f"{config.TARGET_WIDTH} × {config.TARGET_HEIGHT}  "
            + ("✓ 已就绪" if target_ok else "✗ 不可用（将走插值降级）"))
        grid.setColumnStretch(1, 1)
        c.addLayout(grid)
        v.addWidget(card)
        v.addStretch()
        return scroll

    def _page_capture(self) -> QScrollArea:
        scroll, v = _page_wrap("截图", "选择目标分辨率与降级行为。")

        card, c = _card()
        self.resolution_combo = QComboBox()
        cur = dsr._current()
        cur_w, cur_h = cur.dmPelsWidth, cur.dmPelsHeight
        for w, h in dsr.list_resolutions():
            if w >= cur_w and h >= cur_h:
                tag = ""
                if (w, h) == (3840, 2160): tag = "  · 4K"
                elif (w, h) == (2560, 1440): tag = "  · 2K"
                elif (w, h) == (cur_w, cur_h): tag = "  · 当前（不切换）"
                self.resolution_combo.addItem(f"{w} × {h}{tag}", (w, h))
        c.addWidget(_field(
            "目标分辨率",
            self.resolution_combo,
            "截图时临时切换到此分辨率，获取原生超分数据。选择当前则不切换。"
        ))

        self.scale_combo = QComboBox()
        for s in [2, 3, 4, 6, 8]:
            self.scale_combo.addItem(f"{s}× 放大", s)
        c.addWidget(_field(
            "插值倍数（降级用）",
            self.scale_combo,
            "目标分辨率不可用时，回退到 LANCZOS 插值放大。"
        ))
        v.addWidget(card)
        v.addStretch()
        return scroll

    def _page_file(self) -> QScrollArea:
        scroll, v = _page_wrap("文件", "保存路径与输出行为。")

        card, c = _card()
        row_dir = QHBoxLayout()
        row_dir.setSpacing(8)
        self.save_dir_edit = QLineEdit()
        self.save_dir_edit.setPlaceholderText("默认: 桌面/Screenshots")
        browse_btn = QPushButton("浏览…")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self._browse_dir)
        row_dir.addWidget(self.save_dir_edit, 1)
        row_dir.addWidget(browse_btn)

        wrap = QWidget()
        wl = QVBoxLayout(wrap); wl.setContentsMargins(0, 4, 0, 4); wl.setSpacing(4)
        kl = QLabel("保存路径"); kl.setObjectName("fieldLabel")
        wl.addWidget(kl); wl.addLayout(row_dir)
        c.addWidget(wrap)

        self.auto_save_check = QCheckBox("自动保存到文件")
        self.auto_copy_check = QCheckBox("自动复制到剪贴板")
        c.addWidget(self.auto_save_check)
        c.addWidget(self.auto_copy_check)
        v.addWidget(card)
        v.addStretch()
        return scroll

    def _page_hotkey(self) -> QScrollArea:
        scroll, v = _page_wrap("热键", "全局快捷键设置。")

        card, c = _card()
        self.hotkey_capture = HotkeyCapture()
        c.addWidget(_field(
            "截图快捷键",
            self.hotkey_capture,
            "点击后按下任意组合键即可录入，按 Esc 取消。"
        ))
        v.addWidget(card)
        v.addStretch()
        return scroll

    # --- 底部按钮栏 ---
    def _build_bottom_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("bottomBar")
        h = QHBoxLayout(bar)
        h.setContentsMargins(24, 14, 24, 14)
        h.addStretch()
        cancel = QPushButton("取消")
        cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel.setMinimumWidth(96)
        cancel.clicked.connect(self.close)
        save = QPushButton("保存")
        save.setObjectName("primary")
        save.setCursor(Qt.CursorShape.PointingHandCursor)
        save.setMinimumWidth(96)
        save.setDefault(True)
        save.clicked.connect(self._save_and_close)
        h.addWidget(cancel)
        h.addSpacing(8)
        h.addWidget(save)
        return bar

    # --- 加载/保存 ---
    def _load_values(self):
        target = (config.TARGET_WIDTH, config.TARGET_HEIGHT)
        for i in range(self.resolution_combo.count()):
            if self.resolution_combo.itemData(i) == target:
                self.resolution_combo.setCurrentIndex(i)
                break
        for i in range(self.scale_combo.count()):
            if self.scale_combo.itemData(i) == config.SCALE:
                self.scale_combo.setCurrentIndex(i)
                break
        self.save_dir_edit.setText(config.SAVE_DIR or "")
        self.auto_save_check.setChecked(config.AUTO_SAVE)
        self.auto_copy_check.setChecked(config.AUTO_COPY)
        self.hotkey_capture.setHotkey(config.HOTKEY)

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(
            self, "选择保存目录", self.save_dir_edit.text() or "")
        if d:
            self.save_dir_edit.setText(d)

    def _save_and_close(self):
        w, h = self.resolution_combo.currentData()
        config.TARGET_WIDTH  = w
        config.TARGET_HEIGHT = h
        config.SCALE         = self.scale_combo.currentData()
        config.SAVE_DIR      = self.save_dir_edit.text().strip() or None
        config.AUTO_SAVE     = self.auto_save_check.isChecked()
        config.AUTO_COPY     = self.auto_copy_check.isChecked()
        config.HOTKEY        = self.hotkey_capture.hotkey() or "alt+shift+s"
        try:
            config.save()
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"无法写入配置文件: {e}")
            return
        fade = QPropertyAnimation(self, b"windowOpacity", self)
        fade.setDuration(70)
        fade.setStartValue(1.0)
        fade.setEndValue(0.0)
        fade.setEasingCurve(QEasingCurve.Type.InCubic)
        fade.finished.connect(self._finish_close)
        fade.start()

    def _finish_close(self):
        self.saved.emit()
        self.close()
