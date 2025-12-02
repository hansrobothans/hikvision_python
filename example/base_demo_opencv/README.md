# OpenCV Demo - 使用OpenCV显示相机图像

这个示例展示了如何使用OpenCV的cv2.imshow()来显示海康威视相机采集的图像，非常适合需要进行图像处理和计算机视觉应用的场景。

## 主要特点

### 1. 使用OpenCV显示
- 使用 `cv2.imshow()` 显示图像
- 使用 `cv2.namedWindow()` 创建可调整大小的窗口
- 图像格式转换为BGR（OpenCV标准格式）
- 支持全屏和窗口调整

### 2. 命令行界面
- 纯命令行交互，无GUI框架依赖
- 简单直观的键盘控制
- 实时显示帧信息（帧号、分辨率）

### 3. 图像处理支持
- 使用NumPy数组存储图像数据
- 方便进行各种OpenCV图像处理操作
- 在图像上添加文本信息演示

### 4. 键盘快捷键
- `s` - 保存当前图像为BMP格式
- `p` - 打印当前相机参数
- `q` 或 `ESC` - 退出程序

## 与其他示例的区别

| 特性 | base_demo_pyside6 | qimage_demo_pyside6 | opencv_demo |
|------|-------------------|---------------------|-------------|
| 界面框架 | PySide6 | PySide6 | 无（纯OpenCV） |
| 显示方式 | MV_CC_DisplayOneFrame | QImage + QPixmap | cv2.imshow |
| 图像格式 | 原始格式 | RGB8 | BGR8 |
| 图像数据 | ctypes buffer | QImage | NumPy array |
| 适用场景 | GUI应用 | GUI应用 | 图像处理/CV |
| 依赖库 | PySide6 | PySide6 | OpenCV + NumPy |
| 控制方式 | 按钮 | 按钮 | 键盘快捷键 |

## 文件说明

- `BasicDemo.py` - 主程序，命令行交互界面
- `CamOperation_class.py` - 相机操作类，包含OpenCV显示功能

## 运行要求

- Python 3.x
- OpenCV (opencv-python)
- NumPy
- 海康威视MVS SDK

### 安装依赖

```bash
pip install opencv-python numpy
```

## 使用方法

```bash
cd example/opencv_demo
python BasicDemo.py
```

### 运行流程

1. 程序自动枚举所有相机设备
2. 选择要使用的相机（如果只有一个相机会自动选择）
3. 打开相机并开始采集
4. OpenCV窗口显示实时图像
5. 使用键盘快捷键控制

### 交互示例

```
============================================================
OpenCV Camera Demo - Hikvision MVS SDK
============================================================
Find 1 devices!

[0] USB Device:
    User Defined Name: MV-CA016-10UC
    Model Name: MV-CA016-10UC
    Serial Number: 00J12345678

Auto select device [0]

Opening device...
open device successfully!

Camera Parameters:
  Exposure Time: 10000.00
  Gain: 0.00
  Frame Rate: 30.00

Starting grabbing...
start grabbing successfully!

============================================================
Camera is running. OpenCV window opened.
============================================================

Controls:
  's' - Save current image
  'p' - Print parameters
  'q' or ESC - Quit
============================================================
```

## 主要优势

### 1. 快速开发原型
- 最少的依赖和代码
- 无需设计GUI界面
- 专注于图像处理算法

### 2. 方便的图像处理
- 直接使用NumPy数组操作
- 丰富的OpenCV图像处理函数
- 易于集成其他CV算法

### 3. 轻量级
- 不需要Qt等重型GUI框架
- 启动快速
- 内存占用小

### 4. 教学和调试友好
- 简单清晰的代码结构
- 容易理解和修改
- 适合学习和实验

## 代码示例

### 在图像上添加处理效果

在 `CamOperation_class.py` 的 `Work_thread()` 函数中，转换为NumPy数组后可以添加各种处理：

```python
# 转换后的image是NumPy数组
image = image_array.reshape((self.st_frame_info.nHeight, self.st_frame_info.nWidth, 3))

# 示例1: 添加文本
cv2.putText(image, "Frame: %d" % self.st_frame_info.nFrameNum,
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

# 示例2: 绘制矩形
cv2.rectangle(image, (100, 100), (200, 200), (0, 0, 255), 2)

# 示例3: 高斯模糊
# image_blurred = cv2.GaussianBlur(image, (5, 5), 0)

# 示例4: 边缘检测
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# edges = cv2.Canny(gray, 100, 200)

# 示例5: 颜色空间转换
# hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
```

## 注意事项

1. **窗口焦点**：必须确保OpenCV窗口处于焦点状态才能接收键盘输入
2. **cv2.waitKey()**：必须在主循环中调用才能刷新显示和接收键盘事件
3. **线程安全**：图像采集在子线程中，显示在主线程中
4. **BGR格式**：OpenCV使用BGR而非RGB，注意颜色通道顺序

## 适用场景

- 图像处理算法开发和测试
- 计算机视觉应用原型
- 机器学习数据采集
- 质量检测应用
- 目标识别和跟踪
- 简单的相机监控
- 教学和演示

## 扩展建议

1. **添加更多快捷键**：如调整曝光、增益等参数
2. **录制视频**：使用cv2.VideoWriter保存视频
3. **实时图像处理**：集成各种CV算法
4. **多相机支持**：同时显示多个相机的图像
5. **性能监控**：显示FPS和处理时间
