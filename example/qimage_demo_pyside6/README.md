# QImage Demo - PySide6图像显示示例

这个示例展示了如何使用PySide6的QLabel控件来显示海康威视相机采集的图像，而不是使用海康SDK的MV_DISPLAY_FRAME_INFO接口。

## 主要特点

### 1. 使用QImage和QPixmap显示图像
- 不使用 `MV_CC_DisplayOneFrame()` 接口
- 使用 `QLabel` 控件配合 `QImage` 和 `QPixmap` 显示图像
- 支持图像自动缩放以适应显示区域，保持纵横比

### 2. 基于信号槽机制
- `CameraOperation` 类继承自 `QObject`
- 使用 `image_signal` 信号发送图像数据
- 主窗口通过槽函数 `display_image()` 接收并显示图像
- 线程安全的图像更新机制

### 3. 图像格式转换
- 使用 `MV_CC_ConvertPixelType()` 将相机原始格式转换为RGB8
- 创建QImage对象，格式为 `QImage.Format_RGB888`
- 复制图像数据避免内存问题

### 4. 响应式布局设计
- 使用Qt布局管理器（QHBoxLayout、QVBoxLayout）替代固定几何位置
- 窗口大小调整时，图像显示区域自动调整
- 支持全屏显示，图像自动缩放填充可用空间
- 右侧控制面板固定宽度（220px），保持UI整洁

## 与base_demo_pyside6的区别

| 特性 | base_demo_pyside6 | qimage_demo_pyside6 |
|------|-------------------|---------------------|
| 显示控件 | QWidget | QLabel |
| 显示方式 | MV_CC_DisplayOneFrame | QImage + QPixmap |
| 图像转换 | 无需转换 | RGB转换 |
| 缩放支持 | 无 | 自动缩放保持比例 |
| 布局方式 | 固定几何位置 | 响应式布局管理器 |
| 全屏支持 | 不支持自适应 | 完美支持全屏缩放 |
| 跨平台 | Windows only | 更好的跨平台支持 |

## 文件说明

- `BasicDemo.py` - 主程序，包含UI逻辑和相机控制
- `CamOperation_class.py` - 相机操作类，包含图像采集和QImage转换
- `PyUICBasicDemo.ui` - Qt Designer UI文件
- `PyUICBasicDemo.py` - 由UI文件生成的Python代码

## 运行要求

- Python 3.x
- PySide6
- 海康威视MVS SDK

## 使用方法

```bash
cd example/qimage_demo_pyside6
python BasicDemo.py
```

## 主要改进点

1. **更好的图像显示控制**
   - 可以方便地进行图像缩放、旋转等处理
   - 支持图像保持纵横比缩放
   - 更容易添加图像处理功能

2. **更好的跨平台兼容性**
   - QImage/QPixmap是Qt的跨平台图像处理方案
   - 不依赖Windows特定的显示接口

3. **更灵活的界面设计**
   - QLabel可以更灵活地布局
   - 支持样式表自定义外观
   - 可以方便地添加图像叠加层（如十字线、ROI框等）

## 注意事项

1. 图像转换会增加一定的CPU开销
2. 高帧率应用可能需要优化转换和显示逻辑
3. 大分辨率图像显示时需要注意内存使用

## 适用场景

- 需要对显示图像进行二次处理的应用
- 需要在图像上叠加UI元素的应用
- 需要跨平台兼容的应用
- 需要灵活控制图像显示效果的应用
