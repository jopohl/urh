from libc.stdint cimport int8_t, uint16_t, uint32_t, int64_t, uint64_t

cdef extern from "htra_api.h":
    # --- Enums ---
    enum PhysicalInterface_TypeDef:
        USB

    enum DevicePowerSupply_TypeDef:
        USBPortOnly
        USBPortAndPowerPort

    enum DataFormat_TypeDef:
        Complex8bit
        Complex16bit

    enum IQS_TriggerSource_TypeDef:
        Bus

    enum TriggerMode_TypeDef:
        Adaptive

    # --- Structs ---
    ctypedef struct BootProfile_TypeDef:
        PhysicalInterface_TypeDef PhysicalInterface
        DevicePowerSupply_TypeDef DevicePowerSupply

    ctypedef struct DeviceInfo_TypeDef:
        uint64_t DeviceUID
        uint16_t Model
        uint16_t HardwareVersion

    ctypedef struct BootInfo_TypeDef:
        DeviceInfo_TypeDef DeviceInfo

    ctypedef struct IQS_Profile_TypeDef:
        double CenterFreq_Hz
        double RefLevel_dBm
        uint32_t DecimateFactor
        uint32_t BusTimeout_ms
        IQS_TriggerSource_TypeDef TriggerSource
        TriggerMode_TypeDef TriggerMode
        DataFormat_TypeDef DataFormat
        int8_t Atten

    ctypedef struct IQS_StreamInfo_TypeDef:
        double IQSampleRate
        uint32_t PacketSamples
        uint32_t PacketDataSize

    ctypedef struct IQStream_TypeDef:
        void* AlternIQStream
        IQS_StreamInfo_TypeDef IQS_StreamInfo

    # --- Functions ---
    int Device_Open(void** Device, int DeviceNum, const BootProfile_TypeDef* BootProfile, BootInfo_TypeDef* BootInfo)
    int Device_Close(void** Device)
    int IQS_ProfileDeInit(void** Device, IQS_Profile_TypeDef* UserProfile_O)
    int IQS_Configuration(void** Device, const IQS_Profile_TypeDef* ProfileIn, IQS_Profile_TypeDef* ProfileOut, IQS_StreamInfo_TypeDef* StreamInfo)
    int IQS_BusTriggerStart(void** Device)
    int IQS_GetIQStream_PM1(void **Device, IQStream_TypeDef* IQStream)
    int IQS_BusTriggerStop(void** Device)