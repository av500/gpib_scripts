#include <stdio.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <stdlib.h>

#include <linux/uinput.h>
#include <fcntl.h>
#include <string.h>
  
#include "gpib/ib.h"

unsigned char utul[] = {UNT,UNL};

int twos(int val)
{
	if (val & (1 << 15)) {
		val = val - (1 << 16);
	}
	return val;
}

void emit( int fd, int type, int code, int val )
{
	struct input_event ie;

	ie.type = type;
	ie.code = code;
	ie.value = val;
	ie.time.tv_sec = 0;
	ie.time.tv_usec = 0;

	write( fd, &ie, sizeof( ie ) );
}

void move_to(int fd, int x, int y)
{
	emit(fd, EV_ABS, ABS_X, x);
	emit(fd, EV_ABS, ABS_Y, y);
	emit(fd, EV_SYN, SYN_REPORT, 0);
}

void click(int fd, int btn, int press)
{
	emit(fd, EV_KEY, btn, press);
	emit(fd, EV_SYN, SYN_REPORT, 0);
}

int main( int argc, char *argv[] )
{
	int dev;
	int board_index = 0;
	int pad = 1;
	int sad = 0;
	int send_eoi = 1;
	int eos_mode = 0;
	struct uinput_setup usetup; 

	int fd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);

	ioctl(fd, UI_SET_EVBIT, EV_KEY);
	ioctl(fd, UI_SET_KEYBIT, BTN_TOUCH);
	ioctl(fd, UI_SET_KEYBIT, BTN_TOOL_PEN);
	ioctl(fd, UI_SET_MSCBIT, EV_MSC);

	ioctl(fd, UI_SET_EVBIT, EV_ABS);
	ioctl(fd, UI_SET_ABSBIT, ABS_X);
	ioctl(fd, UI_SET_ABSBIT, ABS_Y);	

	memset(&usetup, 0, sizeof(usetup));
	usetup.id.bustype = BUS_USB;
	usetup.id.vendor  = 0x9111; /* sample vendor */
	usetup.id.product = 0x9111; /* sample product */
	strcpy(usetup.name, "HP9111A Graphics Tablet");

	ioctl(fd, UI_DEV_SETUP, &usetup);

	int x_res  = 12032;
	int y_res  = 8340; 

	struct uinput_abs_setup abs;
	abs.code               = ABS_X;
	abs.absinfo.value      = 0;
	abs.absinfo.minimum    = 0;
	abs.absinfo.maximum    = x_res;
	abs.absinfo.fuzz       = 0;
	abs.absinfo.flat       = 0;
	abs.absinfo.resolution = 40;

	ioctl(fd, UI_ABS_SETUP, &abs);

	abs.absinfo.maximum    = y_res;
	abs.code               = ABS_Y;

	ioctl(fd, UI_ABS_SETUP, &abs);
	 
	ioctl(fd, UI_DEV_CREATE);

	dev = ibdev( board_index, pad, sad, TNONE, send_eoi, eos_mode );
	if( dev < 0 ) {
		fprintf( stderr, "ibdev() failed\n" );
		fprintf( stderr, "%s\n", gpib_error_string( ThreadIberr() ) );
		return -1;
	}

	printf( "board: %i, pad: %i  sad: %i\n", board_index, pad, sad);
	
	int x_max  = 12032;
	int y_max  = 8340;
	
	int prox   = 0;
	int down   = 0;
	int last_x = 0;
	int last_y = 0;
	
	while(1) {
		uint8_t data[6];
		int status = ibrd( dev, data, 6 );
		if( status & ERR ) {
			fprintf( stderr, "ibrd() failed\n" );
			fprintf( stderr, "%s\n", gpib_error_string( ThreadIberr() ) );
			return -1;
		}

		int count = ThreadIbcntl(); // should be always 6
	
		int x = twos(data[1] + (data[0] << 8));
		int y = twos(data[3] + (data[2] << 8));
		int s = data[5] + (data[4] << 8);

		if( s & 256 ) {
			if( !prox ) {
				printf( "\t\t\t\tPROX\n");
				prox = 1;
				click(fd, BTN_TOOL_PEN, prox);
			}
			if( last_x != x || last_y != y ) {
				int x_pos = x;
				int y_pos = y_res - y;
				if(x_pos < 0) {
					x_pos = 0;
				}
				if(x_pos >= x_res) {
					x_pos = x_res - 1;
				}
				if(y_pos < 0) {
					y_pos = 0;
				}
				if(y_pos >= y_res) {
					y_pos = y_res - 1;
				}
			
				printf( "%5d  %5d  %5d  %5d\n", x, y, x_pos, y_pos);
				move_to(fd, x_pos, y_pos);
				last_x = x;
				last_y = y;
			}
		} else {
			if( prox ) {
				printf( "\t\t\t\tAWAY\n");
				prox = 0;
				click(fd, BTN_TOOL_PEN, prox);
			}
		}
		if( s & 1024 ) {
			if( !down ) {
				printf( "\t\t\t\tDOWN\n");
				down = 1;
				click(fd, BTN_TOUCH, down);
			} 
		} else {
			if( down ) {
				printf( "\t\t\t\tUP\n");
				down = 0;
				click(fd, BTN_TOUCH, down);
			}
		}
	}
	
	if (ERR & ibcmd(board_index, utul, 2)) { // send Untalk and Unlisten
                fprintf( stderr, "ibcmd() failed\n" );
                fprintf( stderr, "%s\n", gpib_error_string( ThreadIberr() ) );
                return -1;
        }

	return 0;
}

