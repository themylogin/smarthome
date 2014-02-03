#include "stm32f10x.h"
#include "stm32f10x_gpio.h"
#include "stm32f10x_rcc.h"
#include "stm32f10x_tim.h"
#include "stm32f10x_usart.h"
#include "misc.h"

union {
	uint8_t uint8[6];
	uint16_t uint16[3];
} input;
int input_size = 0;
int no_connection = 0;

/**
  * @brief   Main program
  * @param  None
  * @retval None
  */
int main(void)
{
	/* System Clocks Configuration */
	RCC_Configuration();

	/* GPIO Configuration */
	GPIO_Configuration();

	/* Watchdog Timer Configuration */
	TIM3_Configuration();

	/* PWM Timer Configuration */
	TIM4_Configuration();

	/* USART Configuration */
	USART_Configuration();

	while (1);
}

/**
  * @brief  Configures the different system clocks.
  * @param  None
  * @retval None
  */
void RCC_Configuration(void)
{
	/* Setup the microcontroller system. Initialize the Embedded Flash Interface,
	 initialize the PLL and update the SystemFrequency variable. */
	SystemInit();

	/* PCLK1 = HCLK/4 */
	RCC_PCLK1Config(RCC_HCLK_Div4);

	/* TIM3 clock enable */
	RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM3, ENABLE);

	/* TIM4 clock enable */
	RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM4, ENABLE);

	/* GPIO and USART1 clock enable */
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOB |
						   RCC_APB2Periph_GPIOC | RCC_APB2Periph_AFIO |
						   RCC_APB2Periph_USART1, ENABLE);

}

/**
  * @brief  Configure the TIM4 Output Channels and USART1 Pins.
  * @param  None
  * @retval None
  */
void GPIO_Configuration(void)
{
	GPIO_InitTypeDef GPIO_InitStructure;

	/* GPIOB Configuration: TIM4 Channel2, 3 and 4 as alternate function push-pull */
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_7 | GPIO_Pin_8 | GPIO_Pin_9;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOB, &GPIO_InitStructure);

	/* GPIOA Configuration: USART1 TX */
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_9;
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
	GPIO_Init(GPIOA, &GPIO_InitStructure);

	/* GPIOA Configuration: USART1 RX */
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_10;
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_InitStructure.GPIO_Mode  = GPIO_Mode_IN_FLOATING;
	GPIO_Init(GPIOA, &GPIO_InitStructure);
}

/**
 * @brief   Configure TIM3
 * @param   None
 * @retval  None
 */
void TIM3_Configuration(void)
{
	TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure;
	TIM_TimeBaseStructure.TIM_Period = 10000;	// no signal for 1.38888 sec = connection lost
	TIM_TimeBaseStructure.TIM_Prescaler = 9999;	// 7.2 kHz = each 138.888 usec
	TIM_TimeBaseStructure.TIM_ClockDivision = 0;
	TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up;
	TIM_TimeBaseInit(TIM3, &TIM_TimeBaseStructure);

	TIM_ITConfig(TIM3, TIM_IT_Update, ENABLE);
	TIM_Cmd(TIM3, ENABLE);

	NVIC_InitTypeDef   NVIC_InitStructure;
	NVIC_InitStructure.NVIC_IRQChannel = TIM3_IRQn;
	NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 0x0F;
	NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0x0F;
	NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
	NVIC_Init(&NVIC_InitStructure);
	NVIC_EnableIRQ(TIM3_IRQn);
}

/**
 * @brief   Configure TIM4
 * @param   None
 * @retval  None
 */
