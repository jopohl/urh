cdef extern from "mirsdrapi-rsp.h":
    ctypedef struct mir_sdr_DeviceT:
       char *SerNo
       char *DevNm
       unsigned char hwVer
       unsigned char devAvail

    ctypedef enum mir_sdr_Bw_MHzT:
      mir_sdr_BW_Undefined = 0
      mir_sdr_BW_0_200     = 200
      mir_sdr_BW_0_300     = 300
      mir_sdr_BW_0_600     = 600
      mir_sdr_BW_1_536     = 1536
      mir_sdr_BW_5_000     = 5000
      mir_sdr_BW_6_000     = 6000
      mir_sdr_BW_7_000     = 7000
      mir_sdr_BW_8_000     = 8000

    ctypedef enum mir_sdr_If_kHzT:
      mir_sdr_IF_Undefined = -1
      mir_sdr_IF_Zero      = 0
      mir_sdr_IF_0_450     = 450
      mir_sdr_IF_1_620     = 1620
      mir_sdr_IF_2_048     = 2048

    ctypedef enum mir_sdr_ErrT:
      mir_sdr_Success            = 0
      mir_sdr_Fail               = 1
      mir_sdr_InvalidParam       = 2
      mir_sdr_OutOfRange         = 3
      mir_sdr_GainUpdateError    = 4
      mir_sdr_RfUpdateError      = 5
      mir_sdr_FsUpdateError      = 6
      mir_sdr_HwError            = 7
      mir_sdr_AliasingError      = 8
      mir_sdr_AlreadyInitialised = 9
      mir_sdr_NotInitialised     = 10
      mir_sdr_NotEnabled         = 11
      mir_sdr_HwVerError         = 12
      mir_sdr_OutOfMemError      = 13

    ctypedef enum mir_sdr_TransferModeT:
      mir_sdr_ISOCH = 0
      mir_sdr_BULK  = 1

    ctypedef enum mir_sdr_ReasonForReinitT:
      mir_sdr_CHANGE_NONE    = 0x00
      mir_sdr_CHANGE_GR      = 0x01
      mir_sdr_CHANGE_FS_FREQ = 0x02
      mir_sdr_CHANGE_RF_FREQ = 0x04
      mir_sdr_CHANGE_BW_TYPE = 0x08
      mir_sdr_CHANGE_IF_TYPE = 0x10
      mir_sdr_CHANGE_LO_MODE = 0x20
      mir_sdr_CHANGE_AM_PORT = 0x40

    ctypedef enum mir_sdr_LoModeT:
      mir_sdr_LO_Undefined = 0
      mir_sdr_LO_Auto      = 1
      mir_sdr_LO_120MHz    = 2
      mir_sdr_LO_144MHz    = 3
      mir_sdr_LO_168MHz    = 4

    ctypedef enum mir_sdr_BandT:
      mir_sdr_BAND_AM_LO   = 0
      mir_sdr_BAND_AM_MID  = 1
      mir_sdr_BAND_AM_HI   = 2
      mir_sdr_BAND_VHF     = 3
      mir_sdr_BAND_3       = 4
      mir_sdr_BAND_X       = 5
      mir_sdr_BAND_4_5     = 6
      mir_sdr_BAND_L       = 7

    ctypedef enum mir_sdr_SetGrModeT:
      mir_sdr_USE_SET_GR                = 0
      mir_sdr_USE_SET_GR_ALT_MODE       = 1
      mir_sdr_USE_RSP_SET_GR            = 2

    ctypedef enum mir_sdr_RSPII_BandT:
      mir_sdr_RSPII_BAND_UNKNOWN = 0
      mir_sdr_RSPII_BAND_AM_LO   = 1
      mir_sdr_RSPII_BAND_AM_MID  = 2
      mir_sdr_RSPII_BAND_AM_HI   = 3
      mir_sdr_RSPII_BAND_VHF     = 4
      mir_sdr_RSPII_BAND_3       = 5
      mir_sdr_RSPII_BAND_X_LO    = 6
      mir_sdr_RSPII_BAND_X_MID   = 7
      mir_sdr_RSPII_BAND_X_HI    = 8
      mir_sdr_RSPII_BAND_4_5     = 9
      mir_sdr_RSPII_BAND_L       = 10

    ctypedef enum mir_sdr_RSPII_AntennaSelectT:
      mir_sdr_RSPII_ANTENNA_A = 5
      mir_sdr_RSPII_ANTENNA_B = 6

    ctypedef enum mir_sdr_AgcControlT:
      mir_sdr_AGC_DISABLE  = 0
      mir_sdr_AGC_100HZ    = 1
      mir_sdr_AGC_50HZ     = 2
      mir_sdr_AGC_5HZ      = 3

    ctypedef enum mir_sdr_GainMessageIdT:
      mir_sdr_GAIN_MESSAGE_START_ID  = 0x80000000
      mir_sdr_ADC_OVERLOAD_DETECTED  = mir_sdr_GAIN_MESSAGE_START_ID + 1
      mir_sdr_ADC_OVERLOAD_CORRECTED = mir_sdr_GAIN_MESSAGE_START_ID + 2

    ctypedef enum mir_sdr_MinGainReductionT:
      mir_sdr_EXTENDED_MIN_GR = 0
      mir_sdr_NORMAL_MIN_GR   = 20

    ctypedef struct mir_sdr_GainValuesT:
       float curr;
       float max;
       float min;

    ctypedef void mir_sdr_StreamCallback_t(short *xi, short *xq, unsigned int firstSampleNum, int grChanged, int rfChanged, int fsChanged, unsigned int numSamples, unsigned int reset, unsigned int hwRemoved, void *cbContext)
    ctypedef void mir_sdr_GainChangeCallback_t(unsigned int gRdB, unsigned int lnaGRdB, void *cbContext)

    mir_sdr_ErrT mir_sdr_ReadPacket(short *xi, short *xq, unsigned int *firstSampleNum, int *grChanged, int *rfChanged, int *fsChanged)
    mir_sdr_ErrT mir_sdr_SetRf(double drfHz, int abs, int syncUpdate)
    mir_sdr_ErrT mir_sdr_SetFs(double dfsHz, int abs, int syncUpdate, int reCal)
    mir_sdr_ErrT mir_sdr_SetGr(int gRdB, int abs, int syncUpdate)
    mir_sdr_ErrT mir_sdr_SetGrParams(int minimumGr, int lnaGrThreshold)
    mir_sdr_ErrT mir_sdr_SetDcMode(int dcCal, int speedUp)
    mir_sdr_ErrT mir_sdr_SetDcTrackTime(int trackTime)
    mir_sdr_ErrT mir_sdr_SetSyncUpdateSampleNum(unsigned int sampleNum)
    mir_sdr_ErrT mir_sdr_SetSyncUpdatePeriod(unsigned int period)
    mir_sdr_ErrT mir_sdr_ApiVersion(float *version)
    mir_sdr_ErrT mir_sdr_ResetUpdateFlags(int resetGainUpdate, int resetRfUpdate, int resetFsUpdate)
    mir_sdr_ErrT mir_sdr_SetParam(unsigned int id, unsigned int value)
    mir_sdr_ErrT mir_sdr_SetPpm(double ppm)
    mir_sdr_ErrT mir_sdr_SetGrAltMode(int *gRidx, int LNAstate, int *gRdBsystem, int abs, int syncUpdate)
    mir_sdr_ErrT mir_sdr_DCoffsetIQimbalanceControl(unsigned int DCenable, unsigned int IQenable)
    mir_sdr_ErrT mir_sdr_DecimateControl(unsigned int enable, unsigned int decimationFactor, unsigned int wideBandSignal)

    mir_sdr_ErrT mir_sdr_StreamInit(int *gRdB, double fsMHz, double rfMHz, mir_sdr_Bw_MHzT bwType, mir_sdr_If_kHzT ifType, int LNAstate, int *gRdBsystem, mir_sdr_SetGrModeT setGrMode, int *samplesPerPacket, mir_sdr_StreamCallback_t StreamCbFn, mir_sdr_GainChangeCallback_t GainChangeCbFn, void *cbContext)
    mir_sdr_ErrT mir_sdr_StreamUninit()
    mir_sdr_ErrT mir_sdr_Reinit(int *gRdB, double fsMHz, double rfMHz, mir_sdr_Bw_MHzT bwType, mir_sdr_If_kHzT ifType, mir_sdr_LoModeT loMode, int LNAstate, int *gRdBsystem, mir_sdr_SetGrModeT setGrMode, int *samplesPerPacket, mir_sdr_ReasonForReinitT reasonForReinit)
    mir_sdr_ErrT mir_sdr_DebugEnable(unsigned int enable)

    mir_sdr_ErrT mir_sdr_GetDevices(mir_sdr_DeviceT *devices, unsigned int *numDevs, unsigned int maxDevs)
    mir_sdr_ErrT mir_sdr_SetDeviceIdx(unsigned int idx)
    mir_sdr_ErrT mir_sdr_ReleaseDeviceIdx()
    mir_sdr_ErrT mir_sdr_GetHwVersion(unsigned char *ver)
    mir_sdr_ErrT mir_sdr_RSPII_AntennaControl(mir_sdr_RSPII_AntennaSelectT select)
    mir_sdr_ErrT mir_sdr_RSPII_ExternalReferenceControl(unsigned int output_enable)
    mir_sdr_ErrT mir_sdr_RSPII_BiasTControl(unsigned int enable)
    mir_sdr_ErrT mir_sdr_RSPII_RfNotchEnable(unsigned int enable)

    mir_sdr_ErrT mir_sdr_RSP_SetGr(int gRdB, int LNAstate, int abs, int syncUpdate)
    mir_sdr_ErrT mir_sdr_RSP_SetGrLimits(mir_sdr_MinGainReductionT minGr)

    mir_sdr_ErrT mir_sdr_AmPortSelect(int port)
