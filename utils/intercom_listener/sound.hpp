/* 
 * File:   sound.hpp
 * Author: themylogin
 *
 * Created on August 4, 2013, 2:37 PM
 */

#ifndef SOUND_HPP
#define	SOUND_HPP

#include <cstdint>
#include <exception>
#include <string>

#include <alsa/asoundlib.h>

namespace sound
{
    typedef snd_pcm_t* device;
    
    class exception : public std::exception
    {
    public:
        exception(std::string error, std::string snd_error)
        {
            this->error = error;
            this->snd_error = snd_error;
        }
        
        const char* what() const throw()
        {
            return (this->error + ": " + this->snd_error).c_str();
        }
        
    private:
        std::string error;
        std::string snd_error;
    };
    
    device open_device(const std::string name);
    bool read_device(device device, int16_t* buffer, size_t frames);
}

#endif	/* SOUND_HPP */
