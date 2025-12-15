from libc.stdint cimport int8_t, uint8_t, uint16_t, uint32_t, int64_t, uint64_t

cdef extern from "htra_api.h":
    # --- Enums from htra_api.h ---
    ctypedef enum PhysicalInterface_TypeDef: USB, QSFP, ETH, HLVDS, VIRTUAL
    ctypedef enum DevicePowerSupply_TypeDef: USBPortAndPowerPort, USBPortOnly, Others
    ctypedef enum DataFormat_TypeDef: Complex16bit=0x00, Complex32bit=0x01, Complex8bit=0x02, Complexfloat=0x06
    ctypedef enum IQS_TriggerSource_TypeDef: FreeRun, External, Bus, Level, Timer, TxSweep, MultiDevSyncByExt, MultiDevSyncByGNSS1PPS, SpectrumMask, GNSS1PPS
    ctypedef enum TriggerMode_TypeDef: FixedPoints, Adaptive
    ctypedef enum RxPort_TypeDef: ExternalPort, InternalPort, ANT_Port, TR_Port, SWR_Port, INT_Port
    ctypedef enum TriggerEdge_TypeDef: RisingEdge, FallingEdge, DoubleEdge
    ctypedef enum TriggerOutMode_TypeDef: None_TriggerOutMode "None"=0x00, PerHop, PerSweep, PerProfile
    ctypedef enum TriggerOutPulsePolarity_TypeDef: Positive, Negative
    ctypedef enum TriggerTimerSync_TypeDef: NoneSync, SyncToExt_RisingEdge, SyncToExt_FallingEdge, SyncToExt_SingleRisingEdge, SyncToExt_SingleFallingEdge, SyncToGNSS1PPS_RisingEdge, SyncToGNSS1PPS_FallingEdge, SyncToGNSS1PPS_SingleRisingEdge, SyncToGNSS1PPS_SingleFallingEdge
    ctypedef enum GainStrategy_TypeDef: LowNoisePreferred, HighLinearityPreferred
    ctypedef enum PreamplifierState_TypeDef: AutoOn, ForcedOff
    ctypedef enum ReferenceClockSource_TypeDef: ReferenceClockSource_Internal, ReferenceClockSource_External, ReferenceClockSource_Internal_Premium, ReferenceClockSource_External_Forced
    ctypedef enum SystemClockSource_TypeDef: SystemClockSource_Internal, SystemClockSource_External
    ctypedef enum DCCancelerMode_TypeDef: DCCOff, DCCHighPassFilterMode, DCCManualOffsetMode, DCCAutoOffsetMode
    ctypedef enum QDCMode_TypeDef: QDCOff, QDCManualMode, QDCAutoMode
    ctypedef enum LOOptimization_TypeDef: LOOpt_Auto, LOOpt_Speed, LOOpt_Spur, LOOpt_PhaseNoise

    # --- Structs ---
    # FINAL FIX: Each field must be on its own line.
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
        RxPort_TypeDef RxPort
        uint32_t BusTimeout_ms
        IQS_TriggerSource_TypeDef TriggerSource
        TriggerEdge_TypeDef TriggerEdge
        TriggerMode_TypeDef TriggerMode
        uint64_t TriggerLength
        TriggerOutMode_TypeDef TriggerOutMode
        TriggerOutPulsePolarity_TypeDef TriggerOutPulsePolarity
        double TriggerLevel_dBm
        double TriggerLevel_SafeTime
        double TriggerDelay
        double PreTriggerTime
        TriggerTimerSync_TypeDef TriggerTimerSync
        double TriggerTimer_Period
        uint8_t EnableReTrigger
        double ReTrigger_Period
        uint16_t ReTrigger_Count
        DataFormat_TypeDef DataFormat
        GainStrategy_TypeDef GainStrategy
        PreamplifierState_TypeDef Preamplifier
        uint8_t AnalogIFBWGrade
        uint8_t IFGainGrade
        uint8_t EnableDebugMode
        ReferenceClockSource_TypeDef ReferenceClockSource
        double ReferenceClockFrequency
        uint8_t EnableReferenceClockOut
        SystemClockSource_TypeDef SystemClockSource
        double ExternalSystemClockFrequency
        double NativeIQSampleRate_SPS
        uint8_t EnableIFAGC
        int8_t Atten
        DCCancelerMode_TypeDef DCCancelerMode
        QDCMode_TypeDef QDCMode
        float QDCIGain
        float QDCQGain
        float QDCPhaseComp
        int8_t DCCIOffset
        int8_t DCCQOffset
        LOOptimization_TypeDef LOOptimization

    ctypedef struct IQS_StreamInfo_TypeDef:
        double IQSampleRate
        uint32_t PacketSamples
        uint32_t PacketDataSize

    ctypedef struct IQStream_TypeDef:
        void* AlternIQStream
        IQS_StreamInfo_TypeDef IQS_StreamInfo
        float IQS_ScaleToV

    # --- Functions ---
    int Device_Open(void** Device, int DeviceNum, const BootProfile_TypeDef* BootProfile, BootInfo_TypeDef* BootInfo)
    int Device_Close(void** Device)
    int IQS_ProfileDeInit(void** Device, IQS_Profile_TypeDef* UserProfile_O)
    int IQS_Configuration(void** Device, const IQS_Profile_TypeDef* ProfileIn, IQS_Profile_TypeDef* ProfileOut, IQS_StreamInfo_TypeDef* StreamInfo)
    int IQS_BusTriggerStart(void** Device)
    int IQS_GetIQStream_PM1(void **Device, IQStream_TypeDef* IQStream)
    int IQS_BusTriggerStop(void** Device)
