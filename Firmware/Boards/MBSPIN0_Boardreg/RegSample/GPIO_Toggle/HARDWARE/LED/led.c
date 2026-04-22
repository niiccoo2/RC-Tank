////////////////////////////////////////////////////////////////////////////////
/// @file     led.c
/// @author   AE TEAM
/// @brief    THIS FILE PROVIDES ALL THE SYSTEM FUNCTIONS.
////////////////////////////////////////////////////////////////////////////////
/// @attention
///
/// THE EXISTING FIRMWARE IS ONLY FOR REFERENCE, WHICH IS DESIGNED TO PROVIDE
/// CUSTOMERS WITH CODING INFORMATION ABOUT THEIR PRODUCTS SO THEY CAN SAVE
/// TIME. THEREFORE, MINDMOTION SHALL NOT BE LIABLE FOR ANY DIRECT, INDIRECT OR
/// CONSEQUENTIAL DAMAGES ABOUT ANY CLAIMS ARISING OUT OF THE CONTENT OF SUCH
/// HARDWARE AND/OR THE USE OF THE CODING INFORMATION CONTAINED HEREIN IN
/// CONNECTION WITH PRODUCTS MADE BY CUSTOMERS.
///
/// <H2><CENTER>&COPY; COPYRIGHT MINDMOTION </CENTER></H2>
////////////////////////////////////////////////////////////////////////////////

// Define to prevent recursive inclusion
#define _LED_C_

// Files includes
#include "led.h"

////////////////////////////////////////////////////////////////////////////////
/// @addtogroup MM32_Example_Layer
/// @{

////////////////////////////////////////////////////////////////////////////////
/// @addtogroup LED
/// @{

////////////////////////////////////////////////////////////////////////////////
/// @addtogroup LED_Exported_Constants
/// @{

////////////////////////////////////////////////////////////////////////////////
/// @brief    LED initialization
/// @param    None
/// @retval   None
////////////////////////////////////////////////////////////////////////////////
void LED_Init(void)
{
    RCC->AHBENR |= RCC_AHBENR_GPIOA | RCC_AHBENR_GPIOB;                         //enable GPIOA,B clock

    GPIOA->CRH &= ~(GPIO_CNF_MODE_MASK << GPIO_CRH_CNF_MODE_15_Pos);
    GPIOA->CRH |= GPIO_CNF_MODE_OUT_PP << GPIO_CRH_CNF_MODE_15_Pos;

    GPIOA->ODR |= GPIO_ODR_ODR15;                                               //PA15  output high

    //set PB3,PB4,PB5 as push-pull output
    GPIOB->CRL &= ~((GPIO_CNF_MODE_MASK << GPIO_CRL_CNF_MODE_3_Pos) | \
                    (GPIO_CNF_MODE_MASK << GPIO_CRL_CNF_MODE_4_Pos) | \
                    (GPIO_CNF_MODE_MASK << GPIO_CRL_CNF_MODE_5_Pos) );
    GPIOB->CRL |=  ((GPIO_CNF_MODE_OUT_PP << GPIO_CRL_CNF_MODE_3_Pos) | \
                    (GPIO_CNF_MODE_OUT_PP << GPIO_CRL_CNF_MODE_4_Pos) | \
                    (GPIO_CNF_MODE_OUT_PP << GPIO_CRL_CNF_MODE_5_Pos) );

    GPIOB->ODR |= GPIO_ODR_ODR3 | GPIO_ODR_ODR4 | GPIO_ODR_ODR5;                //PB3,PB4,PB5 output high

    LED1_OFF();
    LED2_OFF();
    LED3_OFF();
    LED4_OFF();
}

/// @}


/// @}

/// @}

