/* 
 * File:   code.hpp
 * Author: themylogin
 *
 * Created on August 4, 2013, 3:44 PM
 */

#ifndef CODE_HPP
#define	CODE_HPP

#include "block.hpp"

namespace sound_processor
{
    class code : public block
    {
    public:
        code();
    protected:
        virtual std::string process_block(int16_t* buffer, size_t buffer_size);        
    private:
        bool has_code();
        int find_next_knock(size_t block_window);
        
        bool stopped;
        
        static const size_t block_size = 44100 * 0.05;
        
        static const size_t max_data_size = 44100 * 5;                
        static const size_t max_block_count = max_data_size / block_size;
        bool block_peaked[max_block_count];
        size_t block_count;
    };
}

#endif	/* CODE_HPP */

