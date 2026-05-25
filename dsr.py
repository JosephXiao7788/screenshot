import ctypes
from ctypes import wintypes
import time
import mss
from PIL import Image

ENUM_CURRENT_SETTINGS  = -1
CDS_FULLSCREEN         = 0x00000004
DISP_CHANGE_SUCCESSFUL = 0
DM_BITSPERPEL  = 0x00040000
DM_PELSWIDTH   = 0x00080000
DM_PELSHEIGHT  = 0x00100000
DM_DISPLAYFREQ = 0x00400000

SWP_NOZORDER   = 0x0004
SWP_NOACTIVATE = 0x0010
SW_SHOWNORMAL    = 1
SW_SHOWMINIMIZED = 2
SW_SHOWMAXIMIZED = 3


class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName",         ctypes.c_wchar * 32),
        ("dmSpecVersion",        ctypes.c_ushort),
        ("dmDriverVersion",      ctypes.c_ushort),
        ("dmSize",               ctypes.c_ushort),
        ("dmDriverExtra",        ctypes.c_ushort),
        ("dmFields",             ctypes.c_ulong),
        ("dmPositionX",          ctypes.c_long),
        ("dmPositionY",          ctypes.c_long),
        ("dmDisplayOrientation", ctypes.c_ulong),
        ("dmDisplayFixedOutput", ctypes.c_ulong),
        ("dmColor",              ctypes.c_short),
        ("dmDuplex",             ctypes.c_short),
        ("dmYResolution",        ctypes.c_short),
        ("dmTTOption",           ctypes.c_short),
        ("dmCollate",            ctypes.c_short),
        ("dmFormName",           ctypes.c_wchar * 32),
        ("dmLogPixels",          ctypes.c_ushort),
        ("dmBitsPerPel",         ctypes.c_ulong),
        ("dmPelsWidth",          ctypes.c_ulong),
        ("dmPelsHeight",         ctypes.c_ulong),
        ("dmDisplayFlags",       ctypes.c_ulong),
        ("dmDisplayFrequency",   ctypes.c_ulong),
        ("dmICMMethod",          ctypes.c_ulong),
        ("dmICMIntent",          ctypes.c_ulong),
        ("dmMediaType",          ctypes.c_ulong),
        ("dmDitherType",         ctypes.c_ulong),
        ("dmReserved1",          ctypes.c_ulong),
        ("dmReserved2",          ctypes.c_ulong),
        ("dmPanningWidth",       ctypes.c_ulong),
        ("dmPanningHeight",      ctypes.c_ulong),
    ]


class DISPLAY_DEVICE(ctypes.Structure):
    _fields_ = [
        ("cb",           ctypes.c_ulong),
        ("DeviceName",   ctypes.c_wchar * 32),
        ("DeviceString", ctypes.c_wchar * 128),
        ("StateFlags",   ctypes.c_ulong),
        ("DeviceID",     ctypes.c_wchar * 128),
        ("DeviceKey",    ctypes.c_wchar * 128),
    ]


class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [
        ("length",            ctypes.c_uint),
        ("flags",             ctypes.c_uint),
        ("showCmd",           ctypes.c_uint),
        ("ptMinPosition",     wintypes.POINT),
        ("ptMaxPosition",     wintypes.POINT),
        ("rcNormalPosition",  wintypes.RECT),
    ]


user32 = ctypes.windll.user32


def get_adapter_name():
    dd = DISPLAY_DEVICE()
    dd.cb = ctypes.sizeof(DISPLAY_DEVICE)
    user32.EnumDisplayDevicesW(None, 0, ctypes.byref(dd), 0)
    return dd.DeviceString


def _current():
    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)
    user32.EnumDisplaySettingsW(None, ENUM_CURRENT_SETTINGS, ctypes.byref(dm))
    return dm


def find_4k_mode():
    return find_mode(3840, 2160)


def find_mode(width, height):
    """找到指定分辨率的最高刷新率模式。"""
    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)
    best = None
    i = 0
    while user32.EnumDisplaySettingsW(None, i, ctypes.byref(dm)):
        if dm.dmPelsWidth == width and dm.dmPelsHeight == height:
            if best is None or dm.dmDisplayFrequency > best.dmDisplayFrequency:
                best = DEVMODE()
                ctypes.memmove(ctypes.byref(best), ctypes.byref(dm), ctypes.sizeof(DEVMODE))
        i += 1
    return best


