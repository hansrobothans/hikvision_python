# HikCamera 使用说明

## 概述

`HikCamera` 是一个参考 OpenCV 接口设计的海康工业相机封装类，提供简单易用的 API。

## 已解决的问题

### 问题：大量"无法读取帧"错误

**原因**：
- 相机初始化需要时间
- 图像采集线程刚启动时还没有获取到第一帧
- `read()` 方法直接返回 None，导致错误提示

**解决方案**：
1. 在 `read()` 方法中添加等待逻辑，最多等待3秒直到第一帧到达
2. 在采集线程中添加详细的调试信息
3. 在demo程序中添加初始化等待时间

## 基本使用

### 1. 枚举相机

```python
from HikCamera import HikCamera

# 枚举所有相机
camera_list = HikCamera.enumerate_devices()
print(f"找到 {len(camera_list)} 个相机")

for cam_info in camera_list:
    print(f"  [{cam_info['index']}] {cam_info['model']} - {cam_info['serial']}")
```

### 2. 打开相机并读取图像

```python
import cv2
from HikCamera import HikCamera
import time

# 打开第一个相机
cam = HikCamera(0)

if not cam.isOpened():
    print("无法打开相机")
    exit()

# 重要：等待相机初始化（可选但推荐）
time.sleep(0.5)

while True:
    # 读取一帧（类似 OpenCV）
    ret, frame = cam.read()

    if ret:
        cv2.imshow('Hikvision Camera', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
```

## API 参考

### 类方法

#### `HikCamera.enumerate_devices()`
枚举所有可用的海康相机。

**返回**：
- `list`: 相机信息列表，每个元素包含 `{'index': int, 'model': str, 'serial': str, 'type': str}`

### 实例方法

#### `__init__(index=0)`
创建相机对象并自动打开指定索引的相机。

**参数**：
- `index`: 相机索引，从0开始

#### `isOpened()`
检查相机是否已打开。

**返回**：
- `bool`: 相机是否已打开

#### `read()`
读取一帧图像（类似 OpenCV 的 `cap.read()`）。

**返回**：
- `tuple`: `(ret, frame)`
  - `ret`: `bool`，是否成功读取
  - `frame`: `numpy.ndarray`，BGR格式的图像，如果失败则为None

**注意**：
- 首次调用会等待第一帧到达（最多3秒）
- 如果相机未打开或未启动采集，返回 `(False, None)`

#### `release()`
释放相机资源。

**重要**：程序结束前必须调用此方法释放资源！

#### `get(propId)`
获取相机属性。

**参数**：
- `propId`: 属性ID
  - `3` (`CAP_PROP_FRAME_WIDTH`): 图像宽度
  - `4` (`CAP_PROP_FRAME_HEIGHT`): 图像高度
  - `5` (`CAP_PROP_FPS`): 帧率
  - `15` (`CAP_PROP_EXPOSURE`): 曝光时间（微秒）
  - `17` (`CAP_PROP_GAIN`): 增益（dB）

**返回**：
- `float`: 属性值

#### `set(propId, value)`
设置相机属性。

**参数**：
- `propId`: 属性ID（同 `get()`）
- `value`: 属性值

**返回**：
- `bool`: 是否设置成功

## 使用示例

### 示例1：基本使用

```python
import cv2
from HikCamera import HikCamera

# 打开相机
cam = HikCamera(0)

if not cam.isOpened():
    print("无法打开相机")
    exit()

while True:
    ret, frame = cam.read()
    if ret:
        cv2.imshow('Camera', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
```

### 示例2：设置相机参数

```python
from HikCamera import HikCamera, CAP_PROP_EXPOSURE, CAP_PROP_GAIN

cam = HikCamera(0)

# 获取当前参数
print(f"曝光时间: {cam.get(CAP_PROP_EXPOSURE)} us")
print(f"增益: {cam.get(CAP_PROP_GAIN)} dB")

# 设置参数
cam.set(CAP_PROP_EXPOSURE, 10000)  # 设置曝光时间为10000微秒
cam.set(CAP_PROP_GAIN, 5)          # 设置增益为5dB

# ... 读取图像 ...

cam.release()
```

