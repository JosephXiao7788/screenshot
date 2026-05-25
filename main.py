import sys
import os
import socket
import threading
import ctypes
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QColor
import keyboard


def _resource_path(name: str) -> str:
    """兼容 PyInstaller 打包后查找资源文件。"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)

# 声明本进程 Per-Monitor DPI 感知，避免分辨率切换时坐标被自动缩放
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import config
config.load()    # 启动时从 config.json 读取

import capture
import dsr
from overlay import Overlay, FreezeOverlay
from settings import SettingsWindow


_lock_sock = None
def _acquire_single_instance():
    global _lock_sock
    _lock_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        _lock_sock.bind(("127.0.0.1", 47291))
        _lock_sock.listen(1)
        return True
    except OSError:
        return False


class Signals(QObject):
    take     = pyqtSignal()
    captured = pyqtSignal(object, bool)


signals  = Signals()
tray     = None
_overlay = None
_freeze  = None
_settings_window = None
_hotkey_handle   = None


def on_capture_done(img, is_native):
    global _freeze, _overlay
    if _freeze:
        _freeze.close()
        _freeze = None

    path = None
    if config.AUTO_SAVE:
        path = capture.save_image(img)
    if config.AUTO_COPY:
        capture.image_to_clipboard(img)

    if is_native:
        quality = f"原生 {config.TARGET_WIDTH}×{config.TARGET_HEIGHT}"
    else:
        quality = f"{config.SCALE}x 插值"
    tray.showMessage(
        "截图完成",
        quality + (f"  已保存: {path}" if path else "  已复制到剪贴板"),
        QSystemTrayIcon.MessageIcon.Information,
        2000,
    )
    _overlay = None


def on_done(x1, y1, x2, y2):
    global _freeze
    _freeze = FreezeOverlay()
    _freeze.show()
    QApplication.processEvents()

    def worker():
        img, is_native = capture.capture_and_scale(x1, y1, x2, y2)
        signals.captured.emit(img, is_native)

    threading.Thread(target=worker, daemon=True).start()


def open_overlay():
    global _overlay
    if _overlay is not None:
        return
    _overlay = Overlay(on_done)


def open_settings():
    global _settings_window
    if _settings_window is not None and _settings_window.isVisible():
        _settings_window.raise_()
        _settings_window.activateWindow()
        return
    _settings_window = SettingsWindow()
    _settings_window.saved.connect(_on_settings_saved)
    _settings_window.show()
    _settings_window.raise_()
    _settings_window.activateWindow()


def _bind_hotkey():
    global _hotkey_handle
    if _hotkey_handle is not None:
        try:
            keyboard.remove_hotkey(_hotkey_handle)
        except Exception:
            pass
    _hotkey_handle = keyboard.add_hotkey(config.HOTKEY, lambda: signals.take.emit())


def _on_settings_saved():
    _bind_hotkey()
    _rebuild_menu()
    tray.setToolTip(_tooltip_text())
    tray.showMessage(
        "设置已保存",
        f"热键: {config.HOTKEY.upper()}  目标: {config.TARGET_WIDTH}×{config.TARGET_HEIGHT}",
        QSystemTrayIcon.MessageIcon.Information,
        1500,
    )


def _tooltip_text():
    adapter = dsr.get_adapter_name().split()[0]
    mode = dsr.find_mode(config.TARGET_WIDTH, config.TARGET_HEIGHT)
    status = f"{config.TARGET_WIDTH}×{config.TARGET_HEIGHT} 可用" if mode else "插值降级"
    return f"超分截图  [{config.HOTKEY.upper()}]  {adapter} - {status}"


def _rebuild_menu():
    menu = QMenu()
    menu.addAction(f"截图  ({config.HOTKEY.upper()})", signals.take.emit)
    menu.addSeparator()
    menu.addAction("设置…", open_settings)
    menu.addSeparator()
    menu.addAction("退出", QApplication.instance().quit)
    tray.setContextMenu(menu)


def main():
    global tray
    if not _acquire_single_instance():
        print("已有实例在运行，退出。")
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")   # 用扁平风格替代系统默认，避免按钮残留原生纹理
    app.setQuitOnLastWindowClosed(False)

    signals.take.connect(open_overlay)
    signals.captured.connect(on_capture_done)
    _bind_hotkey()

    icon_path = _resource_path("icon.ico")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
    else:
        px = QPixmap(32, 32); px.fill(QColor(0, 174, 255))
        app_icon = QIcon(px)
    app.setWindowIcon(app_icon)
    tray = QSystemTrayIcon(app_icon, app)
    _rebuild_menu()
    tray.setToolTip(_tooltip_text())
    tray.activated.connect(
        lambda reason: open_settings()
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None
    )
    tray.show()

    vendor = dsr.detect_vendor()
    tray.showMessage(
        "超分截图已启动",
        f"显卡: {vendor}  |  热键: {config.HOTKEY.upper()}  |  双击托盘打开设置",
        QSystemTrayIcon.MessageIcon.Information,
        3000,
    )

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
