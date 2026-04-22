////////////////////////////////////////////////////////////////////////////////
/// @file    led.h
/// @author  AE TEAM
/// @brief   THIS FILE PROVIDES ALL THE SYSTEM FIRMWARE FUNCTIONS.
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
#ifndef __LED_H
#define __LED_H

// Files includes
#include "mm32_device.h"


////////////////////////////////////////////////////////////////////////////////
/// @defgroup MM32_Example_Layer
/// @brief MM32 Example Layer
/// @{

////////////////////////////////////////////////////////////////////////////////
/// @defgroup MM32_RESOURCE
/// @brief MM32 Examples resource modules
/// @{

////////////////////////////////////////////////////////////////////////////////
/// @defgroup MM32_Exported_Constants
/// @{

#define LED1_ON()     GPIOA->BRR=GPIO_BRR_BR15// PA15
#define LED1_OFF()    GPIOA->BSRR = GPIO_BSRR_BS15// PA15
#define LED1_TOGGLE()  (GPIOA->ODR&GPIO_ODR_ODR15)?(GPIOA->BRR=GPIO_BRR_BR15):(GPIOA->BSRR = GPIO_BSRR_BS15)


#define LED2_ON()   GPIOB->BRR=GPIO_BRR_BR3// PB3
#define LED2_OFF()  GPIOB->BSRR = GPIO_BSRR_BS3// PB3
#define LED2_TOGGLE()  (GPIOB->ODR&GPIO_ODR_ODR3)?(GPIOB->BRR=GPIO_BRR_BR3):(GPIOB->BSRR = GPIO_BSRR_BS3)

#define LED3_ON()   GPIOB->BRR=GPIO_BRR_BR4// PB4
#define LED3_OFF()  GPIOB->BSRR = GPIO_BSRR_BS4// PB4
#define LED3_TOGGLE()  (GPIOB->ODR&GPIO_ODR_ODR4)?(GPIOB->BRR=GPIO_BRR_BR4):(GPIOB->BSRR = GPIO_BSRR_BS4)

#define LED4_ON()   GPIOB->BRR=GPIO_BRR_BR5// PB5
#define LED4_OFF()  GPIOB->BSRR=GPIO_BSRR_BS5// PB5
#define LED4_TOGGLE()  (GPIOB->ODR&GPIO_ODR_ODR5)?(GPIOB->BRR=GPIO_BRR_BR5):(GPIOB->BSRR = GPIO_BSRR_BS5)
void LED_Init(void);


/// @}


/// @}

/// @}


////////////////////////////////////////////////////////////////////////////////
#endif
////////////////////////////////////////////////////////////////////////////////
