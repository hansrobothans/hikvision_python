"""
海康工业相机封装 - 参考OpenCV VideoCapture实现方式
支持同步/异步抓取模式
"""
"""
海康工业相机简单Demo
使用 HikCamera 类，提供类似 OpenCV 的简单接口
按 'q' 键退出程序
"""
import sys
import os
import cv2
import time

# 添加父目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
parent_parent_dir = os.path.dirname(parent_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if parent_parent_dir not in sys.path:
    sys.path.insert(0, parent_parent_dir)


from claude_hkc import HikCameraCapture












# ====== 使用示例 ======
if __name__ == "__main__":

    # 方式1: 同步模式 (类似OpenCV)
    print("=== 同步模式示例 ===")

    # 先枚举设备
    HikCameraCapture.enumerate_devices()

    cap = HikCameraCapture(0, async_mode=False)

    if cap.isOpened():
        print("开始采集图像...")
        for i in range(10):
            ret, frame = cap.read()
            if ret:
                print(f"获取第 {i+1} 帧, shape: {frame.shape}")
                # 可以用OpenCV显示
                cv2.imshow("Frame", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("读取帧失败")

    cap.release()
    cv2.destroyAllWindows()

    # 方式2: 异步模式 (后台持续抓取)
    print("\n=== 异步模式示例 ===")
    with HikCameraCapture(0, async_mode=True) as cap:
        print("等待缓冲区填充...")
        time.sleep(1.0)  # 等待缓冲区填充

        print("开始读取异步缓冲... (按 'q' 退出)")
        frame_count = 0
        while frame_count < 100:  # 增加到100帧
            ret, frame = cap.read()
            if ret:
                frame_count += 1
                # 在图像上显示帧号
                info_text = f"Async Mode - Frame: {frame_count}"
                cv2.putText(frame, info_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # 显示图像
                cv2.imshow("Async Mode", frame)

                # 每10帧打印一次信息
                if frame_count % 10 == 0:
                    print(f"  已显示 {frame_count} 帧, shape: {frame.shape}")

                # 等待30ms，让窗口有时间刷新
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    print(f"  用户退出，共显示 {frame_count} 帧")
                    break
            else:
                # 如果读取失败，短暂等待
                time.sleep(0.01)

    cv2.destroyAllWindows()
    print(f"异步模式结束，共显示 {frame_count} 帧")

    # 方式3: 分步获取 (grab + retrieve)
    print("\n=== 分步获取示例 ===")
    cap = HikCameraCapture(0)

    if cap.isOpened():
        print("开始分步获取... (按 'q' 退出)")
        frame_count = 0
        max_frames = 50  # 增加到50帧

        for i in range(max_frames):
            if cap.grab():
                ret, frame = cap.retrieve()
                if ret:
                    frame_count += 1
                    # 在图像上显示帧号
                    info_text = f"Grab+Retrieve Mode - Frame: {frame_count}"
                    cv2.putText(frame, info_text, (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    # 显示图像
                    cv2.imshow("Grab+Retrieve Mode", frame)

                    # 每10帧打印一次信息
                    if frame_count % 10 == 0:
                        print(f"  已显示 {frame_count} 帧, shape: {frame.shape}")

                    # 等待30ms，让窗口有时间刷新
                    if cv2.waitKey(30) & 0xFF == ord('q'):
                        print(f"  用户退出，共显示 {frame_count} 帧")
                        break
                else:
                    print(f"  第 {i+1} 帧 retrieve 失败")
            else:
                print(f"  第 {i+1} 帧 grab 失败")

    cap.release()
    cv2.destroyAllWindows()
    print(f"分步获取模式结束，共显示 {frame_count} 帧")

    print("\n程序结束")
