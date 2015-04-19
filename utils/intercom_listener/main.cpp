/* 
 * File:   main.cpp
 * Author: themylogin
 *
 * Created on August 4, 2013, 2:31 PM
 */

#include <cstdlib>
#include <iostream>
#include <string>

#include <boost/thread/thread.hpp>

#include "sound.hpp"
#include "sound_processor/bell.hpp"
#include "sound_processor/code.hpp"
#include "sound_processor/none.hpp"

sound::device device;
sound_processor::sound_processor* processor;
boost::mutex processor_lock;

void read_state()
{
    while (true)
    {
        std::string in;
        std::cin >> in;

        processor_lock.lock();
        if (in == "DO_NOT_LISTEN")
        {
            delete processor;
            processor = new sound_processor::none();
        }
        if (in == "LISTEN_FOR_BELL")
        {
            delete processor;
            processor = new sound_processor::bell();
        }
        if (in == "LISTEN_FOR_CODE")
        {
            delete processor;
            processor = new sound_processor::code();
        }
        processor_lock.unlock();
    }
}

void process_audio()
{
    while (true)
    {
        const size_t frames = 128;
        int16_t buffer[frames * 2];
        bool success = sound::read_device(device, buffer, frames);
        if (!success)
        {
            continue;
        }
        
        int16_t channel_buffer[frames];
        for (int i = 0; i < frames; i++)
        {
            channel_buffer[i] = buffer[i * 2];
        }
        
        processor_lock.lock();
        std::string result = processor->process_sound(channel_buffer, frames);
        processor_lock.unlock();        
        if (result != "")
        {
            std::cout << result << std::endl;
        }
    }
}

/*
 * 
 */
int main(int argc, char** argv)
{
    if (argc != 2)
    {
        std::cerr << "Usage: " << argv[0] << " <sound card>" << std::endl;
        return 1;
    }
    
    device = sound::open_device(argv[1]);
    processor = new sound_processor::bell();
    
    boost::thread read_state_thread(read_state);
    boost::thread process_audio_thread(process_audio);
    
    read_state_thread.join();
    process_audio_thread.join();
    
    return 0;
}

