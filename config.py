import json
import os

# 默认值
HOTKEY        = "alt+shift+s"
SCALE         = 2
SAVE_DIR      = None
AUTO_COPY     = True
AUTO_SAVE     = True
TARGET_WIDTH  = 3840   # DSR/VSR 截图时切换到的目标宽
TARGET_HEIGHT = 2160   # DSR/VSR 截图时切换到的目标高

_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
_KEYS = ["HOTKEY", "SCALE", "SAVE_DIR", "AUTO_COPY", "AUTO_SAVE",
         "TARGET_WIDTH", "TARGET_HEIGHT"]


def load():
    if not os.path.exists(_CONFIG_FILE):
        return
    try:
        with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k in _KEYS:
            if k in data:
                globals()[k] = data[k]
    except Exception:
        pass


def save():
    data = {k: globals()[k] for k in _KEYS}
    with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
