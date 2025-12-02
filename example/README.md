# 海康威视相机示例程序

本目录包含多个海康威视MVS SDK的Python示例程序，展示了不同的图像显示和处理方式。

## 🚀 推荐：HikCamera 封装类（OpenCV 风格）

**新增**：我们提供了一个参考 OpenCV 接口设计的 `HikCamera` 封装类，让海康工业相机的使用变得和普通摄像头一样简单！

### 快速示例

```python
import cv2
from HikCamera import HikCamera

# 枚举相机（可选）
camera_list = HikCamera.enumerate_devices()
print(f"找到 {len(camera_list)} 个相机")

# 打开第一个相机 - 就像使用 cv2.VideoCapture(0) 一样！
cam = HikCamera(0)

if not cam.isOpened():
    print("无法打开相机")
    exit()

while True:
    # 读取图像 - API 完全兼容 OpenCV
    ret, frame = cam.read()

    if ret:
        cv2.imshow('Hikvision Camera', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
```

### 主要特点

- ✅ **OpenCV 兼容接口**：`read()`, `isOpened()`, `release()`, `get()`, `set()`
- ✅ **零学习成本**：如果会用 `cv2.VideoCapture`，就会用 `HikCamera`
- ✅ **自动资源管理**：自动处理相机初始化和资源释放
- ✅ **多相机支持**：通过索引轻松访问多个相机
- ✅ **线程安全**：内部自动处理多线程同步

### 运行 Demo

```bash
# 运行海康相机 demo
python example/hikvision_camera_demo.py

# 或运行普通摄像头 demo（对比）
python example/opencv_camera_demo.py
```

---

## 示例目录

### 1. [base_demo_pyside6](base_demo_pyside6/)
**基础PySide6示例 - 使用海康SDK原生显示**

- 使用PySide6创建GUI界面
- 使用 `MV_CC_DisplayOneFrame()` 直接显示图像
- 固定窗口布局
- Windows平台优化

**适合场景**：
- 需要快速显示相机图像的Windows应用
- 对显示性能要求高的应用
- 不需要对图像进行处理的监控应用

### 2. [qimage_demo_pyside6](qimage_demo_pyside6/)
**QImage显示示例 - 使用PySide6 QLabel显示**

- 使用PySide6创建响应式GUI界面
- 使用 `QImage` + `QPixmap` 显示图像
- 响应式布局，支持窗口调整和全屏
- 图像自动缩放保持纵横比

**适合场景**：
- 需要响应式界面的GUI应用
- 需要在图像上叠加UI元素的应用
- 需要跨平台兼容的应用
- 需要对图像进行Qt处理的应用

### 3. [opencv_demo](opencv_demo/)
**OpenCV显示示例 - 命令行 + OpenCV显示**

- 纯命令行界面，无GUI框架
- 使用 `cv2.imshow()` 显示图像
- NumPy数组格式，方便图像处理
- 键盘快捷键控制

**适合场景**：
- 图像处理算法开发和测试
- 计算机视觉应用原型
- 机器学习数据采集
- 不需要复杂GUI的应用

## 快速对比

| 特性 | base_demo_pyside6 | qimage_demo_pyside6 | opencv_demo |
|------|-------------------|---------------------|-------------|
| **界面类型** | PySide6 GUI | PySide6 GUI | 命令行 + OpenCV窗口 |
| **显示方式** | MV_CC_DisplayOneFrame | QImage + QPixmap | cv2.imshow |
| **图像格式** | 原始格式 | RGB8 | BGR8 |
| **数据结构** | ctypes buffer | QImage | NumPy array |
| **布局方式** | 固定位置 | 响应式布局 | OpenCV窗口 |
| **全屏支持** | ❌ | ✅ | ✅ |
| **图像缩放** | ❌ | ✅ | ✅ |
| **跨平台** | Windows优先 | ✅ | ✅ |
| **图像处理** | ❌ | Qt处理 | OpenCV处理 |
| **性能** | 最高 | 中等 | 中等 |
| **GUI复杂度** | 中等 | 中等 | 最简单 |

## 依赖要求

### 共同依赖
- Python 3.x
- 海康威视MVS SDK

### 各示例特定依赖

```bash
# base_demo_pyside6 和 qimage_demo_pyside6
pip install PySide6

# opencv_demo
pip install opencv-python numpy
```

## 快速开始

### 1. 基础PySide6示例
```bash
cd base_demo_pyside6
python BasicDemo.py
```

### 2. QImage显示示例
```bash
cd qimage_demo_pyside6
python BasicDemo.py
```

### 3. OpenCV示例
```bash
cd opencv_demo
python BasicDemo.py
```

## 选择指南

### 选择 base_demo_pyside6 如果：
- ✅ 只在Windows上运行
- ✅ 需要最佳显示性能
- ✅ 不需要图像处理
- ✅ 不需要调整窗口大小

### 选择 qimage_demo_pyside6 如果：
- ✅ 需要现代化的响应式界面
- ✅ 需要全屏显示支持
- ✅ 需要跨平台兼容
- ✅ 需要在图像上叠加UI元素
- ✅ 需要对图像进行Qt处理

### 选择 opencv_demo 如果：
- ✅ 需要进行图像处理
- ✅ 开发计算机视觉应用
- ✅ 不需要复杂的GUI
- ✅ 希望代码简单直接
- ✅ 需要快速原型开发

## 项目结构

```
example/
├── README.md                          # 本文件
├── base_demo_pyside6/                 # 基础PySide6示例
│   ├── BasicDemo.py                   # 主程序
│   ├── CamOperation_class.py          # 相机操作类
│   ├── PyUICBasicDemo.py              # UI代码
│   └── PyUICBasicDemo.ui              # UI设计文件
├── qimage_demo_pyside6/               # QImage显示示例
│   ├── BasicDemo.py                   # 主程序
│   ├── CamOperation_class.py          # 相机操作类（带QImage支持）
│   ├── PyUICBasicDemo.py              # UI代码
│   ├── PyUICBasicDemo.ui              # UI设计文件
│   └── README.md                      # 详细说明
└── opencv_demo/                       # OpenCV显示示例
    ├── BasicDemo.py                   # 主程序
    ├── CamOperation_class.py          # 相机操作类（带OpenCV支持）
    └── README.md                      # 详细说明
```

## 共同功能

所有示例都支持：
- ✅ 枚举和选择相机设备
- ✅ 打开/关闭相机
- ✅ 开始/停止采集
- ✅ 连续模式和触发模式
- ✅ 软触发
- ✅ 获取和设置相机参数（曝光、增益、帧率）
- ✅ 保存图像为BMP格式

## 常见问题

### 1. 导入模块失败
确保已将项目根目录添加到Python路径，所有示例都包含了路径配置代码。

### 2. 找不到相机
- 检查相机是否正确连接
- 检查MVS SDK是否正确安装
- 运行SDK自带的MVS Client验证相机

### 3. 显示窗口没有响应
- **base_demo_pyside6**: 确保使用了正确的QWidget winId
- **qimage_demo_pyside6**: 检查信号槽连接是否正确
- **opencv_demo**: 确保调用了cv2.waitKey()

### 4. 图像格式转换失败
不同示例使用不同的目标格式：
- **qimage_demo_pyside6**: RGB8
- **opencv_demo**: BGR8

## 技术支持

- 海康威视MVS SDK文档
- Python SDK示例代码
- 项目GitHub Issues

## 许可证

请遵守海康威视MVS SDK的许可协议。
