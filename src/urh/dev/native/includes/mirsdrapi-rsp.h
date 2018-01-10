//
// Copyright (c) 2013 Mirics Ltd, All Rights Reserved
//

#ifndef MIR_SDR_H
#define MIR_SDR_H

#ifndef _MIR_SDR_QUALIFIER
#if !defined(STATIC_LIB) && (defined(_M_X64) || defined(_M_IX86)) 
#define _MIR_SDR_QUALIFIER __declspec(dllimport)
#elif defined(STATIC_LIB) || defined(__GNUC__) 
#define _MIR_SDR_QUALIFIER
#endif
#endif  // _MIR_SDR_QUALIFIER

// Application code should check that it is compiled against the same API version
// mir_sdr_ApiVersion() returns the API version 
#define MIR_SDR_API_VERSION   (float)(2.10)

#if defined(ANDROID) || defined(__ANDROID__)
// Android requires a mechanism to request info from Java application
typedef enum
{
  mir_sdr_GetFd              = 0,
  mir_sdr_FreeFd             = 1,
  mir_sdr_DevNotFound        = 2,
  mir_sdr_DevRemoved         = 3
} mir_sdr_JavaReqT;

typedef int (*mir_sdr_SendJavaReq_t)(mir_sdr_JavaReqT cmd, int param);
#endif

typedef enum
{
  mir_sdr_Success            = 0,
  mir_sdr_Fail               = 1,
  mir_sdr_InvalidParam       = 2,
  mir_sdr_OutOfRange         = 3,
  mir_sdr_GainUpdateError    = 4,
  mir_sdr_RfUpdateError      = 5,
  mir_sdr_FsUpdateError      = 6,
  mir_sdr_HwError            = 7,
  mir_sdr_AliasingError      = 8,
  mir_sdr_AlreadyInitialised = 9,
  mir_sdr_NotInitialised     = 10,
  mir_sdr_NotEnabled         = 11,
  mir_sdr_HwVerError         = 12,
  mir_sdr_OutOfMemError      = 13
} mir_sdr_ErrT;

typedef enum
{
  mir_sdr_BW_Undefined = 0,
  mir_sdr_BW_0_200     = 200,
  mir_sdr_BW_0_300     = 300,
  mir_sdr_BW_0_600     = 600,
  mir_sdr_BW_1_536     = 1536,
  mir_sdr_BW_5_000     = 5000,
  mir_sdr_BW_6_000     = 6000,
  mir_sdr_BW_7_000     = 7000,
  mir_sdr_BW_8_000     = 8000
} mir_sdr_Bw_MHzT;

typedef enum
{
  mir_sdr_IF_Undefined = -1,
  mir_sdr_IF_Zero      = 0,
  mir_sdr_IF_0_450     = 450,
  mir_sdr_IF_1_620     = 1620,
  mir_sdr_IF_2_048     = 2048
} mir_sdr_If_kHzT;

typedef enum
{
  mir_sdr_ISOCH = 0,
  mir_sdr_BULK  = 1
} mir_sdr_TransferModeT;

typedef enum
{
  mir_sdr_CHANGE_NONE    = 0x00,
  mir_sdr_CHANGE_GR      = 0x01,
  mir_sdr_CHANGE_FS_FREQ = 0x02,
  mir_sdr_CHANGE_RF_FREQ = 0x04,
  mir_sdr_CHANGE_BW_TYPE = 0x08,
  mir_sdr_CHANGE_IF_TYPE = 0x10,
  mir_sdr_CHANGE_LO_MODE = 0x20,
  mir_sdr_CHANGE_AM_PORT = 0x40
} mir_sdr_ReasonForReinitT;

typedef enum
{
  mir_sdr_LO_Undefined = 0,
  mir_sdr_LO_Auto      = 1,
  mir_sdr_LO_120MHz    = 2,
  mir_sdr_LO_144MHz    = 3,
  mir_sdr_LO_168MHz    = 4
} mir_sdr_LoModeT;

