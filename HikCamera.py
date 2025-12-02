"""
海康工业相机 OpenCV 风格封装类
提供类似 OpenCV 的简单接口，方便使用
"""
import sys
import os
import threading
import time
import numpy as np
from ctypes import *

# Add MvImport to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from MvImport.CameraParams_header import *
from MvImport.MvCameraControl_class import *


class HikCamera:
    """
    海康工业相机封装类
    提供类似 OpenCV VideoCapture 的接口

    使用示例:
        # 枚举相机
        camera_list = HikCamera.enumerate_devices()
        print(f"找到 {len(camera_list)} 个相机")

        # 打开相机
        cam = HikCamera(0)  # 打开第一个相机
        if not cam.isOpened():
            print("无法打开相机")
            exit()

        # 读取图像
        while True:
            ret, frame = cam.read()
            if ret:
                cv2.imshow('Hikvision Camera', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # 释放相机
        cam.release()
    """

    # 类变量：存储设备列表
    _device_list = None
    _device_count = 0

    def __init__(self, index=0):
        """
        初始化海康相机

        参数:
            index: 相机索引，从0开始
        """
        self.index = index
        self.cam = None
        self.is_opened = False
        self.is_grabbing = False

        # 图像缓存相关
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.buffer_lock = threading.Lock()

        # 内部缓存
        self.buf_save_image = None
        self.buf_save_image_len = 0
        self.st_frame_info = MV_FRAME_OUT_INFO_EX()

        # 线程控制
        self.grab_thread = None
        self.thread_running = False

        # 自动打开相机
        self.open()

    @staticmethod
    def enumerate_devices():
        """
        枚举所有可用的海康相机

        返回:
            list: 相机信息列表，每个元素包含 {'index': int, 'model': str, 'serial': str}
        """
        deviceList = MV_CC_DEVICE_INFO_LIST()
        tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE

        ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
        if ret != 0:
            print(f"枚举设备失败! ret[0x{ret:x}]")
            return []

        # 保存设备列表到类变量
        HikCamera._device_list = deviceList
        HikCamera._device_count = deviceList.nDeviceNum

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

    def open(self):
        """
        打开相机设备

        返回:
            bool: 成功返回True，失败返回False
        """
        if self.is_opened:
            print("相机已经打开")
            return True

        # 如果没有枚举设备，先枚举
        if HikCamera._device_list is None:
            HikCamera.enumerate_devices()

        if HikCamera._device_count == 0:
            print("没有可用的相机设备")
            return False

        if self.index >= HikCamera._device_count:
            print(f"相机索引 {self.index} 超出范围 (0-{HikCamera._device_count-1})")
            return False

        # 创建相机句柄
        stDeviceList = cast(HikCamera._device_list.pDeviceInfo[self.index],
                           POINTER(MV_CC_DEVICE_INFO)).contents
        self.cam = MvCamera()
        ret = self.cam.MV_CC_CreateHandle(stDeviceList)
        if ret != 0:
            print(f"创建句柄失败! ret[0x{ret:x}]")
            return False

        # 打开设备
        ret = self.cam.MV_CC_OpenDevice()
        if ret != 0:
            print(f"打开设备失败! ret[0x{ret:x}]")
            self.cam.MV_CC_DestroyHandle()
            return False

        print(f"成功打开相机 [{self.index}]")
        self.is_opened = True

        # 对于GigE相机，设置最佳包大小
        if stDeviceList.nTLayerType == MV_GIGE_DEVICE:
            nPacketSize = self.cam.MV_CC_GetOptimalPacketSize()
            if int(nPacketSize) > 0:
                ret = self.cam.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
                if ret != 0:
                    print(f"警告: 设置包大小失败! ret[0x{ret:x}]")

        # 设置触发模式为关闭（连续采集模式）
        ret = self.cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
        if ret != 0:
            print(f"警告: 设置触发模式失败! ret[0x{ret:x}]")

        # 自动开始采集
        self._start_grabbing()

        return True

    def _start_grabbing(self):
        """内部方法：开始图像采集"""
        if self.is_grabbing or not self.is_opened:
            return False

        ret = self.cam.MV_CC_StartGrabbing()
        if ret != 0:
            print(f"开始取流失败! ret[0x{ret:x}]")
            return False

        self.is_grabbing = True
        self.thread_running = True

        # 启动取图线程
        self.grab_thread = threading.Thread(target=self._grab_thread_func)
        self.grab_thread.daemon = True
        self.grab_thread.start()

        print("开始图像采集")
        return True

    def _stop_grabbing(self):
        """内部方法：停止图像采集"""
        if not self.is_grabbing:
            return False

        self.thread_running = False

        # 等待线程结束
        if self.grab_thread is not None:
            self.grab_thread.join(timeout=2.0)

        ret = self.cam.MV_CC_StopGrabbing()
        if ret != 0:
            print(f"停止取流失败! ret[0x{ret:x}]")
            return False

        self.is_grabbing = False
        print("停止图像采集")
        return True

    def _grab_thread_func(self):
        """取图线程函数"""
        stOutFrame = MV_FRAME_OUT()
        memset(byref(stOutFrame), 0, sizeof(stOutFrame))

        frame_count = 0
        error_count = 0

        while self.thread_running:
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

                        # 更新最新帧
                        self.frame_lock.acquire()
                        self.latest_frame = image
                        self.frame_lock.release()

                        frame_count += 1
                        if frame_count == 1:
                            print(f"成功获取第一帧图像: {self.st_frame_info.nWidth}x{self.st_frame_info.nHeight}")
                    else:
                        print(f"像素格式转换失败! ret[0x{ret:x}]")

                    self.buffer_lock.release()

                except Exception as e:
                    print(f"处理帧数据出错: {e}")
                    import traceback
                    traceback.print_exc()
                    if self.buffer_lock.locked():
                        self.buffer_lock.release()
                finally:
                    # 释放缓存
                    self.cam.MV_CC_FreeImageBuffer(stOutFrame)
            else:
                if self.thread_running:
                    error_count += 1
                    # 只在首帧成功后才报告错误（避免启动时的正常等待被误报为错误）
                    if frame_count > 0 and error_count <= 5:
                        print(f"获取图像缓冲失败! ret[0x{ret:x}]")
                    time.sleep(0.01)  # 避免CPU占用过高

    def read(self):
        """
        读取一帧图像（类似OpenCV的cap.read()）

        返回:
            tuple: (ret, frame)
                ret: bool, 是否成功读取
                frame: numpy.ndarray, BGR格式的图像，如果失败则为None
        """
        if not self.is_opened or not self.is_grabbing:
            return False, None

        # 等待第一帧图像（最多等待3秒）
        timeout = 3.0
        start_time = time.time()
        while self.latest_frame is None and (time.time() - start_time) < timeout:
            time.sleep(0.01)

        self.frame_lock.acquire()
        frame = self.latest_frame
        self.frame_lock.release()

        if frame is None:
            return False, None

        return True, frame.copy()

    def isOpened(self):
        """
        检查相机是否已打开（类似OpenCV的cap.isOpened()）

        返回:
            bool: 相机是否已打开
        """
        return self.is_opened

    def release(self):
        """
        释放相机资源（类似OpenCV的cap.release()）
        """
        if not self.is_opened:
            return

        # 停止采集
        if self.is_grabbing:
            self._stop_grabbing()

        # 关闭设备
        ret = self.cam.MV_CC_CloseDevice()
        if ret != 0:
            print(f"关闭设备失败! ret[0x{ret:x}]")

        # 销毁句柄
        self.cam.MV_CC_DestroyHandle()

        self.is_opened = False
        self.cam = None

        # 清理缓存
        if self.buf_save_image is not None:
            del self.buf_save_image
            self.buf_save_image = None

        print(f"相机 [{self.index}] 已释放")

    def get(self, propId):
        """
        获取相机属性（类似OpenCV的cap.get()）

        参数:
            propId: 属性ID
                - 3: CV_CAP_PROP_FRAME_WIDTH (宽度)
                - 4: CV_CAP_PROP_FRAME_HEIGHT (高度)
                - 5: CV_CAP_PROP_FPS (帧率)
                - 15: CV_CAP_PROP_EXPOSURE (曝光时间)
                - 17: CV_CAP_PROP_GAIN (增益)

        返回:
            float: 属性值
        """
        if not self.is_opened:
            return 0.0

        try:
            if propId == 3:  # Width
                return float(self.st_frame_info.nWidth)
            elif propId == 4:  # Height
                return float(self.st_frame_info.nHeight)
            elif propId == 5:  # FPS
                stFloatValue = MVCC_FLOATVALUE()
                ret = self.cam.MV_CC_GetFloatValue("AcquisitionFrameRate", stFloatValue)
                if ret == 0:
                    return stFloatValue.fCurValue
            elif propId == 15:  # Exposure
                stFloatValue = MVCC_FLOATVALUE()
                ret = self.cam.MV_CC_GetFloatValue("ExposureTime", stFloatValue)
                if ret == 0:
                    return stFloatValue.fCurValue
            elif propId == 17:  # Gain
                stFloatValue = MVCC_FLOATVALUE()
                ret = self.cam.MV_CC_GetFloatValue("Gain", stFloatValue)
                if ret == 0:
                    return stFloatValue.fCurValue
        except Exception as e:
            print(f"获取属性失败: {e}")

        return 0.0

    def set(self, propId, value):
        """
        设置相机属性（类似OpenCV的cap.set()）

        参数:
            propId: 属性ID
                - 5: CV_CAP_PROP_FPS (帧率)
                - 15: CV_CAP_PROP_EXPOSURE (曝光时间)
                - 17: CV_CAP_PROP_GAIN (增益)
            value: 属性值

        返回:
            bool: 是否设置成功
        """
        if not self.is_opened:
            return False

        try:
            if propId == 5:  # FPS
                ret = self.cam.MV_CC_SetFloatValue("AcquisitionFrameRate", float(value))
                return ret == 0
            elif propId == 15:  # Exposure
                ret = self.cam.MV_CC_SetEnumValue("ExposureAuto", 0)  # 关闭自动曝光
                time.sleep(0.1)
                ret = self.cam.MV_CC_SetFloatValue("ExposureTime", float(value))
                return ret == 0
            elif propId == 17:  # Gain
                ret = self.cam.MV_CC_SetFloatValue("Gain", float(value))
                return ret == 0
        except Exception as e:
            print(f"设置属性失败: {e}")

        return False

    def __del__(self):
        """析构函数：确保资源被释放"""
        if self.is_opened:
            self.release()


# OpenCV风格的属性常量
CAP_PROP_FRAME_WIDTH = 3
CAP_PROP_FRAME_HEIGHT = 4
CAP_PROP_FPS = 5
CAP_PROP_EXPOSURE = 15
CAP_PROP_GAIN = 17
