// gcc test.c -o test -lusb-1.0

#include <libusb-1.0/libusb.h>
#include <stdio.h>
#include <unistd.h>


int main(void)
{
	libusb_context *ctx;
       	libusb_init(&ctx);

	libusb_device_handle *devh = libusb_open_device_with_vid_pid(ctx, 0x05ac, 0x5678);
	if (!devh) {
		fprintf(stderr, "failed to open device 05ac:5678\n");
		return -1;
	}
	libusb_claim_interface(devh, 0);

	uint8_t rgb = 4;
	for (size_t i = 0; i < 32; i++) {
		libusb_bulk_transfer(devh, 0x1, &rgb, 1, NULL, 0);
		printf("[OUT] data = %d\n", rgb);
		rgb = (rgb == 1) ? 4 : (rgb >> 1);
		sleep(1); // wait 1s to see the led change its color
	}

	libusb_close(devh);
	libusb_exit(ctx);
	return 0;
}
