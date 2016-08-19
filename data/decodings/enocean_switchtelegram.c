#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{        
    int i, len = strlen(argv[2]);
    
    if (argc>2)
    {
        if (argv[1][0]=='d')
            for(i = 0; i < len; i++)
                switch(i % 12)
                {
                    case 0:
                    case 1:
                    case 2:
                    case 4:
                    case 5:
                    case 6:
                    case 8:
                    case 9:
                        putchar(argv[2][i]);
                        break;
                    default:
                        break;
                }            
        else
            for(i = 0; i < len; i++)
                switch(i % 8)
                {
                    case 0:
                    case 1:
                    case 3:
                    case 4:
                    case 6:
                        putchar(argv[2][i]);
                        break;
                    case 2:
                    case 5:
                        putchar(argv[2][i]);
                        if(argv[2][i] == '0') putchar('1');
                        else putchar('0');
                        break;
                    case 7:
                        putchar(argv[2][i]);
                        if(i < len - 1)
                            printf("01");
                }
        
    }
    else printf("Usage: %s <d/e> <bit sequence>\n\td - decode\n\te - encode\n\tbit sequence as string of 0 and 1.\n", argv[0]);
    
    return 0;
} 
