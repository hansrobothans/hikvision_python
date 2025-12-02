#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
环境检查脚本 - 用于检查海康威视相机SDK运行环境
在新电脑上运行此脚本以诊断DLL加载问题
"""

import sys
import os
import platform
import ctypes
from pathlib import Path

def check_python_arch():
    """检查Python架构"""
    print("=" * 60)
    print("1. Python架构检查")
    print("=" * 60)
    is_64bit = sys.maxsize > 2**32
    arch = "64位" if is_64bit else "32位"
    print(f"✓ Python版本: {sys.version}")
    print(f"✓ Python架构: {arch}")
    print(f"✓ 平台: {platform.system()} {platform.release()}")
    return is_64bit

def check_dll_directory(is_64bit):
    """检查DLL目录是否存在"""
    print("\n" + "=" * 60)
    print("2. DLL目录检查")
    print("=" * 60)

    script_dir = Path(__file__).parent
    mvimport_dir = script_dir / "MvImport"

    if is_64bit:
        dll_dir = mvimport_dir / "Win64_x64"
        dll_name = "Win64_x64"
    else:
        dll_dir = mvimport_dir / "Win32_i86"
        dll_name = "Win32_i86"

    if dll_dir.exists():
        print(f"✓ DLL目录存在: {dll_dir}")
        dll_files = list(dll_dir.glob("*.dll"))
        print(f"✓ 找到 {len(dll_files)} 个DLL文件")

        # 检查关键DLL文件
        key_dlls = ["MvCameraControl.dll", "MVGigEVisionSDK.dll", "MvUsb3vTL.dll"]
        for dll in key_dlls:
            dll_path = dll_dir / dll
            if dll_path.exists():
                print(f"  ✓ {dll}")
            else:
                print(f"  ✗ 缺失: {dll}")
        return dll_dir
    else:
        print(f"✗ DLL目录不存在: {dll_dir}")
        print(f"  请确保 MvImport/{dll_name}/ 目录已复制到此位置")
        return None

def check_vc_runtime():
    """检查Visual C++ Runtime"""
    print("\n" + "=" * 60)
    print("3. Visual C++ Runtime检查")
    print("=" * 60)

    # 尝试加载常见的VC运行时DLL
    vc_dlls = {
        "msvcr120.dll": "Visual C++ 2013 Runtime",
        "msvcp120.dll": "Visual C++ 2013 Runtime",
        "vcruntime140.dll": "Visual C++ 2015-2022 Runtime",
    }

    for dll_name, description in vc_dlls.items():
        try:
            # 尝试从系统路径加载
            ctypes.WinDLL(dll_name)
            print(f"✓ {description} ({dll_name})")
        except Exception:
            print(f"✗ 缺失: {description} ({dll_name})")

def check_dll_dependencies(dll_dir):
    """尝试加载主DLL"""
    print("\n" + "=" * 60)
    print("4. DLL加载测试")
    print("=" * 60)

    if not dll_dir:
        print("✗ 无法测试 - DLL目录不存在")
        return False

    main_dll = dll_dir / "MvCameraControl.dll"

    try:
        # 添加DLL目录到搜索路径
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(str(dll_dir))

        # 添加到PATH
        os.environ['PATH'] = str(dll_dir) + os.pathsep + os.environ.get('PATH', '')

        # 尝试加载DLL
        print(f"正在尝试加载: {main_dll}")
        dll = ctypes.WinDLL(str(main_dll))
        print("✓ MvCameraControl.dll 加载成功！")
        return True

    except Exception as e:
        print(f"✗ DLL加载失败")
        print(f"错误信息: {e}")
        print("\n可能的原因:")
        print("1. 缺少 Visual C++ Redistributable 2013")
        print("2. 缺少某些依赖DLL文件")
        print("3. DLL架构与Python不匹配")
        return False

def check_sdk_import():
    """尝试导入SDK模块"""
    print("\n" + "=" * 60)
    print("5. SDK模块导入测试")
    print("=" * 60)

    try:
        from MvImport.MvCameraControl_class import MvCamera
        print("✓ MvCameraControl_class 导入成功")

        try:
            ret = MvCamera.MV_CC_Initialize()
            print(f"✓ SDK初始化成功 (返回值: {ret})")
            return True
        except Exception as e:
            print(f"✗ SDK初始化失败: {e}")
            return False

    except Exception as e:
        print(f"✗ 模块导入失败: {e}")
        return False

def print_summary(checks):
    """打印检查总结"""
    print("\n" + "=" * 60)
    print("检查总结")
    print("=" * 60)

    all_passed = all(checks.values())

    if all_passed:
        print("✓ 所有检查通过！环境配置正确。")
    else:
        print("✗ 发现问题，请根据上述检查结果进行修复：\n")

        if not checks.get('dll_dir'):
            print("1. 请确保将完整的 MvImport 目录复制到项目中")

        if not checks.get('dll_load'):
            print("2. 请安装 Visual C++ Redistributable:")
            print("   - Visual C++ 2013: https://aka.ms/highdpimfc2013x64enu")
            print("   - Visual C++ 2015-2022: https://aka.ms/vs/17/release/vc_redist.x64.exe")

        if not checks.get('sdk_import'):
            print("3. 请检查Python环境和模块导入路径")

def main():
    """主函数"""
    print("\n海康威视相机SDK环境检查工具")
    print("Version 1.0\n")

    checks = {}

    # 1. 检查Python架构
    is_64bit = check_python_arch()

    # 2. 检查DLL目录
    dll_dir = check_dll_directory(is_64bit)
    checks['dll_dir'] = dll_dir is not None

    # 3. 检查VC运行时
    check_vc_runtime()

    # 4. 检查DLL加载
    checks['dll_load'] = check_dll_dependencies(dll_dir)

    # 5. 检查SDK导入
    checks['sdk_import'] = check_sdk_import()

    # 打印总结
    print_summary(checks)

    print("\n按Enter键退出...")
    input()

if __name__ == "__main__":
    main()
