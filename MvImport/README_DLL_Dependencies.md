# 海康威视相机SDK DLL依赖说明

## 在新电脑上运行时的系统要求

如果您将此项目复制到另一台电脑并遇到DLL加载错误，请确保安装以下运行时库：

### 1. Visual C++ Redistributable (必须安装)

海康威视SDK的DLL文件需要Microsoft Visual C++运行时库支持。

**下载并安装以下版本：**

- **Visual C++ Redistributable 2013 (VC12)** - 主要需求
  - 64位: https://aka.ms/highdpimfc2013x64enu
  - 32位: https://aka.ms/highdpimfc2013x86enu

- **Visual C++ Redistributable 2015-2022** - 推荐安装最新版
  - 64位: https://aka.ms/vs/17/release/vc_redist.x64.exe
  - 32位: https://aka.ms/vs/17/release/vc_redist.x86.exe

### 2. 检查Python架构

确保您的Python版本与DLL文件架构匹配：

```python
import sys
print('64位' if sys.maxsize > 2**32 else '32位')
```

- 64位Python需要使用 `Win64_x64` 目录下的DLL
- 32位Python需要使用 `Win32_i86` 目录下的DLL

### 3. 文件结构

确保以下目录结构完整：

```
MvImport/
├── Win64_x64/              # 64位DLL文件（56个文件）
│   ├── MvCameraControl.dll
│   ├── MVGigEVisionSDK.dll
│   ├── MvUsb3vTL.dll
│   └── ... (其他依赖DLL)
├── Win32_i86/              # 32位DLL文件
│   └── ... (32位依赖DLL)
└── MvCameraControl_class.py
```

### 4. 常见错误及解决方案

#### 错误: `FileNotFoundError: Could not find module '...\MvCameraControl.dll' (or one of its dependencies)`

**可能原因：**
1. 缺少Visual C++ Redistributable运行时库
2. DLL文件架构与Python不匹配（32位/64位）
3. 某些依赖DLL文件缺失

**解决方法：**
1. 安装上述Visual C++ Redistributable
2. 确认Python架构与DLL架构匹配
3. 确保Win64_x64或Win32_i86目录下的所有DLL文件都已复制

#### 错误: `0x8000000C` (MV_E_LOAD_LIBRARY)

这是DLL加载失败的错误码，通常是因为：
- 缺少系统运行时库（安装VC++ Redistributable）
- DLL依赖项缺失（确保所有56个DLL都在）

### 5. 验证安装

运行以下命令检查是否能正确加载：

```python
from MvImport.MvCameraControl_class import *
print("DLL loaded successfully!")
```

如果没有报错，说明DLL加载成功。

### 6. 离线部署建议

如果需要在无网络环境部署：

1. **下载离线安装包**
   - 下载上述VC++ Redistributable安装包
   - 将安装包与项目一起打包

2. **包含所有DLL**
   - 确保Win64_x64和Win32_i86目录完整
   - 不要只复制MvCameraControl.dll，必须包含所有依赖

3. **提供安装脚本**
   - 创建批处理文件自动安装VC++运行时库

## 技术支持

如果遇到其他问题，请检查：
- Windows事件查看器中的应用程序日志
- 使用Dependency Walker工具检查DLL依赖关系
- 确认相机驱动是否正确安装
