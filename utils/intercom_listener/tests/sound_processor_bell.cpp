/*
 * File:   sound_processor_bell.cpp
 * Author: themylogin
 *
 * Created on Aug 12, 2013, 5:52:26 PM
 */

#include "sound_processor_bell.hpp"

#include <stdio.h>
#include <string.h>
#include <vector>

#include "../sound_processor/bell.hpp"

CPPUNIT_TEST_SUITE_REGISTRATION(sound_processor_bell);

sound_processor_bell::sound_processor_bell()
{
}

sound_processor_bell::~sound_processor_bell()
{
}

void sound_processor_bell::setUp()
{
}

void sound_processor_bell::tearDown()
{
}

void sound_processor_bell::testBell()
{
    sound_processor::bell processor;
    
    FILE* fh = fopen("tests/fixtures/bell.raw", "r");
    int pos = 0;
    std::vector<int> bells;
    while (!feof(fh))
    {
        const size_t buffer_size = 128;
        
        int16_t read_buffer[buffer_size];        
        pos += fread(read_buffer, 2, buffer_size, fh); 
        
        int16_t buffer[buffer_size / 2];
        for (int i = 0; i < buffer_size / 2; i++)
        {
            buffer[i] = read_buffer[i * 2];
        }
        
        std::string result = processor.process_sound(buffer, buffer_size / 2);
        if (result == "BELL")
        {
            bells.push_back(pos);
        }
        else if (result != "")
        {
            CPPUNIT_FAIL("sound_processor::bell should not say anything "
                         "than '' and 'BELL' (said '" + result + "')");
        }
    }
    fclose(fh);
    
    std::vector<int> expected_positions = {
        10319488,
        10566400, // +246912 (5.6s)
        10822144, // +255744 (5.8s)
        11069184, // +247040 (5.6s)
        11324928, // +255744 (5.8s)
        11571968, // +247040 (5.6s)
        11889408, //
    };
    
    CPPUNIT_ASSERT(bells.size() == expected_positions.size());
    for (int i = 0; i < expected_positions.size(); i++)
    {
        CPPUNIT_ASSERT(abs(bells[i] - expected_positions[i]) <= 44100 / 4); // +-0.25s
    }            
}
