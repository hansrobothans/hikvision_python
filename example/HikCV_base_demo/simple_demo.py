# -*- coding: utf-8 -*-
"""
HikCV 基础演示 - 简单示例
展示如何使用 VideoCapture 类进行基本操作
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


def main():
    print("=" * 60)
    print("HikCamera.VideoCapture 基础演示")
    print("=" * 60)

    # 1. 创建相机对象（就像 cv2.VideoCapture 一样）
    print("\n1. 打开相机...")
    cap = HikCv.VideoCapture(0)

    if not cap.isOpened():
        print("错误: 无法打开相机")
        return

    print("✓ 成功打开相机")
    print(f"  后端: {cap.getBackendName()}")

    # 2. 设置相机参数
    print("\n2. 设置相机参数...")
    cap.set(HikCv.CAP_PROP_EXPOSURE, 15000)  # 设置曝光时间
    cap.set(HikCv.CAP_PROP_GAIN, 8)          # 设置增益

    print(f"  曝光: {cap.get(HikCv.CAP_PROP_EXPOSURE):.2f} us")
    print(f"  增益: {cap.get(HikCv.CAP_PROP_GAIN):.2f} dB")

    # 3. 采集图像
    print("\n3. 采集图像 (按 'q' 退出)...")
    frame_count = 0

    while True:
        # 读取一帧
        ret, frame = cap.read()

        if ret:
            frame_count += 1

            # 显示帧号
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # 显示图像
            cv2.imshow('HikCamera Demo', frame)

            # 按 'q' 退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # 4. 释放资源
    print(f"\n4. 释放资源...")
    print(f"  共采集 {frame_count} 帧")
    cap.release()
    cv2.destroyAllWindows()
    print("  ✓ 完成")


if __name__ == "__main__":
    main()
