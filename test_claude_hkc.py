"""测试 claude_hkc.py 的各种模式"""

from claude_hkc import HikCameraCapture
import cv2
import time

def test_sync_mode():
    """测试同步模式"""
    print("=" * 60)
    print("测试同步模式")
    print("=" * 60)

    cap = HikCameraCapture(0, async_mode=False)

    if cap.isOpened():
        print("同步模式: 开始采集...")
        for i in range(5):
            ret, frame = cap.read()
            if ret:
                print(f"  第 {i+1} 帧成功, shape: {frame.shape}")
            else:
                print(f"  第 {i+1} 帧失败")

    cap.release()
    print("同步模式测试完成\n")


def test_async_mode():
    """测试异步模式"""
    print("=" * 60)
    print("测试异步模式")
    print("=" * 60)

    cap = HikCameraCapture(0, async_mode=True)

    if cap.isOpened():
        print("异步模式: 等待缓冲区填充...")
        time.sleep(1.0)

        print("异步模式: 开始读取...")
        for i in range(10):
            ret, frame = cap.read()
            if ret:
                print(f"  第 {i+1} 帧成功, shape: {frame.shape}")
            else:
                print(f"  第 {i+1} 帧失败")
            time.sleep(0.1)

    cap.release()
    print("异步模式测试完成\n")


def test_grab_retrieve():
    """测试分步获取模式"""
    print("=" * 60)
    print("测试分步获取模式 (grab + retrieve)")
    print("=" * 60)

    cap = HikCameraCapture(0, async_mode=False)

    if cap.isOpened():
        print("分步模式: 测试 grab + retrieve...")
        for i in range(5):
            if cap.grab():
                ret, frame = cap.retrieve()
                if ret:
                    print(f"  第 {i+1} 帧成功, shape: {frame.shape}")
                else:
                    print(f"  第 {i+1} 帧 retrieve 失败")
            else:
                print(f"  第 {i+1} 帧 grab 失败")

    cap.release()
    print("分步模式测试完成\n")


if __name__ == "__main__":
    try:
        # 先枚举设备
        print("\n枚举设备:")
        devices = HikCameraCapture.enumerate_devices()
        print(f"找到 {len(devices)} 个设备\n")

        if len(devices) == 0:
            print("没有找到相机，测试结束")
            exit(0)

        # 测试各种模式
        test_sync_mode()
        test_grab_retrieve()
        test_async_mode()

        print("\n所有测试完成!")

    except KeyboardInterrupt:
        print("\n用户中断测试")
    except Exception as e:
        print(f"\n测试出错: {e}")
        import traceback
        traceback.print_exc()
