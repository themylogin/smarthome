#include "code.hpp"

namespace sound_processor
{
    code::code() : block()
    {
        this->stopped = false;
        
        this->set_block_size(this->block_size);
        
        this->block_count = 0;
    }
    
    std::string code::process_block(int16_t* buffer, size_t buffer_size)
    {
        if (this->stopped)
        {
            return "";
        }
        
        float rms = this->calculate_rms(buffer, buffer_size);
        this->block_peaked[this->block_count++] = rms > 15000;

        if (this->has_code())
        {
            this->stopped = true;
            return "CODE";
        }

        if (this->block_count == max_block_count)
        {
            this->stopped = true;
            return "NO_CODE";
        }
        
        return "";
    }
    
    bool code::has_code()
    {
        for (size_t probably_first_knock = 0; probably_first_knock < this->block_count; probably_first_knock++)
	{
            if (this->block_peaked[probably_first_knock])
            {
                int second_knock = this->find_next_knock(probably_first_knock);
                if (second_knock != -1)
                {
                    int third_knock = this->find_next_knock(second_knock);
                    if (third_knock != -1)
                    {
                        return true;
                    }
                }
            }
	}
        
        return false;
    }
    
    
    int code::find_next_knock(size_t knock_block)
    {
        if (knock_block + 2 < this->block_count &&
            this->block_peaked[knock_block + 1] &&
            !this->block_peaked[knock_block + 2])
        {
            knock_block++;
        }

        int not_peaked_count = 0;
        for (int block = knock_block + 1; block < this->block_count; block++)
        {
            if (!this->block_peaked[block])
            {
                not_peaked_count++;
            }
            else
            {
                if (not_peaked_count == 3 || not_peaked_count == 4)
                {
                    return block;
                }
                else
                {
                    return -1;
                }
            }
        }
        return -1;
    }
}
