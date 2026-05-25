# SuperShot · 超分截图

利用 **NVIDIA DSR** 和 **AMD VSR** 在截图瞬间临时切换显示分辨率，
直接抓取显卡原生超分帧缓冲区，得到**真正高于显示器物理分辨率**的截图。

不是插值放大，是显卡真实渲染的超分数据。

## ✨ 特性

- 🎯 **真原生超分** — DSR/VSR 切换到 4K（或更高）后再截图，所得即所见的"超清版"
- 🧊 **截图期间冻结屏幕** — 用户感知不到分辨率切换过程的视觉变化
- 🔁 **窗口位置自动还原** — 切换前后保存/恢复窗口位置，截完桌面不会乱
- ⚡ **失败自动降级** — 显卡不支持时回退到 LANCZOS 插值放大，永不失败
- 🪟 **Win11 风格设置界面** — 横向布局，分页导航，圆角，蓝色高亮
- ⌨️ **快捷键所见即所得录入** — 按一下，组合键自动捕获
- 📋 **自动复制 / 自动保存** — 截完即用
- 🚀 **常驻托盘** — 不占任务栏

## 📷 截图

| 设置界面 | 截图选区 |
|----------|----------|
| 横向布局 / 侧边栏导航 / 实色浅灰 | 半透明遮罩 + 蓝色选框 + 尺寸标注 |

## 🖥️ 环境要求

- Windows 10 1809+ / Windows 11
- 显卡支持 DSR（NVIDIA）或 VSR（AMD）—— 否则走插值降级
- **不需要 Python**（使用打包版 `SuperShot.exe`）

### 开启显卡超分

| 显卡 | 操作 |
|------|------|
| NVIDIA | 控制面板 → 管理 3D 设置 → **DSR - 因数** → 勾选 4.00x |
| AMD | Adrenalin → Display → **Virtual Super Resolution** → 启用 |
| Intel 集显 | 不支持，请配合 NVIDIA/AMD 独显使用 |

## 🚀 使用

### 下载即用

到 [Releases](../../releases) 下载最新 `SuperShot.exe`，双击运行即可。

### 快捷键

| 操作 | 默认 |
|------|------|
| 截图 | `Alt + Shift + S` |
| 取消选区 | `Esc` |

可在 **托盘 → 设置… → 热键** 里录入新组合键（点一下，按你想要的键）。

### 设置项

- **目标分辨率** — 截图时临时切换到的分辨率（如 3840×2160）
- **插值倍数** — 超分不可用时的降级放大倍数
- **保存路径** — 默认桌面 `Screenshots/` 子目录
- **自动保存 / 自动复制** — 截完同时写文件 + 进剪贴板

## 🛠️ 从源码构建

```bash
git clone https://github.com/<your-name>/supershot.git
cd supershot
pip install -r requirements.txt
python main.py            # 直接运行
```

### 打包成 exe

```bash
build.bat                 # 一键生成 dist/SuperShot.exe
```

或手动：

```bash
python make_icon.py       # 生成图标
pyinstaller SuperShot.spec --clean --noconfirm
```

## 📂 项目结构

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

## 🧠 实现原理

```
┌──────────────────────────────────────────────────────────┐
│ 用户按 Alt+Shift+S                                       │
│   ↓                                                       │
│ 半透明遮罩展开 → 选区                                     │
│   ↓                                                       │
│ 抓取 1080p 帧 → 全屏 FreezeOverlay（对截图工具隐形）     │
│   ↓                                                       │
│ EnumWindows 保存所有窗口位置                              │
│   ↓                                                       │
│ ChangeDisplaySettingsW(3840×2160)  ← DSR/VSR 切到 4K     │
│   ↓                                                       │
│ mss 抓取 4K 缓冲区中的选区（坐标 ×2）                     │
│   ↓                                                       │
│ ChangeDisplaySettingsW(NULL)       ← 还原到 1080p        │
│   ↓                                                       │
│ SetWindowPlacement × 4 次抢救窗口位置                     │
│   ↓                                                       │
│ FreezeOverlay 关闭，托盘提示"原生 4K 截图完成"            │
└──────────────────────────────────────────────────────────┘
```

关键点：
- `WDA_EXCLUDEFROMCAPTURE` 让冻结层对自身截图不可见
- `Per-Monitor DPI Aware` 避免坐标在切换瞬间被自动缩放
- 多次连续 `SetWindowPlacement` 与 Windows 的窗口重排"赛跑"

## 📝 License

MIT