def list_resolutions():
    """返回所有可用分辨率 (width, height)，去重，按从小到大排序。"""
    seen = set()
    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)
    i = 0
    while user32.EnumDisplaySettingsW(None, i, ctypes.byref(dm)):
        seen.add((dm.dmPelsWidth, dm.dmPelsHeight))
        i += 1
    return sorted(seen, key=lambda x: (x[0], x[1]))


def detect_vendor():
    """根据显卡名识别厂商。返回 'NVIDIA' / 'AMD' / 'Intel' / 'Other'。"""
    name = get_adapter_name().upper()
    if "NVIDIA" in name or "GEFORCE" in name or "RTX" in name or "GTX" in name:
        return "NVIDIA"
    if "AMD" in name or "RADEON" in name or "RYZEN" in name:
        return "AMD"
    if "INTEL" in name:
        return "Intel"
    return "Other"


def _apply(mode):
    mode.dmFields = DM_PELSWIDTH | DM_PELSHEIGHT | DM_DISPLAYFREQ | DM_BITSPERPEL
    return user32.ChangeDisplaySettingsW(ctypes.byref(mode), CDS_FULLSCREEN)


def _restore():
    user32.ChangeDisplaySettingsW(None, 0)


# 保存 (hwnd, left, top, width, height, show_cmd)
def _save_windows():
    saved = []
    EnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

    def callback(hwnd, lparam):
        # 跳过不可见和无标题窗口
        if not user32.IsWindowVisible(hwnd):
            return True
        if user32.GetWindowTextLengthW(hwnd) == 0:
            return True
        # 跳过最小化窗口（最小化后不受分辨率影响）
        if user32.IsIconic(hwnd):
            return True

        placement = WINDOWPLACEMENT()
        placement.length = ctypes.sizeof(WINDOWPLACEMENT)
        if not user32.GetWindowPlacement(hwnd, ctypes.byref(placement)):
            return True

        rect = placement.rcNormalPosition
        saved.append((
            hwnd,
            rect.left, rect.top,
            rect.right - rect.left, rect.bottom - rect.top,
            placement.showCmd,
        ))
        return True

    user32.EnumWindows(EnumProc(callback), 0)
    return saved


def _restore_windows(saved):
    for hwnd, l, t, w, h, show_cmd in saved:
        if not user32.IsWindow(hwnd):
            continue
        # 先重置位置和大小
        placement = WINDOWPLACEMENT()
        placement.length = ctypes.sizeof(WINDOWPLACEMENT)
        placement.showCmd = show_cmd
        placement.rcNormalPosition.left = l
        placement.rcNormalPosition.top = t
        placement.rcNormalPosition.right = l + w
        placement.rcNormalPosition.bottom = t + h
        user32.SetWindowPlacement(hwnd, ctypes.byref(placement))
        # 再用 MoveWindow 二次确认（双保险）
        if show_cmd == SW_SHOWNORMAL:
            user32.MoveWindow(hwnd, l, t, w, h, True)


def capture_region(x1, y1, x2, y2):
    """
    切换到 config 配置的目标分辨率，截取对应区域，再切回。
    切换前保存所有窗口位置，切回后恢复。
    成功返回 PIL.Image，失败返回 None。
    调用方负责事先冻结屏幕。
    """
    import config
    mode = find_mode(config.TARGET_WIDTH, config.TARGET_HEIGHT)
    if mode is None:
        return None

    cur = _current()
    scale_x = mode.dmPelsWidth  / cur.dmPelsWidth
    scale_y = mode.dmPelsHeight / cur.dmPelsHeight

    # 保存所有可见窗口的位置
    saved_windows = _save_windows()

    if _apply(mode) != DISP_CHANGE_SUCCESSFUL:
        return None

    # 等显示器硬件同步，4K 桌面渲染完成
    time.sleep(0.5)

    img = None
    try:
        left   = int(min(x1, x2) * scale_x)
        top    = int(min(y1, y2) * scale_y)
        right  = int(max(x1, x2) * scale_x)
        bottom = int(max(y1, y2) * scale_y)

        with mss.mss() as sct:
            mon = sct.monitors[1]
            left   = max(left,   mon["left"])
            top    = max(top,    mon["top"])
            right  = min(right,  mon["left"] + mon["width"])
            bottom = min(bottom, mon["top"]  + mon["height"])

            region = {"left": left, "top": top,
                      "width": right - left, "height": bottom - top}
            raw = sct.grab(region)
            img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
    finally:
        _restore()
        # 短暂等显示器同步，然后立刻开始连续抢救窗口位置
        time.sleep(0.4)
        # 连续 4 次还原，与 Windows 自己的窗口重排抢时间
        for _ in range(4):
            _restore_windows(saved_windows)
            time.sleep(0.15)

    return img
