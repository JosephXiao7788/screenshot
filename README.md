# SuperShot

> Native super-resolution screenshot tool powered by **NVIDIA DSR** and **AMD VSR**.
> 基于 **NVIDIA DSR** 与 **AMD VSR** 的原生超分辨率截图工具。

<p align="center">
  <img src="icon.png" width="128" alt="SuperShot icon">
</p>

---

## 🇺🇸 English

SuperShot momentarily switches your display to a higher resolution (e.g. 4K via DSR/VSR) at the instant of capture, grabs the native super-resolved frame buffer, then switches back — all hidden behind a screen freeze overlay so you don't see the disruption.

**Not interpolation. Real GPU-rendered super-resolution data.**

### ✨ Features

- 🎯 **True native super-resolution** — switches to 4K (or higher) via DSR/VSR, captures, restores
- 🧊 **Screen freeze during capture** — user sees nothing of the resolution switch
- 🔁 **Window position restored** — saves/restores all window layouts around the switch
- ⚡ **Automatic fallback** — falls back to LANCZOS interpolation if super-res unavailable
- 🪟 **Windows 11 style settings** — landscape layout, sidebar nav, rounded corners
- ⌨️ **Click-and-press hotkey recorder** — just press your combo to bind it
- 📋 **Auto-copy / Auto-save** — instantly available after capture
- 🚀 **Lives in the tray** — no taskbar clutter

### 🖥️ Requirements

- Windows 10 1809+ or Windows 11
- GPU supporting DSR (NVIDIA) or VSR (AMD) — otherwise falls back to interpolation
- **Python not required** when using the packaged `SuperShot.exe`

### Enable GPU super-resolution first

| GPU | How |
|------|------|
| NVIDIA | Control Panel → Manage 3D Settings → **DSR - Factors** → check 4.00x |
| AMD | Adrenalin → Display → **Virtual Super Resolution** → enable |
| Intel iGPU | Not supported, pair with NVIDIA/AMD discrete GPU |

### 🚀 Usage

#### Download

Grab the latest `SuperShot.exe` from the [Releases](../../releases) page and double-click to run.

#### Hotkeys

| Action | Default |
|------|------|
| Capture | `Alt + Shift + S` |
| Cancel selection | `Esc` |

Change the hotkey in **Tray → Settings → Hotkey** (click and press the combo you want).

#### Settings

- **Target resolution** — temp resolution during capture (e.g. 3840×2160)
- **Interpolation factor** — fallback magnification when super-res unavailable
- **Save directory** — defaults to `Desktop/Screenshots/`
- **Auto-save / Auto-copy** — file + clipboard simultaneously

### 🛠️ Build from source

```bash
git clone https://github.com/<your-name>/SuperShot.git
cd SuperShot
pip install -r requirements.txt
python main.py                  # run directly
```

#### Package into exe

```bash
build.bat                       # one-click → dist/SuperShot.exe
```

Or manually:

```bash
python make_icon.py             # generate icon
pyinstaller SuperShot.spec --clean --noconfirm
```

### 🧠 How it works

```
User presses Alt+Shift+S
  ↓
Translucent overlay → select region
  ↓
Capture 1080p snapshot → full-screen FreezeOverlay (invisible to capture API)
  ↓
EnumWindows saves all window positions
  ↓
ChangeDisplaySettingsW(3840×2160)   ← DSR/VSR switches to 4K
  ↓
mss captures region from 4K buffer (coordinates ×2)
  ↓
ChangeDisplaySettingsW(NULL)        ← restore to 1080p
  ↓
SetWindowPlacement × 4 to rescue window positions
  ↓
FreezeOverlay closes, tray notifies "Native 4K capture complete"
```

Key tricks:
- `WDA_EXCLUDEFROMCAPTURE` makes the freeze overlay invisible to its own capture API
- `Per-Monitor DPI Aware` prevents coords from being auto-scaled during switch
- Multiple consecutive `SetWindowPlacement` calls race Windows' own window rearrangement

### 📂 Project structure

```
.
├─ main.py              # entry, single-instance lock, tray, hotkey binding
├─ overlay.py           # selection mask + freeze overlay
├─ capture.py           # screenshot, save, clipboard
├─ dsr.py               # resolution switch, native capture, window save/restore
├─ settings.py          # PyQt6 settings window (Win11 style)
├─ config.py            # config load/save (config.json)
├─ make_icon.py         # icon generator
├─ SuperShot.spec       # PyInstaller config
├─ build.bat            # one-click packaging
└─ requirements.txt
```

### 📝 License

MIT

---

