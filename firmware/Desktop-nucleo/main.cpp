#include "mbed.h"

Serial serial(SERIAL_TX, SERIAL_RX);
 
PwmOut ambient_light_r(PC_6);
PwmOut ambient_light_g(PC_8);
PwmOut ambient_light_b(PC_9);
 
PwmOut table_light_r(PB_13);
PwmOut table_light_g(PB_14);
PwmOut table_light_b(PB_15);
 
int main()
{
    serial.baud(38400);

    ambient_light_r.period_us(4096);
    ambient_light_g.period_us(4096);
    ambient_light_b.period_us(4096);

    table_light_r.period_us(4096);
    table_light_g.period_us(4096);
    table_light_b.period_us(4096);

    while (1)
    {
        char command = serial.getc();

        // Set PWM
        if (command == 0)
        {
            char dst = serial.getc();

            int r = (serial.getc()) | (serial.getc() << 8);
            int g = (serial.getc()) | (serial.getc() << 8);
            int b = (serial.getc()) | (serial.getc() << 8);

            if (dst == 0)
            {
                ambient_light_r.pulsewidth_us(r);
                ambient_light_g.pulsewidth_us(g);
                ambient_light_b.pulsewidth_us(b);
            }

            if (dst == 1)
            {
                table_light_r.pulsewidth_us(r);
                table_light_g.pulsewidth_us(g);
                table_light_b.pulsewidth_us(b);
            }
        }
    }
}
