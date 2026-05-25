import ctypes
import mss
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QImage


class FreezeOverlay(QWidget):
    """截取当前屏幕内容并全屏展示，在分辨率切换期间遮挡视觉变化。"""

    def __init__(self):
        super().__init__()
        with mss.mss() as sct:
            mon = sct.monitors[1]
            raw = sct.grab(mon)
            self._qimg = QImage(
                bytes(raw.rgb), raw.width, raw.height,
                raw.width * 3, QImage.Format.Format_RGB888
            )
            self._native_w = raw.width
            self._native_h = raw.height

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.BypassWindowManagerHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        # 一开始就用超过 4K 的尺寸，分辨率怎么变都能覆盖
        self.setGeometry(0, 0, 4096, 2304)
        self.show()
        self.raise_()
        self._exclude_from_capture()
        self._force_topmost()

        QApplication.primaryScreen().geometryChanged.connect(self._on_screen_changed)

    def _exclude_from_capture(self):
        WDA_EXCLUDEFROMCAPTURE = 0x00000011
        hwnd = int(self.winId())
        ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)

    def _force_topmost(self):
        HWND_TOPMOST = -1
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_SHOWWINDOW = 0x0040
        hwnd = int(self.winId())
        ctypes.windll.user32.SetWindowPos(
            hwnd, HWND_TOPMOST, 0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
        )

    def _on_screen_changed(self, geo):
        # 分辨率变化后重新置顶并放大覆盖
        self.setGeometry(0, 0, max(geo.width(), 4096), max(geo.height(), 2304))
        self._force_topmost()
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        # 用原始尺寸绘制，多余区域留黑（不影响视觉感受，反正盖住的部分就是黑）
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        painter.drawImage(0, 0, self._qimg)

    def closeEvent(self, e):
        try:
            QApplication.primaryScreen().geometryChanged.disconnect(self._on_screen_changed)
        except Exception:
            pass
        super().closeEvent(e)


class Overlay(QWidget):
    def __init__(self, on_done):
        super().__init__()
        self.on_done = on_done
        self.start = QPoint()
        self.end = QPoint()
        self.selecting = False

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setWindowOpacity(1.0)
        self.showFullScreen()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.start = e.pos()
            self.end = e.pos()
            self.selecting = True

    def mouseMoveEvent(self, e):
        if self.selecting:
            self.end = e.pos()
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self.selecting:
            self.selecting = False
            rect = QRect(self.start, self.end).normalized()
            self.hide()
            if rect.width() > 5 and rect.height() > 5:
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(80, lambda: self.on_done(
                    rect.left(), rect.top(), rect.right(), rect.bottom()
                ))
            self.close()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.close()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))

        if self.selecting and self.start != self.end:
            rect = QRect(self.start, self.end).normalized()

            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, QColor(0, 0, 0, 0))
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

            pen = QPen(QColor(0, 174, 255), 2)
            painter.setPen(pen)
            painter.drawRect(rect)

            label = f"{rect.width()} x {rect.height()}  ->  {rect.width() * 2} x {rect.height() * 2} (4K)"
            font = QFont("Arial", 10)
            painter.setFont(font)
            painter.setPen(QColor(255, 255, 255))
            tx = rect.left() + 4
            ty = rect.top() - 6 if rect.top() > 20 else rect.bottom() + 16
            painter.drawText(tx, ty, label)
