#include <stdio.h>
#include <string.h>

typedef unsigned char byte;

byte str2byte(char str[8])
{
    int ret = 0, i;
    for(i = 0; i < 8; i++)
        if (str[i]=='1') ret |= (1<<(7-i));
    return ret;
}

void print_binary(byte inpt)
{
    int i;
    for(i = 0; i < 8; i++)
        if (inpt & (1<<(7-i))) putchar('1');
        else putchar('0');
}

int main(int argc, char **argv)
{
    int i, max, offset;
    byte dec[256]={0}, enc[256]={0};
    char string[2048]={0};
    
    offset = 8; // Preamble + Sync
    
    if (argc>2)
    {
        if (argv[1][0]=='d')
        {
            if (strlen(argv[2]) > 256*8 || strlen(argv[2]) < 4) return -1;
            memcpy(string, argv[2], strlen(argv[2]));
            
            for (i = 0; i < strlen(string)-3; i+=8)
                enc[i/8] = str2byte(&string[i]);                
            max = i/8;
            memcpy(&dec, &enc, 256);

            /*
             * byte[] Dec = new byte[Enc.Length];
             * Dec[0] = Enc[0]; //Packet length
             * Dec[1] = (byte)((~Enc[1]) ^ 0x89);
             * int j;
             * for (j = 2; j < Dec[0]; j++)
             *   Dec[j] = (byte)((Enc[j-1] + 0xdc) ^ Enc[j]);
             * Dec[j] = (byte)(Enc[j] ^ Dec[2]);
             */
            
            dec[offset+0] = enc[offset+0];
            
            dec[offset+1] = (~enc[offset+1])^0x89;
            for(i = offset+2; i < max; i++)
                dec[i] = (enc[i-1]+0xdc) ^ enc[i];
            dec[offset+i] = enc[offset+i] ^ dec[offset+2];
            
            dec[max-1]=0; // Set CRC to 0x0000
            dec[max-2]=0;
            
            for(i = 0; i < max; i++)
                print_binary(dec[i]);
        }
        else
        {
            if (strlen(argv[2]) > 256*8 || strlen(argv[2]) < 4) return -1;
            memcpy(string, argv[2], strlen(argv[2]));
            
            for (i = 0; i < strlen(string)-3; i+=8)
                dec[i/8] = str2byte(&string[i]);
            max = i/8;
            memcpy(&enc, &dec, 256);
            
            /*
             * byte[] Dec = new byte[Enc.Length];
             * Dec[0] = Enc[0]; //Packet length
             * Dec[1] = (byte)((~Enc[1]) ^ 0x89);
             * int j;
             * for (j = 2; j < Dec[0]; j++)
             *   Dec[j] = (byte)((Enc[j-1] + 0xdc) ^ Enc[j]);
             * Dec[j] = (byte)(Enc[j] ^ Dec[2]);
             */
            
            enc[offset+0] = dec[offset+0];
            
            enc[offset+1] = ~(dec[offset+1]^0x89);
            for(i = offset+2; i < max; i++)
                enc[i] = (enc[i-1]+0xdc) ^ dec[i];
            enc[offset+i] = dec[offset+i] ^ dec[offset+2];
            
            enc[max-1]=0; // Set CRC to 0x0000
            enc[max-2]=0;
            
            for(i = 0; i < max; i++)
                print_binary(enc[i]);    
        }
    }
    else printf("Usage: %s <d/e> <bit sequence>\n\td - decode\n\te - encode\n\tbit sequence as string of 0 and 1.\n", argv[0]);
    
    return 0;
} 
