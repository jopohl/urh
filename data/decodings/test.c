#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{	
	int i, count, what;	
	if(argc>2)
	{
		if(argv[1][0]=='d')
		{
			for(i = 0; i < strlen(argv[2]); i++)
				if(argv[2][i] == '0') printf("000");
				else printf("11");
		}
		else
		{
			count = 0;
			what = -1;
			for(i = 0; i < strlen(argv[2]); i++)
			{	
				if(argv[2][i] == '0')
				{
					if(what == 1) count = 0;
					what = 0;
					count++;
					if(count == 3)
					{
						putchar('0');
						count = 0;
					}
				}
				else
				{
					if(what == 0) count = 0;
					what = 1;
					count++;
					if(count == 2)
					{
						putchar('1');
						count = 0;
					}
				}
			}
		}
	}
	return 0;
}
