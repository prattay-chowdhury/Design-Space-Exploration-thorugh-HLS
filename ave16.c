/*****************************************************************
 * [Abstract]: Average of last 16 values
 * [Compile Option]:
 *   BDL:  For Cyber. (bdlpars -DBDL foo.c)
 *     C:  For C simulation with ANSI C compiler. (gcc -DC foo.c)
 * 
 ****************************************************************/
#include <bdlstd.h>
#include "attr.h"
#define SIZE 16


in ter(0:8)  in0;
out ter(0:8)  out0;
var(0:8)  data[SIZE] /* attr1 */ = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};


process ave16(){

   /* Variables declaration */
    int  out0_v, sum,  i; 

	/* attr2 */
        for (i = SIZE-1; i > 0; i--) { 	
            data[i] = data[i- 1];
        }
	
    data[0] = in0;
    sum= data[0]; 	
        
      /* attr3 */
      for (i= 1; i< SIZE; i++) { 	
            sum += data[i]; 	
        }
        out0_v= sum / 16; 
        out0 = out0_v;	

    return (0); 	
}