### 示例3：多相机

```python
import cv2
from HikCamera import HikCamera

# 枚举相机
cameras = HikCamera.enumerate_devices()
print(f"找到 {len(cameras)} 个相机")

# 打开多个相机
cam1 = HikCamera(0)
cam2 = HikCamera(1)

while True:
    ret1, frame1 = cam1.read()
    ret2, frame2 = cam2.read()

    if ret1:
        cv2.imshow('Camera 1', frame1)
    if ret2:
        cv2.imshow('Camera 2', frame2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam1.release()
cam2.release()
cv2.destroyAllWindows()
```

## 最佳实践

### 1. 初始化等待
相机打开后，建议等待一小段时间让相机完全初始化：

```python
cam = HikCamera(0)
time.sleep(0.5)  # 等待500ms
```

### 2. 错误处理
始终检查 `read()` 的返回值：

```python
ret, frame = cam.read()
if ret:
    # 处理图像
    cv2.imshow('Camera', frame)
else:
    # 处理错误
    print("无法读取图像")
```

### 3. 资源释放
使用 `try-finally` 确保资源被释放：

```python
cam = HikCamera(0)
try:
    while True:
        ret, frame = cam.read()
        # ... 处理图像 ...
finally:
    cam.release()
```

### 4. 参数设置时机
在开始采集前设置参数效果最好：

```python
cam = HikCamera(0)
cam.set(CAP_PROP_EXPOSURE, 10000)  # 在读取前设置
time.sleep(0.1)  # 给相机时间应用设置

while True:
    ret, frame = cam.read()
    # ...
```

## 调试信息

`HikCamera` 会输出以下调试信息：

- `"枚举设备失败! ret[0x...]"` - 无法枚举相机
- `"没有找到相机设备!"` - 未找到任何相机
- `"成功打开相机 [X]"` - 相机打开成功
- `"开始图像采集"` - 开始采集图像
- `"成功获取第一帧图像: WxH"` - 首帧获取成功
- `"获取图像缓冲失败! ret[0x...]"` - 图像获取失败（最多显示5次）
- `"像素格式转换失败! ret[0x...]"` - 格式转换失败

## 常见问题

### Q: 为什么开始时有很多"获取图像缓冲失败"错误？
A: 这是正常的。相机启动需要时间，在完全初始化前可能获取不到图像。通常1-2秒后会正常。

### Q: 如何减少启动错误信息？
A: 在相机打开后添加延时：
```python
cam = HikCamera(0)
time.sleep(0.5)
```

### Q: read() 一直返回 False 怎么办？
A: 检查以下几点：
1. 相机是否正确连接
2. 是否有权限访问相机
3. 相机是否被其他程序占用
4. 查看控制台的详细错误信息

### Q: 如何保存图像？
A: 使用 OpenCV 的 `imwrite`：
```python
ret, frame = cam.read()
if ret:
    cv2.imwrite('image.jpg', frame)
```

## 与 OpenCV VideoCapture 的对比

| 功能 | OpenCV VideoCapture | HikCamera |
|------|---------------------|-----------|
| 打开设备 | `cv2.VideoCapture(0)` | `HikCamera(0)` |
| 读取图像 | `cap.read()` | `cam.read()` |
| 检查打开 | `cap.isOpened()` | `cam.isOpened()` |
| 释放资源 | `cap.release()` | `cam.release()` |
| 获取属性 | `cap.get(id)` | `cam.get(id)` |
| 设置属性 | `cap.set(id, val)` | `cam.set(id, val)` |
| 枚举设备 | ❌ | `HikCamera.enumerate_devices()` ✅ |

## 技术细节

- **线程模型**：后台线程持续采集图像，主线程通过 `read()` 获取最新帧
- **图像格式**：自动转换为 BGR8 格式的 NumPy 数组
- **线程安全**：使用锁保护共享资源
- **内存管理**：自动管理图像缓冲区

## 运行示例程序

```bash
# 运行海康相机 demo
python example/hikvision_camera_demo.py

# 运行普通摄像头 demo（对比）
python example/opencv_camera_demo.py
```