## 🇨🇳 中文

SuperShot 在你按下截图热键的瞬间，临时把显示器切换到更高分辨率（例如通过 DSR/VSR 切到 4K），抓取显卡渲染出的原生超分帧缓冲区，再切回原分辨率——整个过程被冻结层遮挡，用户无感知。

**不是插值放大，而是显卡真实渲染的超分数据。**

### ✨ 特性

- 🎯 **真原生超分** — DSR/VSR 切到 4K（或更高）后截图，得到的是显卡渲染的"超清版"
- 🧊 **截图期间冻结屏幕** — 用户感知不到分辨率切换的视觉变化
- 🔁 **窗口位置自动还原** — 切换前后保存/恢复窗口位置，截完桌面不会乱
- ⚡ **失败自动降级** — 显卡不支持时回退到 LANCZOS 插值，永不失败
- 🪟 **Win11 风格设置界面** — 横向布局，侧边栏导航，圆角设计
- ⌨️ **点按录入热键** — 一键，按下组合键自动捕获
- 📋 **自动复制 / 自动保存** — 截完即用
- 🚀 **常驻托盘** — 不占任务栏

### 🖥️ 环境要求

- Windows 10 1809+ 或 Windows 11
- 显卡支持 DSR（NVIDIA）或 VSR（AMD）—— 否则走插值降级
- **不需要 Python**（使用打包好的 `SuperShot.exe`）

### 开启显卡超分

| 显卡 | 操作 |
|------|------|
| NVIDIA | 控制面板 → 管理 3D 设置 → **DSR - 因数** → 勾选 4.00x |
| AMD | Adrenalin → Display → **Virtual Super Resolution** → 启用 |
| Intel 集显 | 不支持，请配合 NVIDIA/AMD 独显使用 |

### 🚀 使用

#### 下载即用

到 [Releases](../../releases) 下载最新 `SuperShot.exe`，双击运行即可。

#### 快捷键

| 操作 | 默认 |
|------|------|
| 截图 | `Alt + Shift + S` |
| 取消选区 | `Esc` |

可在 **托盘 → 设置 → 热键** 里录入新组合键（点一下，按你想要的键）。

#### 设置项

- **目标分辨率** — 截图时临时切换到的分辨率（如 3840×2160）
- **插值倍数** — 超分不可用时的降级放大倍数
- **保存路径** — 默认桌面 `Screenshots/` 子目录
- **自动保存 / 自动复制** — 截完同时写文件 + 进剪贴板

### 🛠️ 从源码构建

```bash
git clone https://github.com/<你的用户名>/SuperShot.git
cd SuperShot
pip install -r requirements.txt
python main.py                  # 直接运行
```

#### 打包成 exe

```bash
build.bat                       # 一键生成 dist/SuperShot.exe
```

或手动：

```bash
python make_icon.py             # 生成图标
pyinstaller SuperShot.spec --clean --noconfirm
```

### 🧠 实现原理

```
用户按 Alt+Shift+S
  ↓
半透明遮罩展开 → 选区
  ↓
抓取 1080p 帧 → 全屏 FreezeOverlay（对截图工具隐形）
  ↓
EnumWindows 保存所有窗口位置
  ↓
ChangeDisplaySettingsW(3840×2160)   ← DSR/VSR 切到 4K
  ↓
mss 抓取 4K 缓冲区中的选区（坐标 ×2）
  ↓
ChangeDisplaySettingsW(NULL)        ← 还原到 1080p
  ↓
SetWindowPlacement × 4 次抢救窗口位置
  ↓
FreezeOverlay 关闭，托盘提示"原生 4K 截图完成"
```

关键点：
- `WDA_EXCLUDEFROMCAPTURE` 让冻结层对自身截图不可见
- `Per-Monitor DPI Aware` 避免坐标在切换瞬间被自动缩放
- 多次连续 `SetWindowPlacement` 与 Windows 的窗口重排"赛跑"

### 📂 项目结构

```
.
├─ main.py              # 入口，单实例锁，托盘，热键绑定
├─ overlay.py           # 选区遮罩 + 冻结层
├─ capture.py           # 截图、保存、剪贴板
├─ dsr.py               # 分辨率切换、原生超分截取、窗口位置保存/恢复
├─ settings.py          # PyQt6 设置窗口（Win11 风格）
├─ config.py            # 配置加载 / 保存（config.json）
├─ make_icon.py         # 图标生成脚本
├─ SuperShot.spec       # PyInstaller 配置
├─ build.bat            # 一键打包脚本
└─ requirements.txt
```

### 📝 License

MIT
