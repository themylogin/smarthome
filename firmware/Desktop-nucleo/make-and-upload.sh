#!/bin/bash
make && echo "tar extended-remote :4242\nload\ncontinue" | arm-none-eabi-gdb Desktop-nucleo.elf
