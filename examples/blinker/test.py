import time
import usb.core


def main():
    dev = usb.core.find(idVendor=0x05ac, idProduct=0x5678)
    if dev is None:
        raise ValueError("Device 0x05ac:0x5678 was not found.")

    dev.set_configuration()

    rgb = 0b100
    for i in range(32):
        dev.write(1, rgb.to_bytes(1, byteorder='big'), 1)
        print(f"[OUT] data = {rgb}");
        rgb = 0b100 if rgb == 0b001 else rgb >> 1
        time.sleep(1) # wait 1s to see the led change its color


if __name__ == "__main__":
    main()
