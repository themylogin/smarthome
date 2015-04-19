/* 
 * File:   none.hpp
 * Author: themylogin
 *
 * Created on August 4, 2013, 3:43 PM
 */

#ifndef BLOCK_HPP
#define	BLOCK_HPP

#include "sound_processor.hpp"

namespace sound_processor
{
    class block : public sound_processor
    {
    public:
        block();
        virtual ~block();
        virtual std::string process_sound(int16_t* buffer, size_t buffer_size);
    protected:
        virtual void set_block_size(size_t block_size);
        virtual std::string process_block(int16_t* buffer, size_t buffer_size) = 0;
    private:
        int16_t* block_data;
        size_t block_size;
        size_t block_position;
    };
}

#endif	/* BLOCK_HPP */

