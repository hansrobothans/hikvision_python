"""
海康工业相机封装 - 参考OpenCV VideoCapture实现方式
支持同步/异步抓取模式
"""

import numpy as np
import cv2
from ctypes import *
import threading
from queue import Queue
import time
import sys
import os

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入海康SDK (参考HikCamera的方式)
from MvImport.CameraParams_header import *
from MvImport.MvCameraControl_class import *


class HikCameraCapture:
    """
    海康工业相机封装类
    模仿OpenCV VideoCapture的使用方式
    """

    def __init__(self, index=0, async_mode=False):
        """
        初始化相机

        参数:
            index: 相机索引 (0表示第一个设备)
            async_mode: 是否使用异步抓取模式
        """
        self.cam = None
        self.is_opened = False
        self.async_mode = async_mode
        self.index = index

        # 异步模式相关 - 使用latest_frame而不是队列（参考HikCamera）
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.grab_thread = None
        self.is_grabbing = False
        self.thread_running = False

        # 内部缓存
        self.buf_save_image = None
        self.buf_save_image_len = 0
        self.st_frame_info = MV_FRAME_OUT_INFO_EX()
        self.buffer_lock = threading.Lock()

        # 用于grab/retrieve模式的临时帧存储
        self.grabbed_frame = None

        # 设备列表
        self.device_list = None

        # 自动打开设备
        if index is not None:
            self.open(index)

    def open(self, index=0):
        """
        打开相机设备

        参数:
            index: 相机索引或序列号
        返回:
            bool: 是否成功打开
        """
        if self.is_opened:
            print("相机已打开")
            return True

        try:
            # 1. 枚举设备
            deviceList = MV_CC_DEVICE_INFO_LIST()
            tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE

            ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
            if ret != 0:
                print(f"枚举设备失败! ret[0x{ret:x}]")
                return False

            if deviceList.nDeviceNum == 0:
                print("未找到设备")
                return False

            print(f"找到 {deviceList.nDeviceNum} 个设备")

            if index >= deviceList.nDeviceNum:
                print(f"设备索引 {index} 超出范围")
                return False

            self.device_list = deviceList

            # 2. 创建句柄
            stDeviceList = cast(deviceList.pDeviceInfo[index], POINTER(MV_CC_DEVICE_INFO)).contents
            self.cam = MvCamera()
            ret = self.cam.MV_CC_CreateHandle(stDeviceList)
            if ret != 0:
                print(f"创建句柄失败! ret[0x{ret:x}]")
                return False

            # 3. 打开设备
            ret = self.cam.MV_CC_OpenDevice()
            if ret != 0:
                print(f"打开设备失败! ret[0x{ret:x}]")
                self.cam.MV_CC_DestroyHandle()
                return False

            # 4. 对于GigE相机，设置最佳包大小
            if stDeviceList.nTLayerType == MV_GIGE_DEVICE:
                nPacketSize = self.cam.MV_CC_GetOptimalPacketSize()
                if int(nPacketSize) > 0:
                    ret = self.cam.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
                    if ret != 0:
                        print(f"警告: 设置包大小失败! ret[0x{ret:x}]")

            # 5. 设置触发模式为关闭(连续采集)
            ret = self.cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
            if ret != 0:
                print(f"警告: 设置触发模式失败! ret[0x{ret:x}]")

            # 6. 开始取流
            ret = self.cam.MV_CC_StartGrabbing()
            if ret != 0:
                print(f"开始取流失败! ret[0x{ret:x}]")
                return False

            self.is_opened = True
            self.is_grabbing = True

            # 7. 如果是异步模式，启动后台抓取线程
            if self.async_mode:
                self._start_grab_thread()

            print(f"成功打开相机 {index}")
            return True

        except Exception as e:
            print(f"打开相机异常: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def enumerate_devices():
        """
        枚举所有可用的海康相机

        返回:
            list: 相机信息列表
        """
        deviceList = MV_CC_DEVICE_INFO_LIST()
        tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE

        ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
        if ret != 0:
            print(f"枚举设备失败! ret[0x{ret:x}]")
            return []

        if deviceList.nDeviceNum == 0:
            print("没有找到相机设备!")
            return []

        print(f"找到 {deviceList.nDeviceNum} 个相机设备")

        camera_info_list = []
        for i in range(deviceList.nDeviceNum):
            mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents

            info = {'index': i}

            if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
                # GigE相机
                strModeName = ""
                for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                    if per == 0:
                        break
                    strModeName = strModeName + chr(per)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)

                info['type'] = 'GigE'
                info['model'] = strModeName
                info['serial'] = strSerialNumber

                nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
                info['ip'] = f"{nip1}.{nip2}.{nip3}.{nip4}"

                print(f"  [{i}] GigE: {strModeName} ({strSerialNumber}) - {info['ip']}")

            elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
                # USB相机
                strModeName = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                    if per == 0:
                        break
                    strModeName = strModeName + chr(per)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)

                info['type'] = 'USB'
                info['model'] = strModeName
                info['serial'] = strSerialNumber

                print(f"  [{i}] USB: {strModeName} ({strSerialNumber})")

            camera_info_list.append(info)

        return camera_info_list

    def grab(self):
        """
        抓取一帧 (只获取，不转换)
        类似OpenCV的grab()方法

        返回:
            bool: 是否成功抓取
        """
        if not self.is_opened:
            return False

        # 异步模式下检查是否有最新帧
        if self.async_mode:
            self.frame_lock.acquire()
            has_frame = self.latest_frame is not None
            self.frame_lock.release()
            return has_frame

        # 同步模式：真正抓取一帧并存储到临时变量
        try:
            stOutFrame = MV_FRAME_OUT()
            memset(byref(stOutFrame), 0, sizeof(stOutFrame))

            ret = self.cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
            if ret != 0:
                self.grabbed_frame = None
                return False

            try:
                # 获取缓存锁
                self.buffer_lock.acquire()

                # 确保缓存足够大
                if self.buf_save_image_len < stOutFrame.stFrameInfo.nFrameLen:
                    if self.buf_save_image is not None:
                        del self.buf_save_image
                    self.buf_save_image = (c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()
                    self.buf_save_image_len = stOutFrame.stFrameInfo.nFrameLen

                # 复制帧信息和数据
                cdll.msvcrt.memcpy(byref(self.st_frame_info),
                                  byref(stOutFrame.stFrameInfo),
                                  sizeof(MV_FRAME_OUT_INFO_EX))
                cdll.msvcrt.memcpy(byref(self.buf_save_image),
                                  stOutFrame.pBufAddr,
                                  self.st_frame_info.nFrameLen)

                self.buffer_lock.release()

                # 保存到临时变量，表示已经grab
                self.grabbed_frame = True
                return True

            except Exception as e:
                print(f"grab处理帧数据出错: {e}")
                if self.buffer_lock.locked():
                    self.buffer_lock.release()
                self.grabbed_frame = None
                return False
            finally:
                # 释放SDK缓存
                self.cam.MV_CC_FreeImageBuffer(stOutFrame)

        except Exception as e:
            print(f"grab异常: {e}")
            self.grabbed_frame = None
            return False

    def retrieve(self, flag=0):
        """
        解码并返回抓取的帧
        类似OpenCV的retrieve()方法

        参数:
            flag: 保留参数，兼容OpenCV接口
        返回:
            tuple: (ret, image) - ret为bool，image为numpy数组
        """
        if not self.is_opened:
            return False, None

        try:
            # 异步模式：从latest_frame获取
            if self.async_mode:
                self.frame_lock.acquire()
                frame = self.latest_frame
                self.frame_lock.release()

                if frame is None:
                    return False, None
                return True, frame.copy()

            # 同步模式：使用grab已经获取的数据进行转换
            if self.grabbed_frame is None:
                return False, None

            try:
                # 获取缓存锁
                self.buffer_lock.acquire()

                # 转换为BGR格式
                nBGRSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3
                buf_bgr = (c_ubyte * nBGRSize)()

                stConvertParam = MV_CC_PIXEL_CONVERT_PARAM()
                memset(byref(stConvertParam), 0, sizeof(stConvertParam))
                stConvertParam.nWidth = self.st_frame_info.nWidth
                stConvertParam.nHeight = self.st_frame_info.nHeight
                stConvertParam.pSrcData = self.buf_save_image
                stConvertParam.nSrcDataLen = self.st_frame_info.nFrameLen
                stConvertParam.enSrcPixelType = self.st_frame_info.enPixelType
                stConvertParam.enDstPixelType = PixelType_Gvsp_BGR8_Packed
                stConvertParam.pDstBuffer = buf_bgr
                stConvertParam.nDstBufferSize = nBGRSize

                ret = self.cam.MV_CC_ConvertPixelType(stConvertParam)
                if ret != 0:
                    print(f"像素格式转换失败! ret[0x{ret:x}]")
                    self.buffer_lock.release()
                    self.grabbed_frame = None
                    return False, None

                # 转换为numpy数组
                image_array = np.frombuffer(buf_bgr, dtype=np.uint8)
                image = image_array.reshape(
                    (self.st_frame_info.nHeight, self.st_frame_info.nWidth, 3)
                ).copy()

                self.buffer_lock.release()

                # 清除grabbed标记
                self.grabbed_frame = None

                return True, image

            except Exception as e:
                print(f"retrieve处理帧数据出错: {e}")
                if self.buffer_lock.locked():
                    self.buffer_lock.release()
                self.grabbed_frame = None
                return False, None

        except Exception as e:
            print(f"retrieve异常: {e}")
            return False, None

    def read(self):
        """
        抓取并返回一帧 (grab + retrieve)
        类似OpenCV的read()方法

        返回:
            tuple: (ret, image) - ret为bool，image为numpy数组
        """
        if not self.grab():
            return False, None
        return self.retrieve()

    def _start_grab_thread(self):
        """启动后台抓取线程"""
        if self.grab_thread is not None:
            return

        self.thread_running = True
        self.grab_thread = threading.Thread(target=self._grab_loop, daemon=True)
        self.grab_thread.start()
        print("异步抓取线程已启动")

    def _grab_loop(self):
        """后台抓取循环 - 参考HikCamera实现"""
        frame_count = 0
        error_count = 0

        while self.thread_running and self.is_opened:
            try:
                # 每次循环都创建新的Frame对象
                stOutFrame = MV_FRAME_OUT()
                memset(byref(stOutFrame), 0, sizeof(stOutFrame))

                ret = self.cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
                if ret == 0:
                    try:
                        # 获取缓存锁
                        self.buffer_lock.acquire()

                        # 确保缓存足够大
                        if self.buf_save_image_len < stOutFrame.stFrameInfo.nFrameLen:
                            if self.buf_save_image is not None:
                                del self.buf_save_image
                            self.buf_save_image = (c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()
                            self.buf_save_image_len = stOutFrame.stFrameInfo.nFrameLen

                        # 复制帧信息和数据
                        cdll.msvcrt.memcpy(byref(self.st_frame_info),
                                          byref(stOutFrame.stFrameInfo),
                                          sizeof(MV_FRAME_OUT_INFO_EX))
                        cdll.msvcrt.memcpy(byref(self.buf_save_image),
                                          stOutFrame.pBufAddr,
                                          self.st_frame_info.nFrameLen)

                        # 转换为BGR格式
                        nBGRSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3
                        buf_bgr = (c_ubyte * nBGRSize)()

                        stConvertParam = MV_CC_PIXEL_CONVERT_PARAM()
                        memset(byref(stConvertParam), 0, sizeof(stConvertParam))
                        stConvertParam.nWidth = self.st_frame_info.nWidth
                        stConvertParam.nHeight = self.st_frame_info.nHeight
                        stConvertParam.pSrcData = self.buf_save_image
                        stConvertParam.nSrcDataLen = self.st_frame_info.nFrameLen
                        stConvertParam.enSrcPixelType = self.st_frame_info.enPixelType
                        stConvertParam.enDstPixelType = PixelType_Gvsp_BGR8_Packed
                        stConvertParam.pDstBuffer = buf_bgr
                        stConvertParam.nDstBufferSize = nBGRSize

                        ret = self.cam.MV_CC_ConvertPixelType(stConvertParam)
                        if ret == 0:
                            # 转换为numpy数组
                            image_array = np.frombuffer(buf_bgr, dtype=np.uint8)
                            image = image_array.reshape(
                                (self.st_frame_info.nHeight, self.st_frame_info.nWidth, 3)
                            ).copy()

                            # 更新最新帧（参考HikCamera）
                            self.frame_lock.acquire()
                            self.latest_frame = image
                            self.frame_lock.release()

                            frame_count += 1
                            if frame_count == 1:
                                print(f"异步线程: 成功获取第一帧 {self.st_frame_info.nWidth}x{self.st_frame_info.nHeight}")
                        else:
                            print(f"异步线程: 像素格式转换失败! ret[0x{ret:x}]")

                        self.buffer_lock.release()

                    except Exception as e:
                        print(f"异步线程: 处理帧数据出错: {e}")
                        import traceback
                        traceback.print_exc()
                        if self.buffer_lock.locked():
                            self.buffer_lock.release()
                    finally:
                        # 释放SDK缓存
                        self.cam.MV_CC_FreeImageBuffer(stOutFrame)
                else:
                    if self.thread_running:
                        error_count += 1
                        # 只在首帧成功后才报告错误
                        if frame_count > 0 and error_count <= 5:
                            print(f"异步线程: 获取图像缓冲失败! ret[0x{ret:x}]")
                        time.sleep(0.01)

            except Exception as e:
                print(f"异步线程: 循环异常: {e}")
                time.sleep(0.01)

    def set(self, prop_id, value):
        """
        设置相机属性
        兼容OpenCV的set()接口

        参数:
            prop_id: 属性ID (cv2.CAP_PROP_*)
            value: 属性值
        """
        if not self.is_opened:
            return False

        try:
            if prop_id == cv2.CAP_PROP_EXPOSURE:
                # 设置曝光时间 (微秒)
                ret = self.cam.MV_CC_SetEnumValue("ExposureAuto", 0)  # 关闭自动曝光
                time.sleep(0.1)
                ret = self.cam.MV_CC_SetFloatValue("ExposureTime", float(value))
                return ret == 0
            elif prop_id == cv2.CAP_PROP_GAIN:
                # 设置增益
                ret = self.cam.MV_CC_SetFloatValue("Gain", float(value))
                return ret == 0
            elif prop_id == cv2.CAP_PROP_FPS:
                # 设置帧率
                ret = self.cam.MV_CC_SetFloatValue("AcquisitionFrameRate", float(value))
                return ret == 0
        except Exception as e:
            print(f"设置属性失败: {e}")

        return False

    def get(self, prop_id):
        """
        获取相机属性
        兼容OpenCV的get()接口

        参数:
            prop_id: 属性ID
        返回:
            float: 属性值
        """
        if not self.is_opened:
            return 0.0

        try:
            if prop_id == cv2.CAP_PROP_FRAME_WIDTH:
                return float(self.st_frame_info.nWidth)
            elif prop_id == cv2.CAP_PROP_FRAME_HEIGHT:
                return float(self.st_frame_info.nHeight)
            elif prop_id == cv2.CAP_PROP_FPS:
                stFloatValue = MVCC_FLOATVALUE()
                ret = self.cam.MV_CC_GetFloatValue("AcquisitionFrameRate", stFloatValue)
                if ret == 0:
                    return stFloatValue.fCurValue
            elif prop_id == cv2.CAP_PROP_EXPOSURE:
                stFloatValue = MVCC_FLOATVALUE()
                ret = self.cam.MV_CC_GetFloatValue("ExposureTime", stFloatValue)
                if ret == 0:
                    return stFloatValue.fCurValue
            elif prop_id == cv2.CAP_PROP_GAIN:
                stFloatValue = MVCC_FLOATVALUE()
                ret = self.cam.MV_CC_GetFloatValue("Gain", stFloatValue)
                if ret == 0:
                    return stFloatValue.fCurValue
        except Exception as e:
            print(f"获取属性失败: {e}")

        return 0.0

    def release(self):
        """释放相机资源"""
        if not self.is_opened:
            return

        # 停止抓取线程
        if self.async_mode:
            self.thread_running = False
            if self.grab_thread is not None:
                self.grab_thread.join(timeout=2)

        # 停止取流
        if self.is_grabbing:
            self.cam.MV_CC_StopGrabbing()
            self.is_grabbing = False

        # 关闭设备
        self.cam.MV_CC_CloseDevice()

        # 销毁句柄
        self.cam.MV_CC_DestroyHandle()

        # 清理缓存
        if self.buf_save_image is not None:
            del self.buf_save_image
            self.buf_save_image = None

        self.is_opened = False
        self.cam = None
        print("相机已释放")

    def isOpened(self):
        """检查相机是否打开"""
        return self.is_opened

    def __del__(self):
        """析构函数"""
        self.release()

    def __enter__(self):
        """支持with语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持with语句"""
        self.release()


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
