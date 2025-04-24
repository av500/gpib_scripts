#include <stdio.h>
#include <sys/time.h>
#include <stdlib.h>
#include "gpib/ib.h"

enum {
	VOLT_HI_POS = 0,
	VOLT_HI_NEG,
	VOLT_LO_POS,
	VOLT_LO_NEG,

	CURR_HI_POS,
	CURR_HI_NEG,
	CURR_LO_POS,
	CURR_LO_NEG,
};

int main(int argc, char *argv[])
{
	int send_eoi = 0;
	int eos_mode = 0;
	int timeout  = T1ms;
 
	if(argc < 2){
		fprintf(stderr, "bop <addr> <value 000 - 999>\n");
		return 1;
	}

	int pad = atoi(argv[1]);
	int val = 0;
	int ren = 0;
	int lim = 99;
	
	if(argc == 3){
		val = atoi(argv[2]);
		ren = 1;
	}
	
	if (val > 999 ) {
		val = 999;
	} else if (val < -999 ) {
		val = -999;
	}
	int mode;
	if(val >= 0) {
		mode = VOLT_HI_POS;
	} else {
		val  = -1 * val;
		mode = VOLT_HI_NEG;
	}

	fprintf(stderr, "addr %2d  REN %d value %d  mode %d\n", pad, ren, val, mode);

	int ud = ibdev( 0, pad, 0, timeout, send_eoi, eos_mode );
	if( ud < 0 ) {
		fprintf( stderr, "ibdev() failed: %s\n", gpib_error_string( ThreadIberr() ) );
		return -1;
	}
	
	int status = ibsre(0, ren);
	if (status & ERR) {
		fprintf(stderr, "ibsre() failed: %s\n", gpib_error_string(ThreadIberr()));
		return -1;
	}
	
	char msg[7];
	
	msg[0] = '0' + mode;
	
	msg[1] = '0' +  val                      / 100;
	msg[2] = '0' + (val - (val / 100 * 100)) /  10;
	msg[3] = '0' + (val - (val /  10 *  10)) /   1;

	// set limit
	msg[4] = '0' +  lim                      /  10;
	msg[5] = '0' + (lim - (lim /  10 *  10)) /   1;

	msg[4] = '9'; 
	msg[5] = '9'; 

	msg[6] = 0; 

	fprintf(stderr, "msg [%s]\n", msg);
	 
	status = ibwrt(ud, msg, 6);
	if (status & ERR) {
		fprintf(stderr, "ibwrt() failed: %s\n", gpib_error_string(ThreadIberr()));
		return -1;
	}

	return 0;
}
