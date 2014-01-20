#include "bell.hpp"

namespace sound_processor
{
    bell::bell() : block()
    {
        this->bell_is_being_detected_for = 0;
        
        this->set_block_size(this->block_size);
        this->low_passed = new int16_t[this->block_size];
        this->high_passed = new int16_t[this->block_size];
    }
    
    bell::~bell()
    {
        delete[] this->low_passed;
        delete[] this->high_passed;
    }
    
    std::string bell::process_block(int16_t* buffer, size_t buffer_size)
    {        
        float alpha = 0.1;
        this->low_passed[0] = buffer[0];
        for (int i = 1; i < buffer_size; i++)
        {
            this->low_passed[i] = alpha * buffer[i] + (1 - alpha) * buffer[i - 1];
        }
        
        for (int i = 0; i < buffer_size; i++)
        {
            this->high_passed[i] = buffer[i] - this->low_passed[i];
        }
        
        if (this->calculate_rms(this->high_passed, buffer_size) >= 5000)
        {
            this->bell_is_being_detected_for += buffer_size;
        }
        else
        {
            if (this->bell_is_being_detected_for >= 44100)
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
