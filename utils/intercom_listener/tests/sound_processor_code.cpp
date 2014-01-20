/*
 * File:   sound_processor_code.cpp
 * Author: themylogin
 *
 * Created on Aug 4, 2013, 6:09:21 PM
 */

#include "sound_processor_code.hpp"

#include <stdio.h>
#include <string.h>

#include "../sound_processor/code.hpp"

CPPUNIT_TEST_SUITE_REGISTRATION(sound_processor_code);

sound_processor_code::sound_processor_code()
{
}

sound_processor_code::~sound_processor_code()
{
}

void sound_processor_code::setUp()
{
}

void sound_processor_code::tearDown()
{
}

void sound_processor_code::testKnock1()
{
    this->testFromFile("tests/fixtures/knock1.raw", true);
}

void sound_processor_code::testKnock2()
{
    this->testFromFile("tests/fixtures/knock2.raw", true);
}

void sound_processor_code::testNoKnock1()
{
    this->testFromFile("tests/fixtures/noKnock1.raw", false);
}

void sound_processor_code::testFromFile(std::string file, bool hasCode)
{
    sound_processor::code processor;
    
    int fed = 0;
    std::string result = "";
    FILE* fh = fopen(file.c_str(), "r");
    while (fed < 44100 * 5)
    {
        const size_t buffer_size = 256;
        
        int16_t read_buffer[buffer_size];        
        if (!feof(fh))
        {
            fread(read_buffer, 2, buffer_size, fh); 
        }
        else
        {
            memset(read_buffer, 0, buffer_size * 2);
        }
        
        int16_t buffer[buffer_size / 2];
        for (int i = 0; i < buffer_size / 2; i++)
        {
            buffer[i] = read_buffer[i * 2];
        }
        
        result += processor.process_sound(buffer, buffer_size / 2);
        fed += 128;
    }
    fclose(fh);
    
    if (hasCode)
    {
        CPPUNIT_ASSERT_MESSAGE("result = '" + result + "'", result == "CODE");
    }
    else
    {
        CPPUNIT_ASSERT_MESSAGE("result = '" + result + "'", result == "NO_CODE");
    }
}

