#include "sound_processor.hpp"

#include <cmath>

namespace sound_processor
{
    float sound_processor::calculate_rms(int16_t* buffer, size_t buffer_size)
    {
        float rms = 0;
        for (int i = 0; i < buffer_size; i++)
        {
            rms += buffer[i] * buffer[i];
        }
        rms /= buffer_size;
        rms = sqrt(rms);
        return rms;
    }
}

