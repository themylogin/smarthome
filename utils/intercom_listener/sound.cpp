#include "sound.hpp"

namespace sound
{
    device open_device(const std::string name)
    {
        int err;
        snd_pcm_t* capture_handle;
	snd_pcm_hw_params_t* hw_params;
	
        if ((err = snd_pcm_open(&capture_handle, name.c_str(), SND_PCM_STREAM_CAPTURE, 0)) < 0)
        {
            throw exception("cannot open audio device '" + name + "'", snd_strerror(err));
        }
		   
        if ((err = snd_pcm_hw_params_malloc(&hw_params)) < 0)
        {
            throw exception("cannot allocate hardware parameter structure", snd_strerror(err));
        }

        if ((err = snd_pcm_hw_params_any(capture_handle, hw_params)) < 0)
        {
            throw exception("cannot initialize hardware parameter structure", snd_strerror(err));
        }

        if ((err = snd_pcm_hw_params_set_access(capture_handle, hw_params, SND_PCM_ACCESS_RW_INTERLEAVED)) < 0)
        {
            throw exception("cannot set access type", snd_strerror(err));
        }

        if ((err = snd_pcm_hw_params_set_format(capture_handle, hw_params, SND_PCM_FORMAT_S16_LE)) < 0)
        {
            throw exception("cannot set sample format", snd_strerror(err));
        }

        if ((err = snd_pcm_hw_params_set_rate(capture_handle, hw_params, 44100, 0)) < 0)
        {
            throw exception("cannot set sample rate", snd_strerror(err));
        }

        if ((err = snd_pcm_hw_params_set_channels(capture_handle, hw_params, 2)) < 0)
        {
            throw exception("cannot set channel count", snd_strerror(err));
        }

        if ((err = snd_pcm_hw_params(capture_handle, hw_params)) < 0)
        {
            throw exception("cannot set parameters", snd_strerror(err));
        }

        snd_pcm_hw_params_free(hw_params);

        if ((err = snd_pcm_prepare(capture_handle)) < 0)
        {
            throw exception("cannot prepare audio interface for use", snd_strerror(err));
        }
        
        return capture_handle;
    }

    bool read_device(device device, int16_t* buffer, size_t frames)
    {
        int err;
        if ((err = snd_pcm_readi(device, buffer, frames)) != frames)
        {
            if (err == -EPIPE)
            {
                if ((err = snd_pcm_prepare(device)) < 0)
                {
                    throw exception("recovering from overrun failed", snd_strerror(err));
                }
                
                return false;
            }
            
            throw exception("read from audio interface failed", snd_strerror(err));
        }
        
        return true;
    }
}
