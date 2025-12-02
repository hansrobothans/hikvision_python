# -*- coding: utf-8 -*-
import sys
import os
import cv2

# Add parent directory to path to import MvImport
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from CamOperation_class import CameraOperation, To_hex_str
from MvImport.MvCameraControl_class import *
from MvImport.MvErrorDefine_const import *
from MvImport.CameraParams_header import *
import ctypes


# Decoding Characters
def decoding_char(c_ubyte_value):
    c_char_p_value = ctypes.cast(c_ubyte_value, ctypes.c_char_p)
    try:
        decode_str = c_char_p_value.value.decode('gbk')  # Chinese characters
    except UnicodeDecodeError:
        decode_str = str(c_char_p_value.value)
    return decode_str


# ch:枚举相机 | en:enum devices
def enum_devices(deviceList):
    n_layer_type = (MV_GIGE_DEVICE | MV_USB_DEVICE | MV_GENTL_CAMERALINK_DEVICE
                    | MV_GENTL_CXP_DEVICE | MV_GENTL_XOF_DEVICE)
    ret = MvCamera.MV_CC_EnumDevices(n_layer_type, deviceList)
    if ret != 0:
        print("Enum devices fail! ret = 0x%x" % ret)
        return ret

    if deviceList.nDeviceNum == 0:
        print("Find no device!")
        return -1

    print("Find %d devices!" % deviceList.nDeviceNum)

    for i in range(0, deviceList.nDeviceNum):
        mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE or mvcc_dev_info.nTLayerType == MV_GENTL_GIGE_DEVICE:
            print("\n[%d] GigE Device:" % i)
            user_defined_name = decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chUserDefinedName)
            model_name = decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName)
            print("    User Defined Name: " + user_defined_name)
            print("    Model Name: " + model_name)

            nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
            nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
            nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
            nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
            print("    Current IP: %d.%d.%d.%d" % (nip1, nip2, nip3, nip4))

        elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
            print("\n[%d] USB Device:" % i)
            user_defined_name = decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chUserDefinedName)
            model_name = decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName)
            print("    User Defined Name: " + user_defined_name)
            print("    Model Name: " + model_name)

            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
            print("    Serial Number: " + strSerialNumber)

    return MV_OK


if __name__ == "__main__":

    # ch:初始化SDK | en: initialize SDK
    MvCamera.MV_CC_Initialize()

    print("=" * 60)
    print("OpenCV Camera Demo - Hikvision MVS SDK")
    print("=" * 60)

    deviceList = MV_CC_DEVICE_INFO_LIST()
    cam = MvCamera()
    obj_cam_operation = None

    # 枚举设备
    ret = enum_devices(deviceList)
    if ret != MV_OK:
        print("Enum devices failed! Press any key to exit...")
        input()
        sys.exit()

    # 选择设备
    if deviceList.nDeviceNum == 1:
        nSelCamIndex = 0
        print("\nAuto select device [0]")
    else:
        print("\nPlease select a device (0-%d): " % (deviceList.nDeviceNum - 1), end='')
        try:
            nSelCamIndex = int(input())
            if nSelCamIndex < 0 or nSelCamIndex >= deviceList.nDeviceNum:
                print("Invalid device index!")
                sys.exit()
        except ValueError:
            print("Invalid input!")
            sys.exit()

    # 创建相机操作对象
    obj_cam_operation = CameraOperation(cam, deviceList, nSelCamIndex)

    # 打开设备
    print("\nOpening device...")
    ret = obj_cam_operation.Open_device()
    if ret != MV_OK:
        print("Open device failed! ret = 0x%x" % ret)
        sys.exit()

    # 设置连续模式
    ret = obj_cam_operation.Set_trigger_mode(False)
    if ret != MV_OK:
        print("Set trigger mode failed! ret = 0x%x" % ret)

    # 获取参数
    ret = obj_cam_operation.Get_parameter()
    if ret == MV_OK:
        print("\nCamera Parameters:")
        print("  Exposure Time: %.2f" % obj_cam_operation.exposure_time)
        print("  Gain: %.2f" % obj_cam_operation.gain)
        print("  Frame Rate: %.2f" % obj_cam_operation.frame_rate)

    # 开始取流
    print("\nStarting grabbing...")
    ret = obj_cam_operation.Start_grabbing()
    if ret != MV_OK:
        print("Start grabbing failed! ret = 0x%x" % ret)
        obj_cam_operation.Close_device()
        sys.exit()

    print("\n" + "=" * 60)
    print("Camera is running. OpenCV window will open shortly.")
    print("=" * 60)
    print("\nControls:")
    print("  's' - Save current image")
    print("  'p' - Print parameters")
    print("  'q' or ESC - Quit")
    print("=" * 60 + "\n")

    # 创建OpenCV窗口（必须在主线程中）
    window_name = "Camera Display"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # 主循环 - 在主线程中显示图像
    try:
        while True:
            # 获取最新图像并显示
            image = obj_cam_operation.Get_latest_image()
            if image is not None:
                cv2.imshow(window_name, image)

            # 等待按键（必须调用waitKey才能刷新窗口）
            key = cv2.waitKey(30) & 0xFF

            if key == ord('q') or key == 27:  # 'q' or ESC
                print("\nQuitting...")
                break
            elif key == ord('s'):  # 's' - save image
                print("\nSaving image...")
                ret = obj_cam_operation.Save_Bmp()
                if ret == MV_OK:
                    print("Image saved successfully!")
                else:
                    print("Save image failed! ret = 0x%x" % ret)
            elif key == ord('p'):  # 'p' - print parameters
                ret = obj_cam_operation.Get_parameter()
                if ret == MV_OK:
                    print("\nCurrent Parameters:")
                    print("  Exposure Time: %.2f" % obj_cam_operation.exposure_time)
                    print("  Gain: %.2f" % obj_cam_operation.gain)
                    print("  Frame Rate: %.2f" % obj_cam_operation.frame_rate)

    except KeyboardInterrupt:
        print("\nInterrupted by user...")

    # 关闭OpenCV窗口
    cv2.destroyAllWindows()

    # 停止取流
    print("\nStopping grabbing...")
    ret = obj_cam_operation.Stop_grabbing()
    if ret != MV_OK:
        print("Stop grabbing failed! ret = 0x%x" % ret)

    # 关闭设备
    print("Closing device...")
    ret = obj_cam_operation.Close_device()
    if ret != MV_OK:
        print("Close device failed! ret = 0x%x" % ret)

    # ch:反初始化SDK | en: finalize SDK
    MvCamera.MV_CC_Finalize()

    print("\nProgram exited successfully.")
    sys.exit()