void TIM4_Configuration(void)
{
	TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure;
	TIM_OCInitTypeDef TIM_OCInitStructure;

	/* -----------------------------------------------------------------------
	TIM4 Configuration: generate 4 PWM signals with 4 different duty cycles:
	TIM4CLK = 72 MHz, Prescaler = 18, TIM4 counter clock = 4 MHz
	TIM4 ARR Register = 3999 => TIM4 Frequency = TIM4 counter clock/(ARR + 1)
	TIM4 Frequency = 1 KHz.
	----------------------------------------------------------------------- */

	/* Time base configuration */
	TIM_TimeBaseStructure.TIM_Period = 3999;
	TIM_TimeBaseStructure.TIM_Prescaler = 18;
	TIM_TimeBaseStructure.TIM_ClockDivision = 0;
	TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up;

	TIM_TimeBaseInit(TIM4, &TIM_TimeBaseStructure);

	/* PWM1 Mode configuration: Channel1 */
	TIM_OCInitStructure.TIM_OCMode = TIM_OCMode_PWM1;
	TIM_OCInitStructure.TIM_OutputState = TIM_OutputState_Enable;
	TIM_OCInitStructure.TIM_Pulse = 4000;
	TIM_OCInitStructure.TIM_OCPolarity = TIM_OCPolarity_High;

	TIM_OC1Init(TIM4, &TIM_OCInitStructure);

	TIM_OC1PreloadConfig(TIM4, TIM_OCPreload_Enable);

	/* PWM1 Mode configuration: Channel2 */
	TIM_OCInitStructure.TIM_OutputState = TIM_OutputState_Enable;
	TIM_OCInitStructure.TIM_Pulse = 4000;

	TIM_OC2Init(TIM4, &TIM_OCInitStructure);

	TIM_OC2PreloadConfig(TIM4, TIM_OCPreload_Enable);

	/* PWM1 Mode configuration: Channel3 */
	TIM_OCInitStructure.TIM_OutputState = TIM_OutputState_Enable;
	TIM_OCInitStructure.TIM_Pulse = 4000;

	TIM_OC3Init(TIM4, &TIM_OCInitStructure);

	TIM_OC3PreloadConfig(TIM4, TIM_OCPreload_Enable);

	/* PWM1 Mode configuration: Channel4 */
	TIM_OCInitStructure.TIM_OutputState = TIM_OutputState_Enable;
	TIM_OCInitStructure.TIM_Pulse = 4000;

	TIM_OC4Init(TIM4, &TIM_OCInitStructure);

	TIM_OC4PreloadConfig(TIM4, TIM_OCPreload_Enable);

	TIM_ARRPreloadConfig(TIM4, ENABLE);

	/* TIM4 enable counter */
	TIM_Cmd(TIM4, ENABLE);
}

/**
 * @brief   Configure Network
 * @param   None
 * @retval  None
 */
void USART_Configuration(void)
{
	USART_InitTypeDef USART_InitStructure;
	USART_InitStructure.USART_BaudRate = 9600;
	USART_InitStructure.USART_WordLength = USART_WordLength_8b;
	USART_InitStructure.USART_StopBits = USART_StopBits_1;
	USART_InitStructure.USART_Parity = USART_Parity_No;
	USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
	USART_InitStructure.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
	USART_Init(USART1, &USART_InitStructure);
	USART_Cmd(USART1, ENABLE);

	NVIC_InitTypeDef NVIC_InitStructure;
	USART_ITConfig(USART1, USART_IT_RXNE, ENABLE);
	NVIC_InitStructure.NVIC_IRQChannel = USART1_IRQn;
	NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 0;
	NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0;
	NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
	NVIC_Init(&NVIC_InitStructure);
}

/**
 * @brief   Handles interrupts from TIM3
 * @param   None
 * @retval  None
 */
void TIM3_IRQHandler(void)
{
	if (no_connection)
	{
		input_size = 0;
		TIM4->CCR2 = 4000;
		TIM4->CCR3 = 4000;
		TIM4->CCR4 = 4000;
	}
	no_connection = 1;

	TIM_ClearITPendingBit(TIM3, TIM3_IRQn);
}

/**
 * @brief   Handles interrupts from USART1
 * @param   None
 * @retval  None
 */
void USART1_IRQHandler(void)
{
	if (USART_GetITStatus(USART1, USART_IT_RXNE) == SET)
	{
		no_connection = 0;
		input.uint8[input_size++] = USART_ReceiveData(USART1);
		if (input_size == 6)
		{
			TIM4->CCR2 = input.uint16[0];
			TIM4->CCR3 = input.uint16[1];
			TIM4->CCR4 = input.uint16[2];
			input_size = 0;
		}

		USART_ClearITPendingBit(USART1, USART_IT_RXNE);
	}
}
