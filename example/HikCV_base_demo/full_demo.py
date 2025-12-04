# -*- coding: utf-8 -*-
"""
HikCV 完整功能演示
展示 VideoCapture 类的所有功能
"""
import cv2
import sys
import os

# 添加父目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
parent_parent_dir = os.path.dirname(parent_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if parent_parent_dir not in sys.path:
    sys.path.insert(0, parent_parent_dir)

# 导入 HikCamera 模块
import HikCv

def demo_enumerate():
    """演示：枚举设备"""
    print("\n" + "=" * 60)
    print("演示 1: 枚举设备")
    print("=" * 60)

    devices = HikCv.enumerate_devices()
    if len(devices) == 0:
        print("没有找到相机设备")
        return False

    print(f"找到 {len(devices)} 个设备:")
    for dev in devices:
        print(f"  [{dev['index']}] {dev['type']}: {dev['model']}")
        print(f"      序列号: {dev['serial']}")
        if 'ip' in dev:
            print(f"      IP地址: {dev['ip']}")

    return True


def demo_basic_usage():
    """演示：基本使用"""
    print("\n" + "=" * 60)
    print("演示 2: 基本使用")
    print("=" * 60)

    # 创建相机对象
    cap = HikCv.VideoCapture(0)

    if not cap.isOpened():
        print("错误: 无法打开相机")
        return

    print(f"✓ 成功打开相机")
    print(f"  后端名称: {cap.getBackendName()}")
    print(f"  分辨率: {int(cap.get(HikCv.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(HikCv.CAP_PROP_FRAME_HEIGHT))}")
    print(f"  帧率: {cap.get(HikCv.CAP_PROP_FPS):.2f} fps")

    # 采集图像
    print("\n采集 30 帧图像...")
    for i in range(30):
        ret, frame = cap.read()
        if ret:
            print(f"\r  进度: {i+1}/30", end="")
            cv2.imshow('Basic Usage', frame)
            cv2.waitKey(30)

    print("\n✓ 完成")
    cap.release()
    cv2.destroyAllWindows()


def demo_property_control():
    """演示：属性控制"""
    print("\n" + "=" * 60)
    print("演示 3: 属性控制")
    print("=" * 60)

    cap = HikCv.VideoCapture(0)
    if not cap.isOpened():
        print("错误: 无法打开相机")
        return

    # 读取当前属性
    print("\n当前属性:")
    print(f"  曝光: {cap.get(HikCv.CAP_PROP_EXPOSURE):.2f} us")
    print(f"  增益: {cap.get(HikCv.CAP_PROP_GAIN):.2f} dB")

    # 修改属性
    print("\n修改属性:")
    if cap.set(HikCv.CAP_PROP_EXPOSURE, 20000):
        print(f"  ✓ 曝光设置为: {cap.get(HikCv.CAP_PROP_EXPOSURE):.2f} us")

    if cap.set(HikCv.CAP_PROP_GAIN, 12):
        print(f"  ✓ 增益设置为: {cap.get(HikCv.CAP_PROP_GAIN):.2f} dB")

    # 采集图像验证
    print("\n采集 20 帧验证...")
    for i in range(20):
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Property Control', frame)
            cv2.waitKey(30)

    print("✓ 完成")
    cap.release()
    cv2.destroyAllWindows()


def demo_grab_retrieve():
    """演示：Grab/Retrieve 模式"""
    print("\n" + "=" * 60)
    print("演示 4: Grab/Retrieve 模式")
    print("=" * 60)

    cap = HikCv.VideoCapture(0)
    if not cap.isOpened():
        print("错误: 无法打开相机")
        return

    print("\n使用 grab() + retrieve() 采集 30 帧...")
    frame_count = 0

    for i in range(30):
        # 第一步：抓取
        if cap.grab():
            # 第二步：解码
            ret, frame = cap.retrieve()
            if ret:
                frame_count += 1
                print(f"\r  进度: {frame_count}/30", end="")

                cv2.putText(frame, f"Grab/Retrieve: {frame_count}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                cv2.imshow('Grab/Retrieve', frame)
                cv2.waitKey(30)

    print(f"\n✓ 成功采集 {frame_count} 帧")
    cap.release()
    cv2.destroyAllWindows()


def demo_context_manager():
    """演示：上下文管理器"""
    print("\n" + "=" * 60)
    print("演示 5: 上下文管理器 (with 语句)")
    print("=" * 60)

    print("\n使用 with 语句...")
    with HikCv.VideoCapture(0) as cap:
        if not cap.isOpened():
            print("错误: 无法打开相机")
            return

        print("✓ 成功打开相机")

        # 采集 20 帧
        for i in range(20):
            ret, frame = cap.read()
            if ret:
                print(f"\r  采集: {i+1}/20", end="")
                cv2.imshow('Context Manager', frame)
                cv2.waitKey(30)

        print("\n✓ 采集完成")

    # with 块结束后自动释放资源
    print("✓ 资源已自动释放")
    cv2.destroyAllWindows()


def demo_exception_mode():
    """演示：异常模式"""
    print("\n" + "=" * 60)
    print("演示 6: 异常模式")
    print("=" * 60)

    cap = HikCv.VideoCapture(0)
    if not cap.isOpened():
        print("错误: 无法打开相机")
        return

    print("\n默认模式（返回错误码）:")
    result = cap.set(999, 100)  # 设置一个不存在的属性
    print(f"  set() 返回: {result}")

    print("\n异常模式（抛出异常）:")
    cap.setExceptionMode(True)
    print(f"  异常模式状态: {cap.getExceptionMode()}")

    print("\n注意: 在异常模式下，错误会抛出异常而不是返回 False")

    cap.release()


def main():
    print("=" * 60)
    print("HikCV 完整功能演示")
    print("=" * 60)

    # 枚举设备
    if not demo_enumerate():
        return

    # 询问用户
    print("\n请选择要运行的演示:")
    print("  1 - 演示 1: 枚举设备")
    print("  2 - 演示 2: 基本使用")
    print("  3 - 演示 3: 属性控制")
    print("  4 - 演示 4: Grab/Retrieve 模式")
    print("  5 - 演示 5: 上下文管理器")
    print("  6 - 演示 6: 异常模式")
    print("  7 - 运行所有演示")

    choice = input("\n请输入选项 (1-7): ").strip()

    if choice == '1':
        demo_enumerate()
    elif choice == '2':
        demo_basic_usage()
    elif choice == '3':
        demo_property_control()
    elif choice == '4':
        demo_grab_retrieve()
    elif choice == '5':
        demo_context_manager()
    elif choice == '6':
        demo_exception_mode()
    elif choice == '7':
        demo_basic_usage()
        demo_property_control()
        demo_grab_retrieve()
        demo_context_manager()
        demo_exception_mode()
    else:
        print("无效的选项")

    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
