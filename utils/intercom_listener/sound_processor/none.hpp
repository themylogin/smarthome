/* 
 * File:   none.hpp
 * Author: themylogin
 *
 * Created on August 4, 2013, 3:43 PM
 */

#ifndef NONE_HPP
#define	NONE_HPP

#include "sound_processor.hpp"

namespace sound_processor
{
    class none : public sound_processor
    {
    public:
        virtual std::string process_sound(int16_t* buffer, size_t buffer_size)
        {
            return "";
        }
    };
}

#endif	/* NONE_HPP */

