/* 
 * File:   sound_processor.hpp
 * Author: themylogin
 *
 * Created on August 4, 2013, 3:20 PM
 */

#ifndef SOUND_PROCESSOR_HPP
#define	SOUND_PROCESSOR_HPP

#include <cstdint>
#include <string>

namespace sound_processor
{
    class sound_processor
    {
    public:
        virtual std::string process_sound(int16_t* buffer, size_t buffer_size) = 0;
    protected:
        float calculate_rms(int16_t* buffer, size_t buffer_size);
    };
};

#endif	/* SOUND_PROCESSOR_HPP */
