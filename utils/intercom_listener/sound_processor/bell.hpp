/* 
 * File:   bell.hpp
 * Author: themylogin
 *
 * Created on August 4, 2013, 3:23 PM
 */

#ifndef BELL_HPP
#define	BELL_HPP

#include "block.hpp"

namespace sound_processor
{
    class bell : public block
    {
    public:
        bell();
        virtual ~bell();
    protected:
        virtual std::string process_block(int16_t* buffer, size_t buffer_size);
        
    private:
        int bell_is_being_detected_for;
        
        const size_t block_size = 4410;
    };
}

#endif	/* BELL_HPP */

