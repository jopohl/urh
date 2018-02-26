#include <stdio.h>
#include <string.h>

typedef unsigned char byte;
typedef unsigned short uint16;

uint16 crc(byte *data, int len) 
{
    byte i, x, crcdata;
    uint16 crcReg = 0xFFFF;  
    for (x = 0; x < len; x++)
    { 
        crcdata = data[x];
        for (i = 0; i < 8; i++) 
        {
            if (((crcReg & 0x8000) >> 8) ^ (crcdata & 0x80))
                crcReg = (crcReg << 1) ^ 0x8005;
            else
                crcReg = (crcReg << 1);        
            crcdata <<= 1;
        }
    }
    return crcReg;
}

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

int find_preamble_start_in_bit(char *string, int len)
{
    char homematic_sync[]="11101001110010101110100111001010";    
    for(int i = 0, j = 0; i < len; i++)
    {
        if(string[i]==homematic_sync[j])
        {     
            j++;
            if(j == 32 && i>= 63) return i-63;            
        }
        else j = 0;
    }
    return -1; //not found
}

void xor_lfsr(char *string)
{
    int i, j, x, len = strlen(string);
    byte polynomial[9] = {0, 0, 0, 1, 0, 0, 0, 0, 1};
    byte lfsr_state[9];
    byte first_bit;
    
    // Init with 8x 1 Bit
    memset(lfsr_state, 1, 9);
    for(j = 0; j < 8; j++)
        if(string[j]=='1')
            string[j]='0';                
        else
            string[j]='1';            
        
    for(x = 8; x < len-7; x += 8)
    {        
        for(i = 0; i < 8; i++)
        {        
            first_bit = 255;
            for(j = 8; j >= 0; j--)
                if(polynomial[j] && lfsr_state[j])
                {
                    if(first_bit == 255)
                        first_bit = 1;
                    else
                        first_bit = (first_bit==1) ? 0 : 1;                
                }
            if(first_bit == 255)
                first_bit = 0;
            
            // Clock
            for(j = 8; j >= 0; j--)
                lfsr_state[j] = lfsr_state[j-1];
            lfsr_state[0] = first_bit;
        }

        // Xor
        for(j = 0; j < 8; j++)
            if(lfsr_state[j+1] == 1)
                if(string[x+j]=='1')
                    string[x+j]='0';                
                else
                    string[x+j]='1';
    }
}

int main(int argc, char **argv)
{
    int i, j, max, offset, len;
    byte dec[256]={0}, enc[256]={0}, crc_ok;
    char string[2048]={0};
    uint16 crcvalue;
    offset = 8; // Preamble + Sync
    
    // Copy data (argv[2]) to string if length is ok, shorten to multiple of 8 bit
    if (strlen(argv[2]) > 256*8 || strlen(argv[2]) < 4) return -1;
    len = strlen(argv[2]);    
    
    i = find_preamble_start_in_bit(argv[2], len);
    if(i < 0) return 0;    // preamble+sync not found or wrong length
    
    len = (len-i)-(len-i)%8;
    memcpy(string, argv[2]+i, len);
               
    if (argc>2)
    {
        if (argv[1][0]=='d')
        {   
            // Apply datawhitening      
            xor_lfsr(string+64);
                               
            // Pack to bytes
            for (i = 0; i < strlen(string)-3; i+=8)
                enc[i/8] = str2byte(&string[i]);                
            max = i/8;
            memcpy(&dec, &enc, 256);

            // Check CRC
            crcvalue = crc(&dec[8], max-2-8);
            crc_ok = 0;
            if( ((crcvalue >> 8) & 0xFF) == dec[max-2] && (crcvalue & 0xFF) == dec[max-1]) crc_ok = 1;
            
            /*
             * byte[] Dec = new byte[Enc.Length];
             * Dec[0] = Enc[0]; //Packet length
             * Dec[1] = (byte)((~Enc[1]) ^ 0x89);
             * int j;
             * for (j = 2; j < Dec[0]; j++)
             *   Dec[j] = (byte)((Enc[j-1] + 0xdc) ^ Enc[j]);
             * Dec[j] = (byte)(Enc[j] ^ Dec[2]);
             */
            
            // Decrypt
            dec[offset+0] = enc[offset+0];
            
            dec[offset+1] = (~enc[offset+1])^0x89;
            for(i = offset+2; i < max; i++)
                dec[i] = (enc[i-1]+0xdc) ^ enc[i];
            dec[offset+i] = enc[offset+i] ^ dec[offset+2];
            
            // Recompute CRC and overwrite with FAKE-CRC, if CRC was OK before
            if(crc_ok)
            {
                crcvalue = crc(&dec[8], max-2-8);
                dec[max-1] = crcvalue & 0xFF; 
                dec[max-2] = (crcvalue >> 8) & 0xFF;
            }
            else
            {
                dec[max-1] = 0x0F; // Set magic code for wrong CRC
                dec[max-2] = 0xD0;
            }
            
            for(i = 0; i < max; i++)
                print_binary(dec[i]);
        }
        else
        {
            // Pack to bytes
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
            
            // Encrypt
            enc[offset+0] = dec[offset+0];
            
            enc[offset+1] = ~(dec[offset+1]^0x89);
            for(i = offset+2; i < max; i++)
                enc[i] = (enc[i-1]+0xdc) ^ dec[i];
            enc[offset+i] = dec[offset+i] ^ dec[offset+2];
            
            // Overwrite with correct CRC
            crcvalue = crc(&enc[8], max-2-8);
            enc[max-1] = crcvalue & 0xFF;
            enc[max-2] = (crcvalue >> 8) & 0xFF;            
            
            // Convert to string
            memset(string, 0, 2048);
            for(i = 0; i < max; i++)
            {
                for(j = 0; j < 8; j++)
                    if(enc[i] & (1<<(7-j))) string[i*8+j]='1';
                    else string[i*8+j]='0';
            }
            // Apply datawhitening
            xor_lfsr(string+64);
            
            // Print bits and duplicate last bit
            printf("%s%c\n", string, string[strlen(string)-1]);
        }
    }
    else printf("Usage: %s <d/e> <bit sequence>\n\td - decode\n\te - encode\n\tbit sequence as string of 0 and 1.\n", argv[0]);
    
    return 0;
} 
