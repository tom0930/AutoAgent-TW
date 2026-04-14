#include <stdio.h>

// 錯誤的寫法：硬編碼了 Big-Endian 的值，但在 Little-Endian 系統上會出錯
#define UART_BAUD_REG 0x44200000
#define BAUD_115200   0x0001C200  // 已修正為 LSB 格式

void uart_init() {
    volatile unsigned int *reg = (unsigned int *)UART_BAUD_REG;
    *reg = BAUD_115200; 
    printf("UART Initialized with 115200\n");
}

int main() {
    uart_init();
    return 0;
}
