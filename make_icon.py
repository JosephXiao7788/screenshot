"""把 Downloads/Gemini_Generated_Image_oos35soos35soos3.png 处理成 icon.ico / icon.png。

源图是 2816×1536 的展示图，主图标在画面正中心。
策略：从中心裁正方形（约 35% 宽度）只取主图标，再做圆角，导出多尺寸 ICO。
"""
import os
from PIL import Image, ImageDraw

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.expanduser("~"), "Downloads",
                   "Gemini_Generated_Image_oos35soos35soos3.png")


def center_crop_square(img: Image.Image, ratio: float) -> Image.Image:
    """从图像中心裁出边长 = min(w,h)*ratio 的正方形。"""
    w, h = img.size
    side = int(min(w, h) * ratio)
    left = (w - side) // 2
    top  = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def main():
    if not os.path.exists(SRC):
        raise FileNotFoundError(f"找不到源图: {SRC}")

    src = Image.open(SRC).convert("RGBA")
    # 中心 38% 区域刚好框住主图标
    icon = center_crop_square(src, 0.38)

    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = [icon.resize((s, s), Image.LANCZOS) for s in sizes]

    png_path = os.path.join(OUT_DIR, "icon.png")
    ico_path = os.path.join(OUT_DIR, "icon.ico")
    images[-1].save(png_path, "PNG")
    images[0].save(ico_path, format="ICO",
                   sizes=[(s, s) for s in sizes],
                   append_images=images[1:])
    print(f"生成: {png_path}")
    print(f"生成: {ico_path}")


if __name__ == "__main__":
    main()
