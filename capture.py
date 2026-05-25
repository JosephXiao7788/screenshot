import mss
import mss.tools
from PIL import Image
import io
import config


def capture_and_scale(x1, y1, x2, y2):
    import dsr

    # 优先走 DSR/VSR 原生 4K 路径
    img = dsr.capture_region(x1, y1, x2, y2)
    if img is not None:
        return img, True

    # 降级：LANCZOS 插值放大
    left = min(x1, x2)
    top = min(y1, y2)
    right = max(x1, x2)
    bottom = max(y1, y2)

    with mss.mss() as sct:
        region = {"left": left, "top": top, "width": right - left, "height": bottom - top}
        raw = sct.grab(region)
        img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")

    w, h = img.size
    img = img.resize((w * config.SCALE, h * config.SCALE), Image.LANCZOS)
    return img, False


def image_to_clipboard(img):
    import win32clipboard
    output = io.BytesIO()
    img.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]  # 去掉 BMP 文件头
    output.close()
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()


def save_image(img):
    import os
    from datetime import datetime
    if config.SAVE_DIR:
        save_dir = config.SAVE_DIR
    else:
        save_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Screenshots")
    os.makedirs(save_dir, exist_ok=True)
    filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
    path = os.path.join(save_dir, filename)
    img.save(path, "PNG")
    return path