typedef enum
{
  mir_sdr_BAND_AM_LO   = 0,
  mir_sdr_BAND_AM_MID  = 1,
  mir_sdr_BAND_AM_HI   = 2,
  mir_sdr_BAND_VHF     = 3,
  mir_sdr_BAND_3       = 4,
  mir_sdr_BAND_X       = 5,
  mir_sdr_BAND_4_5     = 6,
  mir_sdr_BAND_L       = 7
} mir_sdr_BandT;

typedef enum
{
  mir_sdr_USE_SET_GR                = 0,
  mir_sdr_USE_SET_GR_ALT_MODE       = 1,
  mir_sdr_USE_RSP_SET_GR            = 2
} mir_sdr_SetGrModeT;

typedef enum
{
  mir_sdr_RSPII_BAND_UNKNOWN = 0,
  mir_sdr_RSPII_BAND_AM_LO   = 1,
  mir_sdr_RSPII_BAND_AM_MID  = 2,
  mir_sdr_RSPII_BAND_AM_HI   = 3,
  mir_sdr_RSPII_BAND_VHF     = 4,
  mir_sdr_RSPII_BAND_3       = 5,
  mir_sdr_RSPII_BAND_X_LO    = 6,
  mir_sdr_RSPII_BAND_X_MID   = 7,
  mir_sdr_RSPII_BAND_X_HI    = 8,
  mir_sdr_RSPII_BAND_4_5     = 9,
  mir_sdr_RSPII_BAND_L       = 10
} mir_sdr_RSPII_BandT;

typedef enum
{
  mir_sdr_RSPII_ANTENNA_A = 5,
  mir_sdr_RSPII_ANTENNA_B = 6
} mir_sdr_RSPII_AntennaSelectT;

typedef enum
{
  mir_sdr_AGC_DISABLE  = 0,
  mir_sdr_AGC_100HZ    = 1,
  mir_sdr_AGC_50HZ     = 2,
  mir_sdr_AGC_5HZ      = 3
} mir_sdr_AgcControlT;

typedef enum
{
  mir_sdr_GAIN_MESSAGE_START_ID  = 0x80000000,
  mir_sdr_ADC_OVERLOAD_DETECTED  = mir_sdr_GAIN_MESSAGE_START_ID + 1,
  mir_sdr_ADC_OVERLOAD_CORRECTED = mir_sdr_GAIN_MESSAGE_START_ID + 2
} mir_sdr_GainMessageIdT;

typedef enum
{
  mir_sdr_EXTENDED_MIN_GR = 0,
  mir_sdr_NORMAL_MIN_GR   = 20
} mir_sdr_MinGainReductionT;

typedef struct 
{
   char *SerNo;
   char *DevNm;
   unsigned char hwVer;
   unsigned char devAvail;
} mir_sdr_DeviceT;

typedef struct
{
   float curr;
   float max;
   float min;
} mir_sdr_GainValuesT;

// mir_sdr_StreamInit() callback function prototypes
typedef void (*mir_sdr_StreamCallback_t)(short *xi, short *xq, unsigned int firstSampleNum, int grChanged, int rfChanged, int fsChanged, unsigned int numSamples, unsigned int reset, void *cbContext); 
typedef void (*mir_sdr_GainChangeCallback_t)(unsigned int gRdB, unsigned int lnaGRdB, void *cbContext); 

