#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include "usbconf.h"


int main()
{
	FILE *py;
	int offset=0;
	unsigned char *buf, *pnt;
	buf = malloc(4096);
	pnt = buf;

	py = fopen("config.py", "w");
	fprintf(py, "# Generated with genconfig (tools/genconfig)\n");
	fprintf(py, "descriptor_map = {\n");

	fprintf(py, "\t0x01: {0: (%d,  %ld)},\n",offset,  sizeof(device_desc));
	memcpy(buf + offset, &device_desc, sizeof(device_desc));
	offset += sizeof(device_desc);

	fprintf(py, "\t0x02: {0: (%d,  %d)},\n",offset,  usb_config_table[0].len);
	memcpy(buf + offset, usb_config_table[0].config, usb_config_table[0].len);
	offset += usb_config_table[0].len;

	fprintf(py, "\t0x03: {\n");
	fprintf(py, "\t\t 0: (%d, 4),\n", offset);

	buf[offset++] = 4;
	buf[offset++] = 3;
	buf[offset++] = CONFIG_USB_LANG_VAL & 0xff;
	buf[offset++] = (CONFIG_USB_LANG_VAL >> 8) & 0xff;

	for(int i =1; i < CONFIG_USB_NSTRINGS + 1; i++){
		fprintf(py,"\t\t %d: (%d, %ld),\n" ,i, offset, sizeof(struct usb_string_descriptor) + strlen(string_tab[i])*2);

		buf[offset++] = sizeof(struct usb_string_descriptor) + strlen(string_tab[i])*2;
		buf[offset++] = 3;
		for(int j =0; j < strlen(string_tab[i]); j++){
			buf[offset++] = string_tab[i][j];
			buf[offset++]=0;
		}
	}
	fprintf(py, "\t},\n");
	fprintf(py,"\t0x06: {0: (%d, %ld)},\n", offset, sizeof(qualifier_desc));
	memcpy(buf + offset, &qualifier_desc, sizeof(qualifier_desc));
	offset += sizeof(qualifier_desc);

	/*debug qualifier*/
	fprintf(py, "\t0x0a: {0: (%d, %d)},\n", offset, 2);
	buf[offset++] = 2;
	buf[offset++] = USB_DESC_TYPE_DEBUG;

	fprintf(py, "}\n\n");


	printf("total = %d\n", offset);

	fprintf(py, "rom_init = [ ");
	for(int i=0; i < offset; i++){
		if(i%8 == 0)
			fprintf(py,"\n\t");
		fprintf(py, "0x%02x, ", buf[i]);
	}
	fprintf(py, "\n]\n");

	free(buf);
	return 0;
}
