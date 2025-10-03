cdef extern from "sdrplay_api.h":
    ctypedef struct sdrplay_api_DeviceT:
       char *SerNo
       char *DevNm
       unsigned char hwVer
       unsigned char devAvail

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
      sdrplay_api_Success            = 0
      sdrplay_api_Fail               = 1
      sdrplay_api_InvalidParam       = 2
      sdrplay_api_OutOfRange         = 3
      sdrplay_api_GainUpdateError    = 4
      sdrplay_api_RfUpdateError      = 5
      sdrplay_api_FsUpdateError      = 6
      sdrplay_api_HwError            = 7
      sdrplay_api_AliasingError      = 8
      sdrplay_api_AlreadyInitialised = 9
      sdrplay_api_NotInitialised     = 10
      sdrplay_api_NotEnabled         = 11
      sdrplay_api_HwVerError         = 12
      sdrplay_api_OutOfMemError      = 13

    ctypedef enum sdrplay_api_TransferModeT:
      sdrplay_api_ISOCH = 0
      sdrplay_api_BULK  = 1

    ctypedef enum sdrplay_api_ReasonForReinitT:
      sdrplay_api_CHANGE_NONE    = 0x00
      sdrplay_api_CHANGE_GR      = 0x01
      sdrplay_api_CHANGE_FS_FREQ = 0x02
      sdrplay_api_CHANGE_RF_FREQ = 0x04
      sdrplay_api_CHANGE_BW_TYPE = 0x08
      sdrplay_api_CHANGE_IF_TYPE = 0x10
      sdrplay_api_CHANGE_LO_MODE = 0x20
      sdrplay_api_CHANGE_AM_PORT = 0x40

    ctypedef enum sdrplay_api_LoModeT:
      sdrplay_api_LO_Undefined = 0
      sdrplay_api_LO_Auto      = 1
      sdrplay_api_LO_120MHz    = 2
      sdrplay_api_LO_144MHz    = 3
      sdrplay_api_LO_168MHz    = 4

    ctypedef enum sdrplay_api_BandT:
      sdrplay_api_BAND_AM_LO   = 0
      sdrplay_api_BAND_AM_MID  = 1
      sdrplay_api_BAND_AM_HI   = 2
      sdrplay_api_BAND_VHF     = 3
      sdrplay_api_BAND_3       = 4
      sdrplay_api_BAND_X       = 5
      sdrplay_api_BAND_4_5     = 6
      sdrplay_api_BAND_L       = 7

    ctypedef enum sdrplay_api_SetGrModeT:
      sdrplay_api_USE_SET_GR                = 0
      sdrplay_api_USE_SET_GR_ALT_MODE       = 1
      sdrplay_api_USE_RSP_SET_GR            = 2

    ctypedef enum sdrplay_api_RSPII_BandT:
      sdrplay_api_RSPII_BAND_UNKNOWN = 0
      sdrplay_api_RSPII_BAND_AM_LO   = 1
      sdrplay_api_RSPII_BAND_AM_MID  = 2
      sdrplay_api_RSPII_BAND_AM_HI   = 3
      sdrplay_api_RSPII_BAND_VHF     = 4
      sdrplay_api_RSPII_BAND_3       = 5
      sdrplay_api_RSPII_BAND_X_LO    = 6
      sdrplay_api_RSPII_BAND_X_MID   = 7
      sdrplay_api_RSPII_BAND_X_HI    = 8
      sdrplay_api_RSPII_BAND_4_5     = 9
      sdrplay_api_RSPII_BAND_L       = 10

    ctypedef enum sdrplay_api_RSPII_AntennaSelectT:
      sdrplay_api_RSPII_ANTENNA_A = 5
      sdrplay_api_RSPII_ANTENNA_B = 6

    ctypedef enum sdrplay_api_AgcControlT:
      sdrplay_api_AGC_DISABLE  = 0
      sdrplay_api_AGC_100HZ    = 1
      sdrplay_api_AGC_50HZ     = 2
      sdrplay_api_AGC_5HZ      = 3

    ctypedef enum sdrplay_api_GainMessageIdT:
      sdrplay_api_GAIN_MESSAGE_START_ID  = 0x80000000
      sdrplay_api_ADC_OVERLOAD_DETECTED  = sdrplay_api_GAIN_MESSAGE_START_ID + 1
      sdrplay_api_ADC_OVERLOAD_CORRECTED = sdrplay_api_GAIN_MESSAGE_START_ID + 2

    ctypedef enum sdrplay_api_MinGainReductionT:
      sdrplay_api_EXTENDED_MIN_GR = 0
      sdrplay_api_NORMAL_MIN_GR   = 20

    ctypedef struct sdrplay_api_GainValuesT:
       float curr;
       float max;
       float min;

    ctypedef void sdrplay_api_StreamCallback_t(short *xi, short *xq, unsigned int firstSampleNum, int grChanged, int rfChanged, int fsChanged, unsigned int numSamples, unsigned int reset, unsigned int hwRemoved, void *cbContext)
    ctypedef void sdrplay_api_GainChangeCallback_t(unsigned int gRdB, unsigned int lnaGRdB, void *cbContext)

    sdrplay_api_ErrT sdrplay_api_ReadPacket(short *xi, short *xq, unsigned int *firstSampleNum, int *grChanged, int *rfChanged, int *fsChanged)
    sdrplay_api_ErrT sdrplay_api_SetRf(double drfHz, int abs, int syncUpdate)
    sdrplay_api_ErrT sdrplay_api_SetFs(double dfsHz, int abs, int syncUpdate, int reCal)
    sdrplay_api_ErrT sdrplay_api_SetGr(int gRdB, int abs, int syncUpdate)
    sdrplay_api_ErrT sdrplay_api_SetGrParams(int minimumGr, int lnaGrThreshold)
    sdrplay_api_ErrT sdrplay_api_SetDcMode(int dcCal, int speedUp)
    sdrplay_api_ErrT sdrplay_api_SetDcTrackTime(int trackTime)
    sdrplay_api_ErrT sdrplay_api_SetSyncUpdateSampleNum(unsigned int sampleNum)
    sdrplay_api_ErrT sdrplay_api_SetSyncUpdatePeriod(unsigned int period)
    sdrplay_api_ErrT sdrplay_api_ApiVersion(float *version)
    sdrplay_api_ErrT sdrplay_api_ResetUpdateFlags(int resetGainUpdate, int resetRfUpdate, int resetFsUpdate)
    sdrplay_api_ErrT sdrplay_api_SetParam(unsigned int id, unsigned int value)
    sdrplay_api_ErrT sdrplay_api_SetPpm(double ppm)
    sdrplay_api_ErrT sdrplay_api_SetGrAltMode(int *gRidx, int LNAstate, int *gRdBsystem, int abs, int syncUpdate)
    sdrplay_api_ErrT sdrplay_api_DCoffsetIQimbalanceControl(unsigned int DCenable, unsigned int IQenable)
    sdrplay_api_ErrT sdrplay_api_DecimateControl(unsigned int enable, unsigned int decimationFactor, unsigned int wideBandSignal)

    sdrplay_api_ErrT sdrplay_api_StreamInit(int *gRdB, double fsMHz, double rfMHz, sdrplay_api_Bw_MHzT bwType, sdrplay_api_If_kHzT ifType, int LNAstate, int *gRdBsystem, sdrplay_api_SetGrModeT setGrMode, int *samplesPerPacket, sdrplay_api_StreamCallback_t StreamCbFn, sdrplay_api_GainChangeCallback_t GainChangeCbFn, void *cbContext)
    sdrplay_api_ErrT sdrplay_api_StreamUninit()
    sdrplay_api_ErrT sdrplay_api_Reinit(int *gRdB, double fsMHz, double rfMHz, sdrplay_api_Bw_MHzT bwType, sdrplay_api_If_kHzT ifType, sdrplay_api_LoModeT loMode, int LNAstate, int *gRdBsystem, sdrplay_api_SetGrModeT setGrMode, int *samplesPerPacket, sdrplay_api_ReasonForReinitT reasonForReinit)
    sdrplay_api_ErrT sdrplay_api_DebugEnable(unsigned int enable)

    sdrplay_api_ErrT sdrplay_api_GetDevices(sdrplay_api_DeviceT *devices, unsigned int *numDevs, unsigned int maxDevs)
    sdrplay_api_ErrT sdrplay_api_SetDeviceIdx(unsigned int idx)
    sdrplay_api_ErrT sdrplay_api_ReleaseDeviceIdx()
    sdrplay_api_ErrT sdrplay_api_GetHwVersion(unsigned char *ver)
    sdrplay_api_ErrT sdrplay_api_RSPII_AntennaControl(sdrplay_api_RSPII_AntennaSelectT select)
    sdrplay_api_ErrT sdrplay_api_RSPII_ExternalReferenceControl(unsigned int output_enable)
    sdrplay_api_ErrT sdrplay_api_RSPII_BiasTControl(unsigned int enable)
    sdrplay_api_ErrT sdrplay_api_RSPII_RfNotchEnable(unsigned int enable)

    sdrplay_api_ErrT sdrplay_api_RSP_SetGr(int gRdB, int LNAstate, int abs, int syncUpdate)
    sdrplay_api_ErrT sdrplay_api_RSP_SetGrLimits(sdrplay_api_MinGainReductionT minGr)

    sdrplay_api_ErrT sdrplay_api_AmPortSelect(int port)