typedef mir_sdr_ErrT (*mir_sdr_Init_t)(int gRdB, double fsMHz, double rfMHz, mir_sdr_Bw_MHzT bwType, mir_sdr_If_kHzT ifType, int *samplesPerPacket);
typedef mir_sdr_ErrT (*mir_sdr_Uninit_t)(void);
typedef mir_sdr_ErrT (*mir_sdr_ReadPacket_t)(short *xi, short *xq, unsigned int *firstSampleNum, int *grChanged, int *rfChanged, int *fsChanged);
typedef mir_sdr_ErrT (*mir_sdr_SetRf_t)(double drfHz, int abs, int syncUpdate);
typedef mir_sdr_ErrT (*mir_sdr_SetFs_t)(double dfsHz, int abs, int syncUpdate, int reCal);
typedef mir_sdr_ErrT (*mir_sdr_SetGr_t)(int gRdB, int abs, int syncUpdate);
typedef mir_sdr_ErrT (*mir_sdr_SetGrParams_t)(int minimumGr, int lnaGrThreshold);
typedef mir_sdr_ErrT (*mir_sdr_SetDcMode_t)(int dcCal, int speedUp);
typedef mir_sdr_ErrT (*mir_sdr_SetDcTrackTime_t)(int trackTime);
typedef mir_sdr_ErrT (*mir_sdr_SetSyncUpdateSampleNum_t)(unsigned int sampleNum);
typedef mir_sdr_ErrT (*mir_sdr_SetSyncUpdatePeriod_t)(unsigned int period);
typedef mir_sdr_ErrT (*mir_sdr_ApiVersion_t)(float *version);   
typedef mir_sdr_ErrT (*mir_sdr_ResetUpdateFlags_t)(int resetGainUpdate, int resetRfUpdate, int resetFsUpdate);   
#if defined(ANDROID) || defined(__ANDROID__)
typedef mir_sdr_ErrT (*mir_sdr_SetJavaReqCallback_t)(mir_sdr_SendJavaReq_t sendJavaReq);   
#endif
typedef mir_sdr_ErrT (*mir_sdr_SetTransferMode_t)(mir_sdr_TransferModeT mode);
typedef mir_sdr_ErrT (*mir_sdr_DownConvert_t)(short *in, short *xi, short *xq, unsigned int samplesPerPacket, mir_sdr_If_kHzT ifType, unsigned int M, unsigned int preReset);
typedef mir_sdr_ErrT (*mir_sdr_SetParam_t)(unsigned int id, unsigned int value);   
typedef mir_sdr_ErrT (*mir_sdr_SetPpm_t)(double ppm);   
typedef mir_sdr_ErrT (*mir_sdr_SetLoMode_t)(mir_sdr_LoModeT loMode);                   
typedef mir_sdr_ErrT (*mir_sdr_SetGrAltMode_t)(int *gRidx, int LNAstate, int *gRdBsystem, int abs, int syncUpdate);
typedef mir_sdr_ErrT (*mir_sdr_DCoffsetIQimbalanceControl_t)(unsigned int DCenable, unsigned int IQenable);   
typedef mir_sdr_ErrT (*mir_sdr_DecimateControl_t)(unsigned int enable, unsigned int decimationFactor, unsigned int wideBandSignal); 
typedef mir_sdr_ErrT (*mir_sdr_AgcControl_t)(mir_sdr_AgcControlT enable, int setPoint_dBfs, int knee_dBfs, unsigned int decay_ms, unsigned int hang_ms, int syncUpdate, int LNAstate); 
typedef mir_sdr_ErrT (*mir_sdr_StreamInit_t)(int *gRdB, double fsMHz, double rfMHz, mir_sdr_Bw_MHzT bwType, mir_sdr_If_kHzT ifType, int LNAstate, int *gRdBsystem, mir_sdr_SetGrModeT setGrMode, int *samplesPerPacket, mir_sdr_StreamCallback_t StreamCbFn, mir_sdr_GainChangeCallback_t GainChangeCbFn, void *cbContext); 
typedef mir_sdr_ErrT (*mir_sdr_StreamUninit_t)(void); 
typedef mir_sdr_ErrT (*mir_sdr_Reinit_t)(int *gRdB, double fsMHz, double rfMHz, mir_sdr_Bw_MHzT bwType, mir_sdr_If_kHzT ifType, mir_sdr_LoModeT loMode, int LNAstate, int *gRdBsystem, mir_sdr_SetGrModeT setGrMode, int *samplesPerPacket, mir_sdr_ReasonForReinitT reasonForReinit);
typedef mir_sdr_ErrT (*mir_sdr_GetGrByFreq_t)(double rfMHz, mir_sdr_BandT *band, int *gRdB, int LNAstate, int *gRdBsystem, mir_sdr_SetGrModeT setGrMode); 
typedef mir_sdr_ErrT (*mir_sdr_DebugEnable_t)(unsigned int enable);    
typedef mir_sdr_ErrT (*mir_sdr_GetCurrentGain_t)(mir_sdr_GainValuesT *gainVals);    

