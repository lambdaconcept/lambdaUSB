#ifndef __USB_DESC_H_
#define __USB_DESC_H_


typedef unsigned char u8;
typedef unsigned short u16;


#define USB_REQ_DIR_MASK                        (1 << 7) /* Bit 7=1: Direction bit */
#define USB_REQ_DIR_IN                          (1 << 7) /* Bit 7=1: Device-to-host */
#define USB_REQ_DIR_OUT                         (0 << 7) /* Bit 7=0: Host-to-device */
#define USB_REQ_ISIN(type)                      (((type) & USB_REQ_DIR_MASK) != 0)
#define USB_REQ_ISOUT(type)                     (((type) & USB_REQ_DIR_MASK) == 0)

/* Control Setup Packet.  Byte 1 = Standard Request Codes */

#define USB_REQ_GETSTATUS                       (0x00)
#define USB_REQ_CLEARFEATURE                    (0x01)
#define USB_REQ_SETFEATURE                      (0x03)
#define USB_REQ_SETADDRESS                      (0x05)
#define USB_REQ_GETDESCRIPTOR                   (0x06)
#define USB_REQ_SETDESCRIPTOR                   (0x07)
#define USB_REQ_GETCONFIGURATION                (0x08)
#define USB_REQ_SETCONFIGURATION                (0x09)
#define USB_REQ_GETINTERFACE                    (0x0a)
#define USB_REQ_SETINTERFACE                    (0x0b)
#define USB_REQ_SYNCHFRAME                      (0x0c)

#define USB_REQ_SETENCRYPTION                   (0x0d) /* Wireless USB */
#define USB_REQ_GETENCRYPTION                   (0x0e)
#define USB_REQ_SETHANDSHAKE                    (0x0f)
#define USB_REQ_GETHANDSHAKE                    (0x10)
#define USB_REQ_SETCONNECTION                   (0x11)
#define USB_REQ_SETSECURITYDATA                 (0x12)
#define USB_REQ_GETSECURITYDATA                 (0x13)
#define USB_REQ_SETWUSBDATA                     (0x14)
#define USB_REQ_LOOPBACKDATAWRITE               (0x15)
#define USB_REQ_LOOPBACKDATAREAD                (0x16)
#define USB_REQ_SETINTERFACEDS                  (0x17)

/* Descriptor types */

#define USB_DESC_TYPE_DEVICE                    (0x01)
#define USB_DESC_TYPE_CONFIG                    (0x02)
#define USB_DESC_TYPE_STRING                    (0x03)
#define USB_DESC_TYPE_INTERFACE                 (0x04)
#define USB_DESC_TYPE_ENDPOINT                  (0x05)
#define USB_DESC_TYPE_DEVICEQUALIFIER           (0x06)
#define USB_DESC_TYPE_OTHERSPEEDCONFIG          (0x07)
#define USB_DESC_TYPE_INTERFACEPOWER            (0x08)
#define USB_DESC_TYPE_OTG                       (0x09)
#define USB_DESC_TYPE_DEBUG                     (0x0a)
#define USB_DESC_TYPE_INTERFACEASSOCIATION      (0x0b)
#define USB_DESC_TYPE_SECURITY                  (0x0c)
#define USB_DESC_TYPE_KEY                       (0x0d)
#define USB_DESC_TYPE_ENCRYPTION_TYPE           (0x0e)
#define USB_DESC_TYPE_BOS                       (0x0f)
#define USB_DESC_TYPE_DEVICECAPABILITY          (0x10)
#define USB_DESC_TYPE_WIRELESS_ENDPOINTCOMP     (0x11)
#define USB_DESC_TYPE_CSDEVICE                  (0x21)
#define USB_DESC_TYPE_CSCONFIG                  (0x22)
#define USB_DESC_TYPE_CSSTRING                  (0x23)
#define USB_DESC_TYPE_CSINTERFACE               (0x24)
#define USB_DESC_TYPE_CSENDPOINT                (0x25)






struct usb_endpoint_descriptor {
	u8 bLength;
	u8 bDescriptorType;	/* 0x5 */
	u8 bEndpointAddress;
	u8 bmAttributes;
	u16 wMaxPacketSize;
	u8 bInterval;
} __attribute__ ((packed));

struct usb_interface_descriptor {
	u8 bLength;
	u8 bDescriptorType;	/* 0x04 */
	u8 bInterfaceNumber;
	u8 bAlternateSetting;
	u8 bNumEndpoints;
	u8 bInterfaceClass;
	u8 bInterfaceSubClass;
	u8 bInterfaceProtocol;
	u8 iInterface;
} __attribute__ ((packed));

struct usb_configuration_descriptor {
	u8 bLength;
	u8 bDescriptorType;	/* 0x2 */
	u16 wTotalLength;
	u8 bNumInterfaces;
	u8 bConfigurationValue;
	u8 iConfiguration;
	u8 bmAttributes;
	u8 bMaxPower;
} __attribute__ ((packed));

struct usb_device_descriptor {
	u8 bLength;
	u8 bDescriptorType;	/* 0x01 */
	u16 bcdUSB;
	u8 bDeviceClass;
	u8 bDeviceSubClass;
	u8 bDeviceProtocol;
	u8 bMaxPacketSize0;
	u16 idVendor;
	u16 idProduct;
	u16 bcdDevice;
	u8 iManufacturer;
	u8 iProduct;
	u8 iSerialNumber;
	u8 bNumConfigurations;
} __attribute__ ((packed));



struct usb_string_descriptor {
	u8 bLength;
	u8 bDescriptorType;
	u16 wData[0];
} __attribute__ ((packed));

struct usb_generic_descriptor {
	u8 bLength;
	u8 bDescriptorType;
	u8 bDescriptorSubtype;
} __attribute__ ((packed));

struct usb_qualifier_descriptor {
	u8 bLength;
	u8 bDescriptorType;	/* 0x06 */
	u16 bcdUSB;
	u8 bDeviceClass;
	u8 bDeviceSubClass;
	u8 bDeviceProtocol;
	u8 bMaxPacketSize0;
	u8 bNumConfigurations;
	u8 bReserved;
} __attribute__ ((packed));


#endif
