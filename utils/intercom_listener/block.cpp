#include "sound_processor/block.hpp"

namespace sound_processor
{    
    block::block()
    {
        this->block_data = NULL;
        this->block_size = 0;
        this->block_position = 0;
    }
    
    block::~block()
    {
        delete[] this->block_data;
    }

    void block::set_block_size(size_t block_size)
    {
        delete[] this->block_data;
        
        this->block_data = new int16_t[block_size];
        this->block_size = block_size;
        this->block_position = 0;
    }
    
    std::string block::process_sound(int16_t* buffer, size_t buffer_size)
    {
        size_t i;
        for (i = 0;
             this->block_position < this->block_size && i < buffer_size;
             this->block_position++, i++)
        {
            this->block_data[this->block_position] = buffer[i];
        }
                
        if (i < buffer_size)
        {
            std::string result = this->process_block(this->block_data, this->block_size);
            
            for (this->block_position = 0;
                 i < buffer_size;
                 this->block_position++, i++)
            {
                this->block_data[this->block_position] = buffer[i];
            }
            
            return result;
        }
        
        return "";
    }
}
