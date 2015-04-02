#include "stm32f10x_gpio.h"
#include "stm32f10x_rcc.h"

void Delay(__IO uint32_t nCount)
{
	while(nCount--)
	{
	}
}

int main(void)
{
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOC, ENABLE);

	GPIO_InitTypeDef GPIO_InitStruct;

	GPIO_InitStruct.GPIO_Pin = GPIO_Pin_0;
	GPIO_InitStruct.GPIO_Mode = GPIO_Mode_IPD;
	GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOC, &GPIO_InitStruct);

	GPIO_InitStruct.GPIO_Pin = GPIO_Pin_7;
	GPIO_InitStruct.GPIO_Mode = GPIO_Mode_Out_PP;
	GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOC, &GPIO_InitStruct);

    while(1)
    {
    	if (GPIO_ReadInputDataBit(GPIOC, GPIO_Pin_0))
    	{
    		GPIO_ResetBits(GPIOC, GPIO_Pin_7);
    	}
    	else
    	{
    		GPIO_SetBits(GPIOC, GPIO_Pin_7);
    		Delay(72e3);
    		GPIO_ResetBits(GPIOC, GPIO_Pin_7);
    		Delay(72e3);
    	}
    }
}
