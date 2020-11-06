cdef extern from "sdrplay_api_tuner.h":
    ctypedef enum sdrplay_api_TunerSelectT:
        sdrplay_api_Tuner_Neither  = 0
        sdrplay_api_Tuner_A        = 1
        sdrplay_api_Tuner_B        = 2
        sdrplay_api_Tuner_Both     = 3

cdef extern from "sdrplay_api_callback.h":
    ctypedef enum sdrplay_api_EventT:
        sdrplay_api_GainChange            = 0
        sdrplay_api_PowerOverloadChange   = 1
        sdrplay_api_DeviceRemoved         = 2
        sdrplay_api_RspDuoModeChange      = 3

    ctypedef struct sdrplay_api_StreamCbParamsT:
        unsigned int firstSampleNum;
        int grChanged;
        int rfChanged;
        int fsChanged;
        unsigned int numSamples;

    ctypedef union sdrplay_api_EventParamsT:
        pass

    ctypedef void (*sdrplay_api_StreamCallback_t)(short *xi, short *xq, sdrplay_api_StreamCbParamsT *params, unsigned int numSamples, unsigned int reset, void *cbContext);
    ctypedef void (*sdrplay_api_EventCallback_t)(sdrplay_api_EventT eventId, sdrplay_api_TunerSelectT tuner, sdrplay_api_EventParamsT *params, void *cbContext);


    ctypedef struct sdrplay_api_CallbackFnsT:
        sdrplay_api_StreamCallback_t StreamACbFn
        sdrplay_api_StreamCallback_t StreamBCbFn
        sdrplay_api_EventCallback_t  EventCbFn

cdef extern from "sdrplay_api.h":
    ctypedef void *HANDLE

    ctypedef struct sdrplay_api_DeviceT:
        pass

    ctypedef enum sdrplay_api_ErrT:
        pass

    ctypedef struct sdrplay_api_ErrorInfoT:
        char file[256]
        char function[256]
        int  line
        char message[1024]

    sdrplay_api_ErrT        sdrplay_api_Open()
    sdrplay_api_ErrT        sdrplay_api_Close()
    sdrplay_api_ErrT        sdrplay_api_ApiVersion(float *apiVer)
    sdrplay_api_ErrT        sdrplay_api_LockDeviceApi()
    sdrplay_api_ErrT        sdrplay_api_UnlockDeviceApi()
    sdrplay_api_ErrT        sdrplay_api_GetDevices(sdrplay_api_DeviceT *devices, unsigned int *numDevs, unsigned int maxDevs)
    sdrplay_api_ErrT        sdrplay_api_SelectDevice(sdrplay_api_DeviceT *device)
    sdrplay_api_ErrT        sdrplay_api_ReleaseDevice(sdrplay_api_DeviceT *device)
    const char*             sdrplay_api_GetErrorString(sdrplay_api_ErrT err)
    sdrplay_api_ErrorInfoT* sdrplay_api_GetLastError(sdrplay_api_DeviceT *device)
    sdrplay_api_ErrT        sdrplay_api_DisableHeartbeat(void) # Must be called before sdrplay_api_SelectDevice()

    sdrplay_api_ErrT        sdrplay_api_Init(HANDLE dev, sdrplay_api_CallbackFnsT *callbackFns, void *cbContext);
    sdrplay_api_ErrT        sdrplay_api_Uninit(HANDLE dev);
