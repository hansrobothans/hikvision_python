# HikCV 基础演示说明

本目录包含 HikCV (海康工业相机 OpenCV 兼容封装) 的演示程序。

## 文件说明

### 1. simple_demo.py - 简单示例
最基础的使用示例，适合快速入门。

**功能：**
- 打开相机
- 设置参数（曝光、增益）
- 采集并显示图像
- 释放资源

**运行：**
```bash
python simple_demo.py
```

### 2. full_demo.py - 完整功能演示
展示 VideoCapture 的所有功能。

**功能：**
- 演示 1: 枚举设备
- 演示 2: 基本使用
- 演示 3: 属性控制
- 演示 4: Grab/Retrieve 模式
- 演示 5: 上下文管理器
- 演示 6: 异常模式

**运行：**
```bash
python full_demo.py
```

### 3. compare_opencv.py - 对比演示
对比 HikCV 和 OpenCV 的使用方式，展示两者的完全兼容性。

**功能：**
- 显示代码对比
- 可选择使用 HikCV 或 OpenCV
- 使用相同的代码运行不同的后端

**运行：**
```bash
python compare_opencv.py
```

## 快速开始

### 最简单的例子

```python
from HikCV import VideoCapture

# 打开相机（就像 cv2.VideoCapture 一样）
cap = VideoCapture(0)

# 读取图像
ret, frame = cap.read()

# 释放资源
cap.release()
```

### 完整示例

```python
from HikCV import VideoCapture, CAP_PROP_EXPOSURE, CAP_PROP_GAIN
import cv2

# 打开相机
cap = VideoCapture(0)

if not cap.isOpened():
    print("无法打开相机")
    exit()

# 设置参数
cap.set(CAP_PROP_EXPOSURE, 15000)
cap.set(CAP_PROP_GAIN, 10)

# 采集图像
while True:
    ret, frame = cap.read()
    if ret:
        cv2.imshow('Camera', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
```

## 支持的功能

### 初始化方式
```python
# 方式 1: 直接初始化
cap = VideoCapture(0)

# 方式 2: 空初始化后打开
cap = VideoCapture()
cap.open(0)

# 方式 3: 上下文管理器
with VideoCapture(0) as cap:
    ret, frame = cap.read()
```

### 图像采集
```python
# 方式 1: read() - 直接读取
ret, frame = cap.read()

# 方式 2: grab() + retrieve() - 分步采集
if cap.grab():
    ret, frame = cap.retrieve()
```

### 属性控制
```python
# 获取属性
width = cap.get(CAP_PROP_FRAME_WIDTH)
height = cap.get(CAP_PROP_FRAME_HEIGHT)
fps = cap.get(CAP_PROP_FPS)

# 设置属性
cap.set(CAP_PROP_EXPOSURE, 15000)
cap.set(CAP_PROP_GAIN, 10)
```

### 支持的属性常量

- `CAP_PROP_FRAME_WIDTH` - 图像宽度
- `CAP_PROP_FRAME_HEIGHT` - 图像高度
- `CAP_PROP_FPS` - 帧率
- `CAP_PROP_EXPOSURE` - 曝光时间
- `CAP_PROP_GAIN` - 增益
- `CAP_PROP_BRIGHTNESS` - 亮度
- `CAP_PROP_GAMMA` - Gamma值
- `CAP_PROP_AUTO_EXPOSURE` - 自动曝光
- `CAP_PROP_AUTO_WB` - 自动白平衡
- `CAP_PROP_TRIGGER` - 触发模式
- 更多...

## 与 OpenCV 的区别

**唯一的区别：导入语句**

OpenCV:
```python
from cv2 import VideoCapture, CAP_PROP_EXPOSURE
```

HikCV:
```python
from HikCV import VideoCapture, CAP_PROP_EXPOSURE
```

**其他代码完全相同！**

## 常见问题

**Q: 需要安装 OpenCV 吗？**
A: 只有在需要显示图像时才需要 OpenCV 的 `cv2.imshow()`。核心功能不需要。

**Q: 可以同时使用多个相机吗？**
A: 可以，使用不同的索引：
```python
cap1 = VideoCapture(0)
cap2 = VideoCapture(1)
```

**Q: 如何枚举所有相机？**
A: 使用 `enumerate_devices()` 函数：
```python
from HikCV import enumerate_devices
devices = enumerate_devices()
```

**Q: 性能如何？**
A: 与直接使用 SDK 性能完全相同，没有额外开销。

## 更多信息

- 参考 `HikCV.py` 源代码了解完整实现
- 参考 `HikCamera.py` 了解底层封装
- 查看 OpenCV 文档了解 `VideoCapture` 的标准用法

## 支持

如有问题，请参考：
1. 示例代码
2. 源代码注释
3. OpenCV 官方文档