typedef mir_sdr_ErrT (*mir_sdr_GetDevices_t)(mir_sdr_DeviceT *devices, unsigned int *numDevs, unsigned int maxDevs);    
typedef mir_sdr_ErrT (*mir_sdr_SetDeviceIdx_t)(unsigned int idx);    
typedef mir_sdr_ErrT (*mir_sdr_ReleaseDeviceIdx_t)(void);    
typedef mir_sdr_ErrT (*mir_sdr_GetHwVersion_t)(unsigned char *ver);    
typedef mir_sdr_ErrT (*mir_sdr_RSPII_AntennaControl_t)(mir_sdr_RSPII_AntennaSelectT select); 
typedef mir_sdr_ErrT (*mir_sdr_RSPII_ExternalReferenceControl_t)(unsigned int output_enable); 
typedef mir_sdr_ErrT (*mir_sdr_RSPII_BiasTControl_t)(unsigned int enable); 
typedef mir_sdr_ErrT (*mir_sdr_RSPII_RfNotchEnable_t)(unsigned int enable); 

typedef mir_sdr_ErrT (*mir_sdr_RSP_SetGr_t)(int gRdB, int LNAstate, int abs, int syncUpdate);
typedef mir_sdr_ErrT (*mir_sdr_RSP_SetGrLimits_t)(mir_sdr_MinGainReductionT minGr);

typedef mir_sdr_ErrT (*mir_sdr_AmPortSelect_t)(int port);                          

