# -*- coding: utf-8 -*-
"""
HikCV vs OpenCV 对比演示
展示两者完全相同的使用方式
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



def camera_demo(VideoCapture, CAP_PROP_EXPOSURE, title):
    """
    通用相机演示函数

    这个函数可以同时用于 cv2.VideoCapture 和 HikCV.VideoCapture
    代码完全相同！
    """
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)

    # 打开相机（完全相同的代码）
    cap = VideoCapture(0)

    if not cap.isOpened():
        print("错误: 无法打开相机")
        return

    print(f"✓ 成功打开相机")
    print(f"  后端: {cap.getBackendName()}")

    # 设置曝光（完全相同的代码）
    cap.set(CAP_PROP_EXPOSURE, 15000)
    print(f"  曝光: {cap.get(CAP_PROP_EXPOSURE):.2f}")

    # 采集图像（完全相同的代码）
    print("\n采集 50 帧...")
    frame_count = 0

    while frame_count < 50:
        ret, frame = cap.read()
        if ret:
            frame_count += 1

            # 显示信息
            info = f"{title} - Frame: {frame_count}/50"
            cv2.putText(frame, info, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow(title, frame)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                break

    print(f"✓ 采集了 {frame_count} 帧")

    # 释放资源（完全相同的代码）
    cap.release()
    cv2.destroyAllWindows()


def show_code_comparison():
    """显示代码对比"""
    print("\n" + "="*60)
    print("代码对比")
    print("="*60)

    print("\nOpenCV 代码:")
    print("-" * 60)
    print("""
from cv2 import VideoCapture, CAP_PROP_EXPOSURE

cap = VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    cap.set(CAP_PROP_EXPOSURE, 15000)
    cap.release()
""")

    print("\nHikCv 代码:")
    print("-" * 60)
    print("""
from HikCv import VideoCapture, CAP_PROP_EXPOSURE

cap = VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    cap.set(CAP_PROP_EXPOSURE, 15000)
    cap.release()
""")

    print("\n" + "="*60)
    print("看出区别了吗？")
    print("只有导入语句不同，其他代码完全相同！")
    print("="*60)


def main():
    print("="*60)
    print("HikCV vs OpenCV 对比演示")
    print("="*60)

    # 显示代码对比
    show_code_comparison()

    print("\n请选择:")
    print("  1 - 使用 HikCV (海康工业相机)")
    print("  2 - 使用 OpenCV (普通USB摄像头)")
    print("  3 - 只显示代码对比")

    choice = input("\n请输入选项 (1-3): ").strip()

    if choice == '1':
        print("\n使用 HikCv.VideoCapture")
        try:
            from HikCv import VideoCapture, CAP_PROP_EXPOSURE
            camera_demo(VideoCapture, CAP_PROP_EXPOSURE, "HikCv Camera")
        except Exception as e:
            print(f"错误: {e}")

    elif choice == '2':
        print("\n使用 cv2.VideoCapture")
        try:
            from cv2 import VideoCapture as CV_VideoCapture
            from cv2 import CAP_PROP_EXPOSURE as CV_CAP_PROP_EXPOSURE
            camera_demo(CV_VideoCapture, CV_CAP_PROP_EXPOSURE, "OpenCV Camera")
        except Exception as e:
            print(f"错误: {e}")

    elif choice == '3':
        print("\n代码对比已显示在上方")

    else:
        print("无效的选项")

    print("\n" + "="*60)
    print("总结:")
    print("  ✓ HikCv.VideoCapture 完全兼容 OpenCV 接口")
    print("  ✓ 只需改变导入语句")
    print("  ✓ 业务代码无需任何修改")
    print("="*60)


if __name__ == "__main__":
    main()
