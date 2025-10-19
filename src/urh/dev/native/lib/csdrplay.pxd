cdef extern from "sdrplay_api.h":
    ctypedef void* HANDLE

    ctypedef enum sdrplay_api_TunerSelectT:
      sdrplay_api_Tuner_Neither = 0
      sdrplay_api_Tuner_A       = 1
      sdrplay_api_Tuner_B       = 2
      sdrplay_api_Tuner_Both    = 3

    ctypedef enum sdrplay_api_Rsp2_AntennaSelectT:
      sdrplay_api_Rsp2_ANTENNA_A = 5
      sdrplay_api_Rsp2_ANTENNA_B = 6

    ctypedef enum sdrplay_api_Rsp2_AmPortSelectT:
      sdrplay_api_Rsp2_AMPORT_1 = 1
      sdrplay_api_Rsp2_AMPORT_2 = 0

    ctypedef enum sdrplay_api_ReasonForUpdateT:
      sdrplay_api_Update_None                        = 0x00000000

      # Reasons for master only mode
      sdrplay_api_Update_Dev_Fs                      = 0x00000001
      sdrplay_api_Update_Dev_Ppm                     = 0x00000002
      sdrplay_api_Update_Dev_SyncUpdate              = 0x00000004
      sdrplay_api_Update_Dev_ResetFlags              = 0x00000008

      sdrplay_api_Update_Rsp1a_BiasTControl          = 0x00000010
      sdrplay_api_Update_Rsp1a_RfNotchControl        = 0x00000020
      sdrplay_api_Update_Rsp1a_RfDabNotchControl     = 0x00000040

      sdrplay_api_Update_Rsp2_BiasTControl           = 0x00000080
      sdrplay_api_Update_Rsp2_AmPortSelect           = 0x00000100
      sdrplay_api_Update_Rsp2_AntennaControl         = 0x00000200
      sdrplay_api_Update_Rsp2_RfNotchControl         = 0x00000400
      sdrplay_api_Update_Rsp2_ExtRefControl          = 0x00000800

      sdrplay_api_Update_RspDuo_ExtRefControl        = 0x00001000

      sdrplay_api_Update_Master_Spare_1              = 0x00002000
      sdrplay_api_Update_Master_Spare_2              = 0x00004000

      # Reasons for master and slave mode
      # Note: sdrplay_api_Update_Tuner_Gr MUST be the first value defined in this section!
      sdrplay_api_Update_Tuner_Gr                    = 0x00008000
      sdrplay_api_Update_Tuner_GrLimits              = 0x00010000
      sdrplay_api_Update_Tuner_Frf                   = 0x00020000
      sdrplay_api_Update_Tuner_BwType                = 0x00040000
      sdrplay_api_Update_Tuner_IfType                = 0x00080000
      sdrplay_api_Update_Tuner_DcOffset              = 0x00100000
      sdrplay_api_Update_Tuner_LoMode                = 0x00200000

      sdrplay_api_Update_Ctrl_DCoffsetIQimbalance    = 0x00400000
      sdrplay_api_Update_Ctrl_Decimation             = 0x00800000
      sdrplay_api_Update_Ctrl_Agc                    = 0x01000000
      sdrplay_api_Update_Ctrl_AdsbMode               = 0x02000000
      sdrplay_api_Update_Ctrl_OverloadMsgAck         = 0x04000000

      sdrplay_api_Update_RspDuo_BiasTControl         = 0x08000000
      sdrplay_api_Update_RspDuo_AmPortSelect         = 0x10000000
      sdrplay_api_Update_RspDuo_Tuner1AmNotchControl = 0x20000000
      sdrplay_api_Update_RspDuo_RfNotchControl       = 0x40000000
      sdrplay_api_Update_RspDuo_RfDabNotchControl    = 0x80000000

    ctypedef enum sdrplay_api_MinGainReductionT:
      sdrplay_api_EXTENDED_MIN_GR = 0
      sdrplay_api_NORMAL_MIN_GR   = 20

    ctypedef struct sdrplay_api_GainValuesT:
      float curr
      float max
      float min

    ctypedef struct sdrplay_api_GainT:
      int gRdB
      unsigned char LNAstate
      unsigned char syncUpdate
      sdrplay_api_MinGainReductionT minGr
      sdrplay_api_GainValuesT gainVals

    ctypedef struct sdrplay_api_RfFreqT:
      double rfHz
      unsigned char syncUpdate

    ctypedef struct sdrplay_api_DcOffsetTunerT:
      unsigned char dcCal
      unsigned char speedUp
      int trackTime
      int refreshRateTime

    ctypedef struct sdrplay_api_TunerParamsT:
      sdrplay_api_Bw_MHzT        bwType
      sdrplay_api_If_kHzT        ifType
      sdrplay_api_LoModeT        loMode
      sdrplay_api_GainT          gain
      sdrplay_api_RfFreqT        rfFreq
      sdrplay_api_DcOffsetTunerT dcOffsetTuner

    ctypedef struct sdrplay_api_AgcT:
      sdrplay_api_AgcControlT enable
      int setPoint_dBfs
      unsigned short attack_ms
      unsigned short decay_ms
      unsigned short decay_delay_ms
      unsigned short decay_threshold_dB
      int syncUpdate

    ctypedef enum sdrplay_api_AdsbModeT:
      sdrplay_api_ADSB_DECIMATION                  = 0
      sdrplay_api_ADSB_NO_DECIMATION_LOWPASS       = 1
      sdrplay_api_ADSB_NO_DECIMATION_BANDPASS_2MHZ = 2
      sdrplay_api_ADSB_NO_DECIMATION_BANDPASS_3MHZ = 3

    ctypedef struct sdrplay_api_DecimationT:
      unsigned char enable
      unsigned char decimationFactor
      unsigned char wideBandSignal

    ctypedef struct sdrplay_api_DcOffsetT:
      unsigned char DCenable
      unsigned char IQenable

    ctypedef struct sdrplay_api_ControlParamsT:
      sdrplay_api_DcOffsetT dcOffset
      sdrplay_api_DecimationT decimation
      sdrplay_api_AgcT agc
      sdrplay_api_AdsbModeT adsbMode

    ctypedef struct sdrplay_api_Rsp1aTunerParamsT:
      unsigned char biasTEnable

    ctypedef struct sdrplay_api_Rsp2TunerParamsT:
      unsigned char biasTEnable
      sdrplay_api_Rsp2_AmPortSelectT amPortSel
      sdrplay_api_Rsp2_AntennaSelectT antennaSel
      unsigned char rfNotchEnable

    ctypedef struct sdrplay_api_RspDuo_ResetSlaveFlagsT:
      unsigned char resetGainUpdate
      unsigned char resetRfUpdate

    ctypedef enum sdrplay_api_RspDuo_AmPortSelectT:
      sdrplay_api_RspDuo_AMPORT_1 = 1
      sdrplay_api_RspDuo_AMPORT_2 = 0

    ctypedef struct sdrplay_api_RspDuoTunerParamsT:
      unsigned char biasTEnable
      sdrplay_api_RspDuo_AmPortSelectT tuner1AmPortSel
      unsigned char tuner1AmNotchEnable
      unsigned char rfNotchEnable
      unsigned char rfDabNotchEnable
      sdrplay_api_RspDuo_ResetSlaveFlagsT resetSlaveFlags

    ctypedef enum sdrplay_api_RspDx_HdrModeBwT:
      sdrplay_api_RspDx_HDRMODE_BW_0_200 = 0
      sdrplay_api_RspDx_HDRMODE_BW_0_500 = 1
      sdrplay_api_RspDx_HDRMODE_BW_1_200 = 2
      sdrplay_api_RspDx_HDRMODE_BW_1_700 = 3

    ctypedef struct sdrplay_api_RspDxTunerParamsT:
      sdrplay_api_RspDx_HdrModeBwT hdrBw

    ctypedef struct sdrplay_api_RxChannelParamsT:
      sdrplay_api_TunerParamsT        tunerParams
      sdrplay_api_ControlParamsT      ctrlParams
      sdrplay_api_Rsp1aTunerParamsT   rsp1aTunerParams
      sdrplay_api_Rsp2TunerParamsT    rsp2TunerParams
      sdrplay_api_RspDuoTunerParamsT  rspDuoTunerParams
      sdrplay_api_RspDxTunerParamsT   rspDxTunerParams

    ctypedef struct sdrplay_api_FsFreqT:
      double fsHz
      unsigned char syncUpdate
      unsigned char reCal

    ctypedef struct sdrplay_api_SyncUpdateT:
      unsigned int sampleNum
      unsigned int period

    ctypedef struct sdrplay_api_ResetFlagsT:
      unsigned char resetGainUpdate
      unsigned char resetRfUpdate
      unsigned char resetFsUpdate

    ctypedef enum sdrplay_api_TransferModeT:
      sdrplay_api_ISOCH = 0
      sdrplay_api_BULK  = 1

    ctypedef struct sdrplay_api_Rsp1aParamsT:
      unsigned char rfNotchEnable
      unsigned char rfDabNotchEnable

    ctypedef struct sdrplay_api_Rsp2ParamsT:
      unsigned char extRefOutputEn

    ctypedef struct sdrplay_api_RspDuoParamsT:
      int extRefOutputEn

    ctypedef enum sdrplay_api_RspDx_AntennaSelectT:
      sdrplay_api_RspDx_ANTENNA_A = 0
      sdrplay_api_RspDx_ANTENNA_B = 1
      sdrplay_api_RspDx_ANTENNA_C = 2

    ctypedef struct sdrplay_api_RspDxParamsT:
      unsigned char hdrEnable
      unsigned char biasTEnable
      sdrplay_api_RspDx_AntennaSelectT antennaSel
      unsigned char rfNotchEnable
      unsigned char rfDabNotchEnable

    ctypedef struct sdrplay_api_DevParamsT:
      double ppm
      sdrplay_api_FsFreqT fsFreq
      sdrplay_api_SyncUpdateT syncUpdate
      sdrplay_api_ResetFlagsT resetFlags
      sdrplay_api_TransferModeT mode
      unsigned int samplesPerPkt
      sdrplay_api_Rsp1aParamsT rsp1aParams
      sdrplay_api_Rsp2ParamsT rsp2Params
      sdrplay_api_RspDuoParamsT rspDuoParams
      sdrplay_api_RspDxParamsT rspDxParams

    ctypedef struct sdrplay_api_DeviceParamsT:
      sdrplay_api_DevParamsT*       devParams
      sdrplay_api_RxChannelParamsT* rxChannelA
      sdrplay_api_RxChannelParamsT* rxChannelB

    ctypedef enum sdrplay_api_ReasonForUpdateExtension1T:
      sdrplay_api_Update_Ext1_None                   = 0x00000000

      # Reasons for master only mode
      sdrplay_api_Update_RspDx_HdrEnable             = 0x00000001
      sdrplay_api_Update_RspDx_BiasTControl          = 0x00000002
      sdrplay_api_Update_RspDx_AntennaControl        = 0x00000004
      sdrplay_api_Update_RspDx_RfNotchControl        = 0x00000008
      sdrplay_api_Update_RspDx_RfDabNotchControl     = 0x00000010
      sdrplay_api_Update_RspDx_HdrBw                 = 0x00000020
      sdrplay_api_Update_RspDuo_ResetSlaveFlags      = 0x00000040

    ctypedef enum sdrplay_api_RspDuoModeT:
      sdrplay_api_RspDuoMode_Unknown      = 0
      sdrplay_api_RspDuoMode_Single_Tuner = 1
      sdrplay_api_RspDuoMode_Dual_Tuner   = 2
      sdrplay_api_RspDuoMode_Master       = 4
      sdrplay_api_RspDuoMode_Slave        = 8

    ctypedef struct sdrplay_api_DeviceT:
      char SerNo[64]
      unsigned char hwVer
      sdrplay_api_TunerSelectT tuner
      sdrplay_api_RspDuoModeT rspDuoMode
      unsigned char valid
      double rspDuoSampleFreq
      HANDLE dev

    ctypedef enum sdrplay_api_Bw_MHzT:
      sdrplay_api_BW_Undefined = 0
      sdrplay_api_BW_0_200     = 200
      sdrplay_api_BW_0_300     = 300
      sdrplay_api_BW_0_600     = 600
      sdrplay_api_BW_1_536     = 1536
      sdrplay_api_BW_5_000     = 5000
      sdrplay_api_BW_6_000     = 6000
      sdrplay_api_BW_7_000     = 7000
      sdrplay_api_BW_8_000     = 8000

    ctypedef enum sdrplay_api_If_kHzT:
      sdrplay_api_IF_Undefined = -1
      sdrplay_api_IF_Zero      = 0
      sdrplay_api_IF_0_450     = 450
      sdrplay_api_IF_1_620     = 1620
      sdrplay_api_IF_2_048     = 2048

    ctypedef enum sdrplay_api_ErrT:
      sdrplay_api_Success               = 0
      sdrplay_api_Fail                  = 1
      sdrplay_api_InvalidParam          = 2
      sdrplay_api_OutOfRange            = 3
      sdrplay_api_GainUpdateError       = 4
      sdrplay_api_RfUpdateError         = 5
      sdrplay_api_FsUpdateError         = 6
      sdrplay_api_HwError               = 7
      sdrplay_api_AliasingError         = 8
      sdrplay_api_AlreadyInitialised    = 9
      sdrplay_api_NotInitialised        = 10
      sdrplay_api_NotEnabled            = 11
      sdrplay_api_HwVerError            = 12
      sdrplay_api_OutOfMemError         = 13
      sdrplay_api_ServiceNotResponding  = 14
      sdrplay_api_StartPending          = 15
      sdrplay_api_StopPending           = 16
      sdrplay_api_InvalidMode           = 17
      sdrplay_api_FailedVerification1   = 18
      sdrplay_api_FailedVerification2   = 19
      sdrplay_api_FailedVerification3   = 20
      sdrplay_api_FailedVerification4   = 21
      sdrplay_api_FailedVerification5   = 22
      sdrplay_api_FailedVerification6   = 23
      sdrplay_api_InvalidServiceVersion = 24

    ctypedef enum sdrplay_api_LoModeT:
      sdrplay_api_LO_Undefined = 0
      sdrplay_api_LO_Auto      = 1
      sdrplay_api_LO_120MHz    = 2
      sdrplay_api_LO_144MHz    = 3
      sdrplay_api_LO_168MHz    = 4

    ctypedef enum sdrplay_api_AgcControlT:
      sdrplay_api_AGC_DISABLE  = 0
      sdrplay_api_AGC_100HZ    = 1
      sdrplay_api_AGC_50HZ     = 2
      sdrplay_api_AGC_5HZ      = 3
      sdrplay_api_AGC_CTRL_EN  = 4

    ctypedef struct sdrplay_api_StreamCbParamsT:
      unsigned int firstSampleNum
      int          grChanged
      int          rfChanged
      int          fsChanged
      unsigned int numSamples

    ctypedef enum sdrplay_api_EventT:
      sdrplay_api_GainChange            = 0
      sdrplay_api_PowerOverloadChange   = 1
      sdrplay_api_DeviceRemoved         = 2
      sdrplay_api_RspDuoModeChange      = 3
      sdrplay_api_DeviceFailure         = 4

    ctypedef struct sdrplay_api_GainCbParamT:
      unsigned int gRdB
      unsigned int lnaGRdB
      double currGain

    ctypedef enum sdrplay_api_PowerOverloadCbEventIdT:
      sdrplay_api_Overload_Detected  = 0
      sdrplay_api_Overload_Corrected = 1

    ctypedef struct sdrplay_api_PowerOverloadCbParamT:
      sdrplay_api_PowerOverloadCbEventIdT powerOverloadChangeType

    ctypedef enum sdrplay_api_RspDuoModeCbEventIdT:
      sdrplay_api_MasterInitialised      = 0
      sdrplay_api_SlaveAttached          = 1
      sdrplay_api_SlaveDetached          = 2
      sdrplay_api_SlaveInitialised       = 3
      sdrplay_api_SlaveUninitialised     = 4
      sdrplay_api_MasterDllDisappeared   = 5
      sdrplay_api_SlaveDllDisappeared    = 6

    ctypedef struct sdrplay_api_RspDuoModeCbParamT:
      sdrplay_api_RspDuoModeCbEventIdT modeChangeType

    ctypedef union sdrplay_api_EventParamsT:
      sdrplay_api_GainCbParamT          gainParams
      sdrplay_api_PowerOverloadCbParamT powerOverloadParams
      sdrplay_api_RspDuoModeCbParamT    rspDuoModeParams

    ctypedef void (*sdrplay_api_StreamCallback_t)(short *xi,
                                                  short *xq,
                                                  sdrplay_api_StreamCbParamsT *params,
                                                  unsigned int numSamples,
                                                  unsigned int reset,
                                                  void *cbContext)
    ctypedef void (*sdrplay_api_EventCallback_t)(sdrplay_api_EventT eventId,
                                                 sdrplay_api_TunerSelectT tuner,
                                                 sdrplay_api_EventParamsT* params,
                                                 void *cbContext)

    ctypedef struct sdrplay_api_CallbackFnsT:
      sdrplay_api_StreamCallback_t StreamACbFn
      sdrplay_api_StreamCallback_t StreamBCbFn
      sdrplay_api_EventCallback_t  EventCbFn

    sdrplay_api_ErrT sdrplay_api_Open() nogil
    sdrplay_api_ErrT sdrplay_api_Close() nogil
    sdrplay_api_ErrT sdrplay_api_ApiVersion(float *version) nogil
    sdrplay_api_ErrT sdrplay_api_SelectDevice(sdrplay_api_DeviceT *device) nogil
    sdrplay_api_ErrT sdrplay_api_ReleaseDevice(sdrplay_api_DeviceT *device) nogil
    sdrplay_api_ErrT sdrplay_api_Init(HANDLE dev, sdrplay_api_CallbackFnsT *callbackFns, void *cbContext) nogil
    sdrplay_api_ErrT sdrplay_api_Uninit(HANDLE dev) nogil
    sdrplay_api_ErrT sdrplay_api_GetDeviceParams(HANDLE dev,
                                                 sdrplay_api_DeviceParamsT **deviceParams) nogil
    sdrplay_api_ErrT sdrplay_api_GetDevices(sdrplay_api_DeviceT *devices, unsigned int *numDevs, unsigned int maxDevs) nogil
    sdrplay_api_ErrT sdrplay_api_Update(HANDLE dev, sdrplay_api_TunerSelectT tuner,
                                        sdrplay_api_ReasonForUpdateT reasonForUpdate, sdrplay_api_ReasonForUpdateExtension1T reasonForUpdateExt1) nogil
