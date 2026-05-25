import ctypes
import ctypes.wintypes

ENUM_CURRENT_SETTINGS = -1
ENUM_REGISTRY_SETTINGS = -2

class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName",      ctypes.c_wchar * 32),
        ("dmSpecVersion",     ctypes.c_ushort),
        ("dmDriverVersion",   ctypes.c_ushort),
        ("dmSize",            ctypes.c_ushort),
        ("dmDriverExtra",     ctypes.c_ushort),
        ("dmFields",          ctypes.c_ulong),
        ("dmPositionX",       ctypes.c_long),
        ("dmPositionY",       ctypes.c_long),
        ("dmDisplayOrientation", ctypes.c_ulong),
        ("dmDisplayFixedOutput", ctypes.c_ulong),
        ("dmColor",           ctypes.c_short),
        ("dmDuplex",          ctypes.c_short),
        ("dmYResolution",     ctypes.c_short),
        ("dmTTOption",        ctypes.c_short),
        ("dmCollate",         ctypes.c_short),
        ("dmFormName",        ctypes.c_wchar * 32),
        ("dmLogPixels",       ctypes.c_ushort),
        ("dmBitsPerPel",      ctypes.c_ulong),
        ("dmPelsWidth",       ctypes.c_ulong),
        ("dmPelsHeight",      ctypes.c_ulong),
        ("dmDisplayFlags",    ctypes.c_ulong),
        ("dmDisplayFrequency", ctypes.c_ulong),
        ("dmICMMethod",       ctypes.c_ulong),
        ("dmICMIntent",       ctypes.c_ulong),
        ("dmMediaType",       ctypes.c_ulong),
        ("dmDitherType",      ctypes.c_ulong),
        ("dmReserved1",       ctypes.c_ulong),
        ("dmReserved2",       ctypes.c_ulong),
        ("dmPanningWidth",    ctypes.c_ulong),
        ("dmPanningHeight",   ctypes.c_ulong),
    ]

def list_resolutions():
    modes = set()
    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)
    i = 0
    while ctypes.windll.user32.EnumDisplaySettingsW(None, i, ctypes.byref(dm)):
        modes.add((dm.dmPelsWidth, dm.dmPelsHeight, dm.dmDisplayFrequency))
        i += 1
    return sorted(modes, key=lambda x: (x[0], x[1], x[2]))

def get_current():
    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)
    ctypes.windll.user32.EnumDisplaySettingsW(None, ENUM_CURRENT_SETTINGS, ctypes.byref(dm))
    return dm.dmPelsWidth, dm.dmPelsHeight, dm.dmDisplayFrequency

current = get_current()
print(f"当前分辨率: {current[0]}×{current[1]} @ {current[2]}Hz\n")

modes = list_resolutions()
print("所有可用分辨率：")
high_res = []
for w, h, hz in modes:
    tag = ""
    if w >= 2560:
        tag = "  ← 高分辨率"
        high_res.append((w, h, hz))
    print(f"  {w}×{h} @ {hz}Hz{tag}")

print()
candidates = [(w, h, hz) for w, h, hz in high_res if w >= 3840]
if candidates:
    print("✅ 发现 DSR 4K 可用：")
    for w, h, hz in candidates:
        print(f"   {w}×{h} @ {hz}Hz")
else:
    print("❌ 没有找到 4K 分辨率。请先在 NVIDIA 控制面板开启 DSR：")
    print("   管理 3D 设置 → DSR - 比例 → 勾选 4.00x (3840×2160)")
