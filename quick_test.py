"""快速测试 claude_hkc.py 的修复"""

from claude_hkc import HikCameraCapture
import time

print("测试异步模式修复...")
print("=" * 60)

# 测试异步模式
cap = HikCameraCapture(0, async_mode=True)
if cap.isOpened():
    print("等待1秒让缓冲区填充...")
    time.sleep(1.0)

    print("开始读取10帧:")
    success_count = 0
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            print(f"  ✓ 第 {i+1} 帧成功, shape: {frame.shape}")
            success_count += 1
        else:
            print(f"  ✗ 第 {i+1} 帧失败")
        time.sleep(0.05)

    print(f"\n异步模式成功率: {success_count}/10")

cap.release()

print("\n" + "=" * 60)
print("测试分步获取模式...")
print("=" * 60)

# 测试分步获取
cap = HikCameraCapture(0, async_mode=False)
if cap.isOpened():
    print("开始分步获取5帧:")
    success_count = 0
    for i in range(5):
        if cap.grab():
            ret, frame = cap.retrieve()
            if ret:
                print(f"  ✓ 第 {i+1} 帧成功, shape: {frame.shape}")
                success_count += 1
            else:
                print(f"  ✗ 第 {i+1} 帧 retrieve 失败")
        else:
            print(f"  ✗ 第 {i+1} 帧 grab 失败")

    print(f"\n分步模式成功率: {success_count}/5")

cap.release()

print("\n测试完成!")