// API function definitions
#ifdef __cplusplus
extern "C"
{
#endif

   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_Init(int gRdB, double fsMHz, double rfMHz, mir_sdr_Bw_MHzT bwType, mir_sdr_If_kHzT ifType, int *samplesPerPacket);
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_Uninit(void);
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_ReadPacket(short *xi, short *xq, unsigned int *firstSampleNum, int *grChanged, int *rfChanged, int *fsChanged);
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_SetRf(double drfHz, int abs, int syncUpdate);
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_SetFs(double dfsHz, int abs, int syncUpdate, int reCal);
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_SetGr(int gRdB, int abs, int syncUpdate);
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_SetGrParams(int minimumGr, int lnaGrThreshold);
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_SetDcMode(int dcCal, int speedUp);
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_SetDcTrackTime(int trackTime);
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_SetSyncUpdateSampleNum(unsigned int sampleNum);
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_SetSyncUpdatePeriod(unsigned int period);
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_ApiVersion(float *version);    // Called by application to retrieve version of API used to create Dll
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_ResetUpdateFlags(int resetGainUpdate, int resetRfUpdate, int resetFsUpdate);    
#if defined(ANDROID) || defined(__ANDROID__)
   // This function provides a machanism for the Java application to set
   // the callback function used to send request to it
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_SetJavaReqCallback(mir_sdr_SendJavaReq_t sendJavaReq);   
#endif
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_SetTransferMode(mir_sdr_TransferModeT mode);   
   /*
    * This following function will only operate correctly for the parameters detailed in the table below:
    *
    *      IF freq | Signal BW | Input Sample Rate | Output Sample Rate | Required Decimation Factor 
    *     -------------------------------------------------------------------------------------------
    *       450kHz |   200kHz  |     2000kHz       |       500kHz       |          M=4
    *       450kHz |   300kHz  |     2000kHz       |       500kHz       |          M=4
    *       450kHz |   600kHz  |     2000kHz       |      1000kHz       |          M=2
    *      2048kHz |  1536kHz  |     8192kHz       |      2048kHz       |          M=4
    *
    * If preReset == 1, then the filter state will be reset to 0 before starting the filtering operation.
    */
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_DownConvert(short *in, short *xi, short *xq, unsigned int samplesPerPacket, mir_sdr_If_kHzT ifType, unsigned int M, unsigned int preReset);   
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_SetParam(unsigned int id, unsigned int value);   // This MAY be called before mir_sdr_Init()

   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_SetPpm(double ppm);                              // This MAY be called before mir_sdr_Init()
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_SetLoMode(mir_sdr_LoModeT loMode);               // This MUST be called before mir_sdr_Init()/mir_sdr_StreamInit() - otherwise use mir_sdr_Reinit()         
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_SetGrAltMode(int *gRidx, int LNAstate, int *gRdBsystem, int abs, int syncUpdate);
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_DCoffsetIQimbalanceControl(unsigned int DCenable, unsigned int IQenable);   
   /*
    * Valid decimation factors for the following function are 2, 4, 8, 16 or 32 only
    * Setting wideBandSignal=1 will use a slower filter but minimise the in-band roll-off
    */
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_DecimateControl(unsigned int enable, unsigned int decimationFactor, unsigned int wideBandSignal); 
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_AgcControl(mir_sdr_AgcControlT enable, int setPoint_dBfs, int knee_dBfs, unsigned int decay_ms, unsigned int hang_ms, int syncUpdate, int LNAstate); 
   /*
    * mir_sdr_StreamInit() replaces mir_sdr_Init() and sets up a thread (or chain of threads) inside the API which will perform the processing chain (shown below),
    * and then use the callback function to return the data to the calling application/plug-in.
	 * Processing chain (in order):
    * mir_sdr_ReadPacket()
    * DCoffsetCorrection()     - LIF mode - enabled by default
    * DownConvert()            - automatically enabled if the parameters shown for mir_sdr_DownConvert() are selected
    * Decimate()               - disabled by default
    * DCoffsetCorrection()     - ZIF mode - enabled by default
    * IQimbalanceCorrection()  - enabled by default
    * Agc()                    - disabled by default
	 */
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_StreamInit(int *gRdB, double fsMHz, double rfMHz, mir_sdr_Bw_MHzT bwType, mir_sdr_If_kHzT ifType, int LNAstate, int *gRdBsystem, mir_sdr_SetGrModeT setGrMode, int *samplesPerPacket, mir_sdr_StreamCallback_t StreamCbFn, mir_sdr_GainChangeCallback_t GainChangeCbFn, void *cbContext); 
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_StreamUninit(void); 
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_Reinit(int *gRdB, double fsMHz, double rfMHz, mir_sdr_Bw_MHzT bwType, mir_sdr_If_kHzT ifType, mir_sdr_LoModeT loMode, int LNAstate, int *gRdBsystem, mir_sdr_SetGrModeT setGrMode, int *samplesPerPacket, mir_sdr_ReasonForReinitT reasonForReinit);
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_GetGrByFreq(double rfMHz, mir_sdr_BandT *band, int *gRdB, int LNAstate, int *gRdBsystem, mir_sdr_SetGrModeT setGrMode); 
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_DebugEnable(unsigned int enable);  
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_GetCurrentGain(mir_sdr_GainValuesT *gainVals);    

   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_GetDevices(mir_sdr_DeviceT *devices, unsigned int *numDevs, unsigned int maxDevs);    
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_SetDeviceIdx(unsigned int idx);   
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_ReleaseDeviceIdx(void);   
   /*
    * Uninit: ver = 0
    * RSPI :  ver = 1
    * RSPII:  ver = 2
    */
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_GetHwVersion(unsigned char *ver);   
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_RSPII_AntennaControl(mir_sdr_RSPII_AntennaSelectT select); 
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_RSPII_ExternalReferenceControl(unsigned int output_enable); 
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_RSPII_BiasTControl(unsigned int enable); 
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_RSPII_RfNotchEnable(unsigned int enable); 

   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_RSP_SetGr(int gRdB, int LNAstate, int abs, int syncUpdate);
   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_RSP_SetGrLimits(mir_sdr_MinGainReductionT minGr);

   _MIR_SDR_QUALIFIER mir_sdr_ErrT mir_sdr_AmPortSelect(int port);   // If called after mir_sdr_Init() a call to mir_sdr_Reinit(..., reasonForReinit = mir_sdr_CHANGE_AM_PORT)
                                                                     // is also required to change the port
#ifdef __cplusplus
}
#endif

#endif //MIR_SDR_H
