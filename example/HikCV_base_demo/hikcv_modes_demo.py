# -*- coding: utf-8 -*-
"""
HikCv 三种采集模式完整演示
展示同步模式、异步模式和分步获取模式的使用方法

作者: Claude
日期: 2025-12-04
"""
import cv2
import sys
import os
import time

# 添加父目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
parent_parent_dir = os.path.dirname(parent_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if parent_parent_dir not in sys.path:
    sys.path.insert(0, parent_parent_dir)

# 导入 HikCv 模块
import HikCv


def demo_synchronous_mode():
    """
    演示 1: 同步模式 (类似 OpenCV 标准用法)

    特点:
    - 调用 read() 时阻塞等待获取图像
    - 简单直观，适合顺序处理
    - 与 OpenCV VideoCapture 用法完全相同
    """
    print("\n" + "=" * 70)
    print("演示 1: 同步模式 (Synchronous Mode)")
    print("=" * 70)
    print("\n说明: 同步模式下，read() 会阻塞等待直到获取到图像")
    print("适用场景: 简单的图像采集和处理流程\n")

    # 创建相机对象
    print("正在打开相机...")
    cap = HikCv.VideoCapture(0)

    if not cap.isOpened():
        print("❌ 错误: 无法打开相机")
        return

    print("✓ 成功打开相机")
    print(f"  后端: {cap.getBackendName()}")
    print(f"  分辨率: {int(cap.get(HikCv.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(HikCv.CAP_PROP_FRAME_HEIGHT))}")

    # 设置相机参数
    print("\n正在设置相机参数...")
    cap.set(HikCv.CAP_PROP_EXPOSURE, 10000)  # 曝光时间 10ms
    cap.set(HikCv.CAP_PROP_GAIN, 5)          # 增益 5dB
    print(f"  曝光: {cap.get(HikCv.CAP_PROP_EXPOSURE):.2f} us")
    print(f"  增益: {cap.get(HikCv.CAP_PROP_GAIN):.2f} dB")

    # 采集图像
    print("\n开始采集图像 (按 'q' 退出, 'p' 暂停)...")
    frame_count = 0
    start_time = time.time()
    paused = False

    while True:
        if not paused:
            # 读取一帧图像
            ret, frame = cap.read()

            if ret:
                frame_count += 1
                elapsed_time = time.time() - start_time
                fps = frame_count / elapsed_time if elapsed_time > 0 else 0

                # 在图像上添加信息
                info_text = f"Sync Mode | Frame: {frame_count} | FPS: {fps:.1f}"
                cv2.putText(frame, info_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                cv2.putText(frame, "Press 'q' to quit, 'p' to pause", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

                # 显示图像
                cv2.imshow('Synchronous Mode', frame)

                # 每10帧打印一次
                if frame_count % 10 == 0:
                    print(f"  已采集 {frame_count} 帧, 平均 FPS: {fps:.2f}")
            else:
                print("  ⚠ 读取帧失败")

        # 按键处理
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('p'):
            paused = not paused
            status = "暂停" if paused else "继续"
            print(f"  {status}采集...")

    # 统计信息
    elapsed_time = time.time() - start_time
    avg_fps = frame_count / elapsed_time if elapsed_time > 0 else 0

    print(f"\n✓ 同步模式演示完成")
    print(f"  总帧数: {frame_count}")
    print(f"  总时长: {elapsed_time:.2f} 秒")
    print(f"  平均帧率: {avg_fps:.2f} FPS")

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()


def demo_asynchronous_mode():
    """
    演示 2: 异步模式 (后台持续采集)

    特点:
    - 后台线程持续采集图像到缓冲区
    - read() 立即返回最新图像
    - 适合高帧率采集和实时处理

    注意: HikCv 的 VideoCapture 内部已经使用异步采集
    """
    print("\n" + "=" * 70)
    print("演示 2: 异步模式 (Asynchronous Mode)")
    print("=" * 70)
    print("\n说明: 后台线程持续采集图像，read() 立即返回最新帧")
    print("适用场景: 实时图像处理，高帧率采集\n")

    # 使用上下文管理器自动管理资源
    print("正在打开相机...")
    with HikCv.VideoCapture(0) as cap:
        if not cap.isOpened():
            print("❌ 错误: 无法打开相机")
            return

        print("✓ 成功打开相机")
        print(f"  分辨率: {int(cap.get(HikCv.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(HikCv.CAP_PROP_FRAME_HEIGHT))}")

        # 等待缓冲区填充
        print("\n等待后台采集线程启动...")
        time.sleep(0.5)

        # 测试异步读取性能
        print("\n开始异步采集 (按 'q' 退出, 's' 保存图像)...")
        frame_count = 0
        saved_count = 0
        start_time = time.time()
        read_times = []

        while True:
            # 测量读取时间
            read_start = time.time()
            ret, frame = cap.read()
            read_time = (time.time() - read_start) * 1000  # 转换为毫秒

            if ret:
                frame_count += 1
                read_times.append(read_time)

                elapsed_time = time.time() - start_time
                fps = frame_count / elapsed_time if elapsed_time > 0 else 0
                avg_read_time = sum(read_times) / len(read_times)

                # 在图像上添加信息
                info_text = f"Async Mode | Frame: {frame_count} | FPS: {fps:.1f}"
                cv2.putText(frame, info_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

                perf_text = f"Read time: {read_time:.2f}ms (avg: {avg_read_time:.2f}ms)"
                cv2.putText(frame, perf_text, (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

                cv2.putText(frame, "Press 'q' to quit, 's' to save", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

                # 显示图像
                cv2.imshow('Asynchronous Mode', frame)

                # 每20帧打印一次性能数据
                if frame_count % 20 == 0:
                    print(f"  已采集 {frame_count} 帧, FPS: {fps:.2f}, "
                          f"平均读取时间: {avg_read_time:.2f}ms")
            else:
                print("  ⚠ 读取帧失败")
                time.sleep(0.01)

            # 按键处理
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s') and ret:
                # 保存图像
                filename = f"async_frame_{frame_count:04d}.jpg"
                cv2.imwrite(filename, frame)
                saved_count += 1
                print(f"  💾 已保存图像: {filename}")

        # 统计信息
        elapsed_time = time.time() - start_time
        avg_fps = frame_count / elapsed_time if elapsed_time > 0 else 0
        avg_read_time = sum(read_times) / len(read_times) if read_times else 0

        print(f"\n✓ 异步模式演示完成")
        print(f"  总帧数: {frame_count}")
        print(f"  保存帧数: {saved_count}")
        print(f"  总时长: {elapsed_time:.2f} 秒")
        print(f"  平均帧率: {avg_fps:.2f} FPS")
        print(f"  平均读取时间: {avg_read_time:.2f} ms")

    cv2.destroyAllWindows()


def demo_grab_retrieve_mode():
    """
    演示 3: 分步获取模式 (Grab + Retrieve)

    特点:
    - grab() 触发采集但不解码
    - retrieve() 解码上次抓取的图像
    - 适合多相机同步采集
    - 可以在 grab() 和 retrieve() 之间做其他处理
    """
    print("\n" + "=" * 70)
    print("演示 3: 分步获取模式 (Grab + Retrieve Mode)")
    print("=" * 70)
    print("\n说明: grab() 抓取帧, retrieve() 解码帧")
    print("适用场景: 多相机同步采集，需要精确时序控制\n")

    # 创建相机对象
    print("正在打开相机...")
    cap = HikCv.VideoCapture(0)

    if not cap.isOpened():
        print("❌ 错误: 无法打开相机")
        return

    print("✓ 成功打开相机")
    print(f"  分辨率: {int(cap.get(HikCv.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(HikCv.CAP_PROP_FRAME_HEIGHT))}")

    # 演示分步处理
    print("\n开始分步采集 (按 'q' 退出, 'Space' 单步执行)...")
    frame_count = 0
    grab_count = 0
    retrieve_count = 0
    start_time = time.time()
    single_step = False

    while True:
        # 第一步: Grab (抓取帧但不解码)
        grab_start = time.time()
        if cap.grab():
            grab_time = (time.time() - grab_start) * 1000
            grab_count += 1

            # 模拟在 grab 和 retrieve 之间做其他处理
            # 例如：多相机场景下，可以在这里触发其他相机的 grab
            processing_start = time.time()
            # 模拟一些处理时间
            time.sleep(0.001)  # 1ms 的处理时间
            processing_time = (time.time() - processing_start) * 1000

            # 第二步: Retrieve (解码帧)
            retrieve_start = time.time()
            ret, frame = cap.retrieve()
            retrieve_time = (time.time() - retrieve_start) * 1000

            if ret:
                retrieve_count += 1
                frame_count += 1

                elapsed_time = time.time() - start_time
                fps = frame_count / elapsed_time if elapsed_time > 0 else 0

                # 在图像上添加详细信息
                info_text = f"Grab+Retrieve Mode | Frame: {frame_count} | FPS: {fps:.1f}"
                cv2.putText(frame, info_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 128, 0), 2)

                timing_text = f"Grab: {grab_time:.2f}ms | Process: {processing_time:.2f}ms | Retrieve: {retrieve_time:.2f}ms"
                cv2.putText(frame, timing_text, (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

                stats_text = f"Grabbed: {grab_count} | Retrieved: {retrieve_count}"
                cv2.putText(frame, stats_text, (10, 85),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

                mode_text = "Single Step" if single_step else "Continuous"
                cv2.putText(frame, f"Mode: {mode_text} (Space to toggle)", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

                cv2.putText(frame, "Press 'q' to quit", (10, 135),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

                # 显示图像
                cv2.imshow('Grab+Retrieve Mode', frame)

                # 每10帧打印一次
                if frame_count % 10 == 0:
                    print(f"  帧 {frame_count}: Grab={grab_time:.2f}ms, "
                          f"Process={processing_time:.2f}ms, "
                          f"Retrieve={retrieve_time:.2f}ms")
            else:
                print(f"  ⚠ Retrieve 失败 (grab 成功)")
        else:
            print(f"  ⚠ Grab 失败")

        # 按键处理
        wait_time = 0 if single_step else 1
        key = cv2.waitKey(wait_time) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):  # 空格键切换单步/连续模式
            single_step = not single_step
            mode = "单步" if single_step else "连续"
            print(f"  切换到{mode}模式")

    # 统计信息
    elapsed_time = time.time() - start_time
    avg_fps = frame_count / elapsed_time if elapsed_time > 0 else 0

    print(f"\n✓ 分步获取模式演示完成")
    print(f"  Grab 次数: {grab_count}")
    print(f"  Retrieve 成功次数: {retrieve_count}")
    print(f"  总帧数: {frame_count}")
    print(f"  总时长: {elapsed_time:.2f} 秒")
    print(f"  平均帧率: {avg_fps:.2f} FPS")

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()


def demo_comparison():
    """
    演示 4: 三种模式性能对比

    对比三种模式的性能差异
    """
    print("\n" + "=" * 70)
    print("演示 4: 三种模式性能对比")
    print("=" * 70)
    print("\n正在测试三种模式的性能...\n")

    test_frames = 100
    results = {}

    # 测试 1: read() 模式 (内部已异步)
    print("测试 1: read() 模式...")
    cap = HikCv.VideoCapture(0)
    if cap.isOpened():
        time.sleep(0.5)  # 等待稳定
        start_time = time.time()
        success_count = 0

        for i in range(test_frames):
            ret, frame = cap.read()
            if ret:
                success_count += 1

        elapsed = time.time() - start_time
        results['read'] = {
            'fps': success_count / elapsed,
            'success': success_count,
            'time': elapsed
        }
        cap.release()
        print(f"  ✓ 完成: {success_count}/{test_frames} 帧, "
              f"{results['read']['fps']:.2f} FPS, "
              f"耗时 {elapsed:.2f}s")

    # 测试 2: grab() + retrieve() 模式
    print("\n测试 2: grab() + retrieve() 模式...")
    cap = HikCv.VideoCapture(0)
    if cap.isOpened():
        time.sleep(0.5)
        start_time = time.time()
        success_count = 0

        for i in range(test_frames):
            if cap.grab():
                ret, frame = cap.retrieve()
                if ret:
                    success_count += 1

        elapsed = time.time() - start_time
        results['grab_retrieve'] = {
            'fps': success_count / elapsed,
            'success': success_count,
            'time': elapsed
        }
        cap.release()
        print(f"  ✓ 完成: {success_count}/{test_frames} 帧, "
              f"{results['grab_retrieve']['fps']:.2f} FPS, "
              f"耗时 {elapsed:.2f}s")

    # 输出对比结果
    print("\n" + "-" * 70)
    print("性能对比结果:")
    print("-" * 70)

    for mode, data in results.items():
        mode_name = {
            'read': 'read() 模式',
            'grab_retrieve': 'grab() + retrieve() 模式'
        }[mode]

        print(f"\n{mode_name}:")
        print(f"  帧率: {data['fps']:.2f} FPS")
        print(f"  成功率: {data['success']}/{test_frames} ({data['success']/test_frames*100:.1f}%)")
        print(f"  总耗时: {data['time']:.2f} 秒")

    print("\n" + "-" * 70)
    print("结论:")
    print("  - read() 模式最简单，适合大多数场景")
    print("  - grab()+retrieve() 适合多相机同步采集")
    print("  - HikCv 内部已实现异步采集，性能已优化")
    print("-" * 70)


def main():
    """主函数"""
    print("=" * 70)
    print("HikCv 三种采集模式完整演示")
    print("=" * 70)
    print("\n本演示将展示 HikCv 的三种图像采集模式:")
    print("  1. 同步模式 - 标准的 read() 方法")
    print("  2. 异步模式 - 后台持续采集")
    print("  3. 分步获取 - grab() + retrieve() 方法")
    print("  4. 性能对比 - 三种模式对比测试")

    # 首先枚举设备
    print("\n正在枚举相机设备...")
    devices = HikCv.enumerate_devices()

    if len(devices) == 0:
        print("❌ 未找到相机设备，程序退出")
        return

    print(f"✓ 找到 {len(devices)} 个设备\n")

    # 显示菜单
    while True:
        print("\n" + "=" * 70)
        print("请选择要运行的演示:")
        print("-" * 70)
        print("  1 - 同步模式演示 (Synchronous Mode)")
        print("  2 - 异步模式演示 (Asynchronous Mode)")
        print("  3 - 分步获取模式演示 (Grab + Retrieve Mode)")
        print("  4 - 性能对比测试")
        print("  5 - 运行所有演示")
        print("  0 - 退出程序")
        print("-" * 70)

        choice = input("请输入选项 (0-5): ").strip()

        try:
            if choice == '1':
                demo_synchronous_mode()
            elif choice == '2':
                demo_asynchronous_mode()
            elif choice == '3':
                demo_grab_retrieve_mode()
            elif choice == '4':
                demo_comparison()
            elif choice == '5':
                demo_synchronous_mode()
                demo_asynchronous_mode()
                demo_grab_retrieve_mode()
                demo_comparison()
            elif choice == '0':
                print("\n程序退出")
                break
            else:
                print("❌ 无效的选项，请重新选择")
        except KeyboardInterrupt:
            print("\n\n检测到中断信号，程序退出")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("感谢使用 HikCv 演示程序")
    print("=" * 70)


if __name__ == "__main__":
    main()
