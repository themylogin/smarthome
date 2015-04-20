#include "bell.hpp"

namespace sound_processor
{
    bell::bell() : block()
    {
        this->bell_is_being_detected_for = 0;
        
        this->set_block_size(this->block_size);
    }
    
    bell::~bell()
    {
    }
    
    std::string bell::process_block(int16_t* buffer, size_t buffer_size)
    {
        bool bell = true;
        for (int i = 0; i < buffer_size; i++)
        {
            if (buffer[i] < 16384)
            {
                bell = false;
                break;
            }
        }
        
        if (bell)
        {
            this->bell_is_being_detected_for += buffer_size;
        }
        else
        {
            if (this->bell_is_being_detected_for >= 11025)
            {
                this->bell_is_being_detected_for = 0;
                return "BELL";
            }
            else
            {
                this->bell_is_being_detected_for = 0;
            }
        }
        
        return "";
    }
}
