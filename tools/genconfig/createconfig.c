#include <stdio.h>
#include <string.h>
#include <stdlib.h>



void generate_kconfig(int max_conf, int max_if, int max_ep, int max_string)
{
	FILE *kconfig;
	kconfig = fopen("Kconfig", "w");
	char filename[100];


	fprintf(kconfig, "mainmenu \"USB Descriptors\"\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "menu \"USB Device Descriptor\"\n");
	fprintf(kconfig, "config USB_DEVICE_USB_VERSION\n");
	fprintf(kconfig, "\thex \"USB Version\"\n");
	fprintf(kconfig, "\tdefault 0x200\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tUSB Specification Release Number in\n");
	fprintf(kconfig, "\t\tBinary-C oded Decimal (i.e., 2.10 is 210H).\n");
	fprintf(kconfig, "\t\tThis field identifies the release of the USB\n");
	fprintf(kconfig, "\t\tSpecification with which the device and its\n");
	fprintf(kconfig, "\t\tdescriptors are compliant.\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "choice\n");
	fprintf(kconfig, "prompt \"USB Device Class\"\n");
	fprintf(kconfig, "config USB_DEVICE_CLASSID_DEVICE\n");
	fprintf(kconfig, "\tbool \"Defined at Interface Level\"\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tThis base class is defined to be used in Device\n");
	fprintf(kconfig, "\t\tDescriptors to indicate that class information\n");
	fprintf(kconfig, "\t\tshould be determined from the Interface Descriptors\n");
	fprintf(kconfig, "\t\tin the device. There is one class code definition\n");
	fprintf(kconfig, "\t\tin this base class. All other values are reserved.\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "\t\tThis value is also used in Interface Descriptors\n");
	fprintf(kconfig, "\t\tto indicate a null class code triple.\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_CLASS_CDC\n");
	fprintf(kconfig, "\tbool \"Communications and CDC Control\"\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tThis base class is defined for devices that conform to\n");
	fprintf(kconfig, "\t\tthe Communications Device Class Specification found on\n");
	fprintf(kconfig, "\t\tthe USB-IF website. That specification defines the usable\n");
	fprintf(kconfig, "\t\tset of SubClass and Protocol values. Values outside of\n");
	fprintf(kconfig, "\t\tthat defined spec are reserved. Note that the Communication\n");
	fprintf(kconfig, "\t\tDevice Class spec requires some class code values (triples)\n");
	fprintf(kconfig, "\t\tto be used in Device Descriptors and some to be used in\n");
	fprintf(kconfig, "\t\tInterface Descriptors.\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_CLASS_HUB\n");
	fprintf(kconfig, "\tbool \"USB HUB\"\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tThis base class is defined for devices that are USB\n");
	fprintf(kconfig, "\t\thubs and conform to the definition in the USB specification.\n");
	fprintf(kconfig, "\t\tThat specification defines the complete triples as shown below.\n");
	fprintf(kconfig, "\t\tAll other values are reserved. These class codes can only be\n");
	fprintf(kconfig, "\t\tused in Device Descriptors.\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_CLASS_BILLBOARD\n");
	fprintf(kconfig, "\tbool \"Billboard Device Class\"\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tBillBoard Device Class\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_CLASS_DIAGNOSTIC\n");
	fprintf(kconfig, "\tbool \"Diagnostic Device\"\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tThis base class is defined for devices that diagnostic\n");
	fprintf(kconfig, "\t\tdevices. This class code can be used in Device or Interface\n");
	fprintf(kconfig, "\t\tDescriptors. Trace is a form of debugging where processor\n");
	fprintf(kconfig, "\t\tor system activity is made externally visible in real-time\n");
	fprintf(kconfig, "\t\tor stored and later retrieved for viewing by an applications\n");
	fprintf(kconfig, "\t\tdeveloper, applications program, or, external equipment\n");
	fprintf(kconfig, "\t\tspecializing observing system activity. Design for Debug or\n");
	fprintf(kconfig, "\t\tTest (Dfx). This refers to a logic block that provides debug\n");
	fprintf(kconfig, "\t\tor test support (E.g. via Test Access Port (TAP)). DvC: Debug\n");
	fprintf(kconfig, "\t\tCapability on the USB device (Device Capability)\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_CLASS_MISCELLANEOUS\n");
	fprintf(kconfig, "\tbool \"Miscellaneous\"\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tThis base class is defined for miscellaneous device definitions.\n");
	fprintf(kconfig, "\t\tValues not shown in the table below are reserved. The use of\n");
	fprintf(kconfig, "\t\tthese class codes (Device or Interface descriptor) are\n");
	fprintf(kconfig, "\t\tspecifically annotated in each entry below.\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_CLASS_VENDOR\n");
	fprintf(kconfig, "\tbool \"Vendor Specific\"\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tThis base class is defined for vendors to use as they please.\n");
	fprintf(kconfig, "\t\tThese class codes can be used in both Device and Interface Descriptors.\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_CLASS_CUSTOM\n");
	fprintf(kconfig, "\tbool \"Select custom value\"\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tChoise the value yourself\n");
	fprintf(kconfig, "endchoice\n");
	fprintf(kconfig, "if USB_DEVICE_CLASS_CUSTOM\n");
	fprintf(kconfig, "config USB_DEVICE_CLASS_CUSTOM_VAL\n");
	fprintf(kconfig, "\thex \"Custom Device Class value\"\n");
	fprintf(kconfig, "\trange 0 255\n");
	fprintf(kconfig, "\tdefault 0x00\n");
	fprintf(kconfig, "endif\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_CLASS_VAL\n");
	fprintf(kconfig, "\thex\n");
	fprintf(kconfig, "\trange 0 255\n");
	fprintf(kconfig, "\tdefault 0 if USB_DEVICE_CLASSID_DEVICE\n");
	fprintf(kconfig, "\tdefault 2 if USB_DEVICE_CLASS_CDC\n");
	fprintf(kconfig, "\tdefault 9 if USB_DEVICE_CLASS_HUB\n");
	fprintf(kconfig, "\tdefault 0x11 if USB_DEVICE_CLASS_BILLBOARD\n");
	fprintf(kconfig, "\tdefault 0xdc if USB_DEVICE_CLASS_DIAGNOSTIC\n");
	fprintf(kconfig, "\tdefault 0xef if USB_DEVICE_CLASS_MISCELLANEOUS\n");
	fprintf(kconfig, "\tdefault 0xff if USB_DEVICE_CLASS_VENDOR\n");
	fprintf(kconfig, "\tdefault USB_DEVICE_CLASS_CUSTOM_VAL if USB_DEVICE_CLASS_CUSTOM\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_SUBCLASS\n");
	fprintf(kconfig, "\tint \"USB Subclass\"\n");
	fprintf(kconfig, "\tdefault 0\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tSubclass code (assigned by the USB-IF).\n");
	fprintf(kconfig, "\t\tThese codes are qualified by the value of\n");
	fprintf(kconfig, "\t\tthe bDeviceClass field.\n");
	fprintf(kconfig, "\t\tIf the bDeviceClass field is reset to zero,\n");
	fprintf(kconfig, "\t\tthis field must also be reset to zero.\n");
	fprintf(kconfig, "\t\tIf the bDeviceClass field is not set to FFH,\n");
	fprintf(kconfig, "\t\tall values are reserved for assignment by\n");
	fprintf(kconfig, "\t\tthe USB-IF.\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_PROTOCOL\n");
	fprintf(kconfig, "\tint \"USB Protocol\"\n");
	fprintf(kconfig, "\tdefault 0\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tProtocol code (assigned by the USB-IF).\n");
	fprintf(kconfig, "\t\tThese codes are qualified by the value of\n");
	fprintf(kconfig, "\t\tthe bDeviceClass and the\n");
	fprintf(kconfig, "\t\tbDeviceSubClass fields. If a device\n");
	fprintf(kconfig, "\t\tsupports class-specific protocols on a\n");
	fprintf(kconfig, "\t\tdevice basis as opposed to an interface\n");
	fprintf(kconfig, "\t\tbasis, this code identifies the protocols\n");
	fprintf(kconfig, "\t\tthat the device uses as defined by the\n");
	fprintf(kconfig, "\t\tspecification of the device class.\n");
	fprintf(kconfig, "\t\tIf this field is reset to zero, the device\n");
	fprintf(kconfig, "\t\tdoes not use class-specific protocols on a\n");
	fprintf(kconfig, "\t\tdevice basis. However, it may use classspecific protocols on an interface basis.\n");
	fprintf(kconfig, "\t\tIf this field is set to FFH, the device uses a\n");
	fprintf(kconfig, "\t\tvendor-specific protocol on a device basis.\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_MXPACKETSIZE\n");
	fprintf(kconfig, "\tint \"EP0 Max Packet Size\"\n");
	fprintf(kconfig, "\tdefault 64\n");
	fprintf(kconfig, "\trange 8 512\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tMaximum packet size for endpoint zero\n");
	fprintf(kconfig, "\t\t(only 8, 16, 32, or 64 are valid)\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_VENDORID\n");
	fprintf(kconfig, "\thex \"Vendor ID\"\n");
	fprintf(kconfig, "\tdefault 0x1234\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tVendor ID (assigned by the USB-IF)\n");
	fprintf(kconfig, "config USB_DEVICE_PRODUCTID\n");
	fprintf(kconfig, "\thex \"Product ID\"\n");
	fprintf(kconfig, "\tdefault 0x5678\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tProduct ID (assigned by the manufacturer)\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_DEVICEID\n");
	fprintf(kconfig, "\thex \"Device ID\"\n");
	fprintf(kconfig, "\tdefault 0x9ABC\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tDevice release number in binary-coded decimal\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_IMFGR\n");
	fprintf(kconfig, "\tint \"Manufacturer String Index\"\n");
	fprintf(kconfig, "\tdefault 0\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tIndex of string descriptor describing manufacturer\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_IPRODUCT\n");
	fprintf(kconfig, "\tint \"Product String Index\"\n");
	fprintf(kconfig, "\tdefault 0\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tIndex of string descriptor describing product\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_ISERNO\n");
	fprintf(kconfig, "\tint \"Serial Number String Index\"\n");
	fprintf(kconfig, "\tdefault 0\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tIndex of string descriptor describing the device’s serial number\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "config USB_DEVICE_NCONFIGS\n");
	fprintf(kconfig, "\tint \"Number of Configuration\"\n");
	fprintf(kconfig, "\trange 1 255\n");
	fprintf(kconfig, "\t---help---\n");
	fprintf(kconfig, "\t\tNumber of possible configurations\n");
	fprintf(kconfig, "\n");
	fprintf(kconfig, "endmenu\n");
	fprintf(kconfig, "\n");

	fprintf(kconfig, "choice\n");
	fprintf(kconfig, "\tprompt \"USB Language ID\"\n");
	fprintf(kconfig, "\tdefault USB_LANG_ENGLISH_UNITED_STATES\n");

	fprintf(kconfig, "config USB_LANG_USER_SELECT\n");
	fprintf(kconfig, "\tbool \"User Select\"\n");
	fprintf(kconfig, "config USB_LANG_AFRIKAANS\n");
	fprintf(kconfig, "\tbool \"Afrikaans\"\n");
	fprintf(kconfig, "config USB_LANG_ALBANIAN\n");
	fprintf(kconfig, "\tbool \"Albanian\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_SAUDI_ARABIA\n");
	fprintf(kconfig, "\tbool \"Arabic (Saudi Arabia)\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_IRAQ\n");
	fprintf(kconfig, "\tbool \"Arabic (Iraq)\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_EGYPT\n");
	fprintf(kconfig, "\tbool \"Arabic (Egypt)\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_LIBYA\n");
	fprintf(kconfig, "\tbool \"Arabic (Libya)\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_ALGERIA\n");
	fprintf(kconfig, "\tbool \"Arabic (Algeria)\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_MOROCCO\n");
	fprintf(kconfig, "\tbool \"Arabic (Morocco)\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_TUNISIA\n");
	fprintf(kconfig, "\tbool \"Arabic (Tunisia)\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_OMAN\n");
	fprintf(kconfig, "\tbool \"Arabic (Oman)\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_YEMEN\n");
	fprintf(kconfig, "\tbool \"Arabic (Yemen)\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_SYRIA\n");
	fprintf(kconfig, "\tbool \"Arabic (Syria)\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_JORDAN\n");
	fprintf(kconfig, "\tbool \"Arabic (Jordan)\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_LEBANON\n");
	fprintf(kconfig, "\tbool \"Arabic (Lebanon)\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_KUWAIT\n");
	fprintf(kconfig, "\tbool \"Arabic (Kuwait)\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_UAE\n");
	fprintf(kconfig, "\tbool \"Arabic (U.A.E.)\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_BAHRAIN\n");
	fprintf(kconfig, "\tbool \"Arabic (Bahrain)\"\n");
	fprintf(kconfig, "config USB_LANG_ARABIC_QATAR\n");
	fprintf(kconfig, "\tbool \"Arabic (Qatar)\"\n");
	fprintf(kconfig, "config USB_LANG_ARMENIAN\n");
	fprintf(kconfig, "\tbool \"Armenian.\"\n");
	fprintf(kconfig, "config USB_LANG_ASSAMESE\n");
	fprintf(kconfig, "\tbool \"Assamese.\"\n");
	fprintf(kconfig, "config USB_LANG_AZERI_LATIN\n");
	fprintf(kconfig, "\tbool \"Azeri (Latin)\"\n");
	fprintf(kconfig, "config USB_LANG_AZERI_CYRILLIC\n");
	fprintf(kconfig, "\tbool \"Azeri (Cyrillic)\"\n");
	fprintf(kconfig, "config USB_LANG_BASQUE\n");
	fprintf(kconfig, "\tbool \"Basque\"\n");
	fprintf(kconfig, "config USB_LANG_BELARUSSIAN\n");
	fprintf(kconfig, "\tbool \"Belarussian\"\n");
	fprintf(kconfig, "config USB_LANG_BENGALI\n");
	fprintf(kconfig, "\tbool \"Bengali.\"\n");
	fprintf(kconfig, "config USB_LANG_BULGARIAN\n");
	fprintf(kconfig, "\tbool \"Bulgarian\"\n");
	fprintf(kconfig, "config USB_LANG_BURMESE\n");
	fprintf(kconfig, "\tbool \"Burmese\"\n");
	fprintf(kconfig, "config USB_LANG_CATALAN\n");
	fprintf(kconfig, "\tbool \"Catalan\"\n");
	fprintf(kconfig, "config USB_LANG_CHINESE_TAIWAN\n");
	fprintf(kconfig, "\tbool \"Chinese (Taiwan)\"\n");
	fprintf(kconfig, "config USB_LANG_CHINESE_PRC\n");
	fprintf(kconfig, "\tbool \"Chinese (PRC)\"\n");
	fprintf(kconfig, "config USB_LANG_CHINESE_HONG_KONG_SAR_PRC\n");
	fprintf(kconfig, "\tbool \"Chinese (Hong Kong SAR, PRC)\"\n");
	fprintf(kconfig, "config USB_LANG_CHINESE_SINGAPORE\n");
	fprintf(kconfig, "\tbool \"Chinese (Singapore)\"\n");
	fprintf(kconfig, "config USB_LANG_CHINESE_MACAU_SAR\n");
	fprintf(kconfig, "\tbool \"Chinese (Macau SAR)\"\n");
	fprintf(kconfig, "config USB_LANG_CROATIAN\n");
	fprintf(kconfig, "\tbool \"Croatian\"\n");
	fprintf(kconfig, "config USB_LANG_CZECH\n");
	fprintf(kconfig, "\tbool \"Czech\"\n");
	fprintf(kconfig, "config USB_LANG_DANISH\n");
	fprintf(kconfig, "\tbool \"Danish\"\n");
	fprintf(kconfig, "config USB_LANG_DUTCH_NETHERLANDS\n");
	fprintf(kconfig, "\tbool \"Dutch (Netherlands)\"\n");
	fprintf(kconfig, "config USB_LANG_DUTCH_BELGIUM\n");
	fprintf(kconfig, "\tbool \"Dutch (Belgium)\"\n");
	fprintf(kconfig, "config USB_LANG_ENGLISH_UNITED_STATES\n");
	fprintf(kconfig, "\tbool \"English (United States)\"\n");
	fprintf(kconfig, "config USB_LANG_ENGLISH_UNITED_KINGDOM\n");
	fprintf(kconfig, "\tbool \"English (United Kingdom)\"\n");
	fprintf(kconfig, "config USB_LANG_ENGLISH_AUSTRALIAN\n");
	fprintf(kconfig, "\tbool \"English (Australian)\"\n");
	fprintf(kconfig, "config USB_LANG_ENGLISH_CANADIAN\n");
	fprintf(kconfig, "\tbool \"English (Canadian)\"\n");
	fprintf(kconfig, "config USB_LANG_ENGLISH_NEW_ZEALAND\n");
	fprintf(kconfig, "\tbool \"English (New Zealand)\"\n");
	fprintf(kconfig, "config USB_LANG_ENGLISH_IRELAND\n");
	fprintf(kconfig, "\tbool \"English (Ireland)\"\n");
	fprintf(kconfig, "config USB_LANG_ENGLISH_SOUTH_AFRICA\n");
	fprintf(kconfig, "\tbool \"English (South Africa)\"\n");
	fprintf(kconfig, "config USB_LANG_ENGLISH_JAMAICA\n");
	fprintf(kconfig, "\tbool \"English (Jamaica)\"\n");
	fprintf(kconfig, "config USB_LANG_ENGLISH_CARIBBEAN\n");
	fprintf(kconfig, "\tbool \"English (Caribbean)\"\n");
	fprintf(kconfig, "config USB_LANG_ENGLISH_BELIZE\n");
	fprintf(kconfig, "\tbool \"English (Belize)\"\n");
	fprintf(kconfig, "config USB_LANG_ENGLISH_TRINIDAD\n");
	fprintf(kconfig, "\tbool \"English (Trinidad)\"\n");
	fprintf(kconfig, "config USB_LANG_ENGLISH_ZIMBABWE\n");
	fprintf(kconfig, "\tbool \"English (Zimbabwe)\"\n");
	fprintf(kconfig, "config USB_LANG_ENGLISH_PHILIPPINES\n");
	fprintf(kconfig, "\tbool \"English (Philippines)\"\n");
	fprintf(kconfig, "config USB_LANG_ESTONIAN\n");
	fprintf(kconfig, "\tbool \"Estonian\"\n");
	fprintf(kconfig, "config USB_LANG_FAEROESE\n");
	fprintf(kconfig, "\tbool \"Faeroese\"\n");
	fprintf(kconfig, "config USB_LANG_FARSI\n");
	fprintf(kconfig, "\tbool \"Farsi\"\n");
	fprintf(kconfig, "config USB_LANG_FINNISH\n");
	fprintf(kconfig, "\tbool \"Finnish\"\n");
	fprintf(kconfig, "config USB_LANG_FRENCH_STANDARD\n");
	fprintf(kconfig, "\tbool \"French (Standard)\"\n");
	fprintf(kconfig, "config USB_LANG_FRENCH_BELGIAN\n");
	fprintf(kconfig, "\tbool \"French (Belgian)\"\n");
	fprintf(kconfig, "config USB_LANG_FRENCH_CANADIAN\n");
	fprintf(kconfig, "\tbool \"French (Canadian)\"\n");
	fprintf(kconfig, "config USB_LANG_FRENCH_SWITZERLAND\n");
	fprintf(kconfig, "\tbool \"French (Switzerland)\"\n");
	fprintf(kconfig, "config USB_LANG_FRENCH_LUXEMBOURG\n");
	fprintf(kconfig, "\tbool \"French (Luxembourg)\"\n");
	fprintf(kconfig, "config USB_LANG_FRENCH_MONACO\n");
	fprintf(kconfig, "\tbool \"French (Monaco)\"\n");
	fprintf(kconfig, "config USB_LANG_GEORGIAN\n");
	fprintf(kconfig, "\tbool \"Georgian.\"\n");
	fprintf(kconfig, "config USB_LANG_GERMAN_STANDARD\n");
	fprintf(kconfig, "\tbool \"German (Standard)\"\n");
	fprintf(kconfig, "config USB_LANG_GERMAN_SWITZERLAND\n");
	fprintf(kconfig, "\tbool \"German (Switzerland)\"\n");
	fprintf(kconfig, "config USB_LANG_GERMAN_AUSTRIA\n");
	fprintf(kconfig, "\tbool \"German (Austria)\"\n");
	fprintf(kconfig, "config USB_LANG_GERMAN_LUXEMBOURG\n");
	fprintf(kconfig, "\tbool \"German (Luxembourg)\"\n");
	fprintf(kconfig, "config USB_LANG_GERMAN_LIECHTENSTEIN\n");
	fprintf(kconfig, "\tbool \"German (Liechtenstein)\"\n");
	fprintf(kconfig, "config USB_LANG_GREEK\n");
	fprintf(kconfig, "\tbool \"Greek\"\n");
	fprintf(kconfig, "config USB_LANG_GUJARATI\n");
	fprintf(kconfig, "\tbool \"Gujarati.\"\n");
	fprintf(kconfig, "config USB_LANG_HEBREW\n");
	fprintf(kconfig, "\tbool \"Hebrew\"\n");
	fprintf(kconfig, "config USB_LANG_HINDI\n");
	fprintf(kconfig, "\tbool \"Hindi.\"\n");
	fprintf(kconfig, "config USB_LANG_HUNGARIAN\n");
	fprintf(kconfig, "\tbool \"Hungarian\"\n");
	fprintf(kconfig, "config USB_LANG_ICELANDIC\n");
	fprintf(kconfig, "\tbool \"Icelandic\"\n");
	fprintf(kconfig, "config USB_LANG_INDONESIAN\n");
	fprintf(kconfig, "\tbool \"Indonesian\"\n");
	fprintf(kconfig, "config USB_LANG_ITALIAN_STANDARD\n");
	fprintf(kconfig, "\tbool \"Italian (Standard)\"\n");
	fprintf(kconfig, "config USB_LANG_ITALIAN_SWITZERLAND\n");
	fprintf(kconfig, "\tbool \"Italian (Switzerland)\"\n");
	fprintf(kconfig, "config USB_LANG_JAPANESE\n");
	fprintf(kconfig, "\tbool \"Japanese\"\n");
	fprintf(kconfig, "config USB_LANG_KANNADA\n");
	fprintf(kconfig, "\tbool \"Kannada.\"\n");
	fprintf(kconfig, "config USB_LANG_KASHMIRI_INDIA\n");
	fprintf(kconfig, "\tbool \"Kashmiri (India)\"\n");
	fprintf(kconfig, "config USB_LANG_KAZAKH\n");
	fprintf(kconfig, "\tbool \"Kazakh\"\n");
	fprintf(kconfig, "config USB_LANG_KONKANI\n");
	fprintf(kconfig, "\tbool \"Konkani.\"\n");
	fprintf(kconfig, "config USB_LANG_KOREAN\n");
	fprintf(kconfig, "\tbool \"Korean\"\n");
	fprintf(kconfig, "config USB_LANG_KOREAN_JOHAB\n");
	fprintf(kconfig, "\tbool \"Korean (Johab)\"\n");
	fprintf(kconfig, "config USB_LANG_LATVIAN\n");
	fprintf(kconfig, "\tbool \"Latvian\"\n");
	fprintf(kconfig, "config USB_LANG_LITHUANIAN\n");
	fprintf(kconfig, "\tbool \"Lithuanian\"\n");
	fprintf(kconfig, "config USB_LANG_LITHUANIAN_CLASSIC\n");
	fprintf(kconfig, "\tbool \"Lithuanian (Classic)\"\n");
	fprintf(kconfig, "config USB_LANG_MACEDONIAN\n");
	fprintf(kconfig, "\tbool \"Macedonian\"\n");
	fprintf(kconfig, "config USB_LANG_MALAY_MALAYSIAN\n");
	fprintf(kconfig, "\tbool \"Malay (Malaysian)\"\n");
	fprintf(kconfig, "config USB_LANG_MALAY_BRUNEI_DARUSSALAM\n");
	fprintf(kconfig, "\tbool \"Malay (Brunei Darussalam)\"\n");
	fprintf(kconfig, "config USB_LANG_MALAYALAM\n");
	fprintf(kconfig, "\tbool \"Malayalam.\"\n");
	fprintf(kconfig, "config USB_LANG_MANIPURI\n");
	fprintf(kconfig, "\tbool \"Manipuri\"\n");
	fprintf(kconfig, "config USB_LANG_MARATHI\n");
	fprintf(kconfig, "\tbool \"Marathi.\"\n");
	fprintf(kconfig, "config USB_LANG_NEPALI_INDIA\n");
	fprintf(kconfig, "\tbool \"Nepali (India).\"\n");
	fprintf(kconfig, "config USB_LANG_NORWEGIAN_BOKMAL\n");
	fprintf(kconfig, "\tbool \"Norwegian (Bokmal)\"\n");
	fprintf(kconfig, "config USB_LANG_NORWEGIAN_NYNORSK\n");
	fprintf(kconfig, "\tbool \"Norwegian (Nynorsk)\"\n");
	fprintf(kconfig, "config USB_LANG_ORIYA\n");
	fprintf(kconfig, "\tbool \"Oriya.\"\n");
	fprintf(kconfig, "config USB_LANG_POLISH\n");
	fprintf(kconfig, "\tbool \"Polish\"\n");
	fprintf(kconfig, "config USB_LANG_PORTUGUESE_BRAZIL\n");
	fprintf(kconfig, "\tbool \"Portuguese (Brazil)\"\n");
	fprintf(kconfig, "config USB_LANG_PORTUGUESE_STANDARD\n");
	fprintf(kconfig, "\tbool \"Portuguese (Standard)\"\n");
	fprintf(kconfig, "config USB_LANG_PUNJABI\n");
	fprintf(kconfig, "\tbool \"Punjabi.\"\n");
	fprintf(kconfig, "config USB_LANG_ROMANIAN\n");
	fprintf(kconfig, "\tbool \"Romanian\"\n");
	fprintf(kconfig, "config USB_LANG_RUSSIAN\n");
	fprintf(kconfig, "\tbool \"Russian\"\n");
	fprintf(kconfig, "config USB_LANG_SANSKRIT\n");
	fprintf(kconfig, "\tbool \"Sanskrit.\"\n");
	fprintf(kconfig, "config USB_LANG_SERBIAN_CYRILLIC\n");
	fprintf(kconfig, "\tbool \"Serbian (Cyrillic)\"\n");
	fprintf(kconfig, "config USB_LANG_SERBIAN_LATIN\n");
	fprintf(kconfig, "\tbool \"Serbian (Latin)\"\n");
	fprintf(kconfig, "config USB_LANG_SINDHI\n");
	fprintf(kconfig, "\tbool \"Sindhi\"\n");
	fprintf(kconfig, "config USB_LANG_SLOVAK\n");
	fprintf(kconfig, "\tbool \"Slovak\"\n");
	fprintf(kconfig, "config USB_LANG_SLOVENIAN\n");
	fprintf(kconfig, "\tbool \"Slovenian\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_TRADITIONAL_SORT\n");
	fprintf(kconfig, "\tbool \"Spanish (Traditional Sort)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_MEXICAN\n");
	fprintf(kconfig, "\tbool \"Spanish (Mexican)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_MODERN_SORT\n");
	fprintf(kconfig, "\tbool \"Spanish (Modern Sort)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_GUATEMALA\n");
	fprintf(kconfig, "\tbool \"Spanish (Guatemala)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_COSTA_RICA\n");
	fprintf(kconfig, "\tbool \"Spanish (Costa Rica)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_PANAMA\n");
	fprintf(kconfig, "\tbool \"Spanish (Panama)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_DOMINICAN_REPUBLIC\n");
	fprintf(kconfig, "\tbool \"Spanish (Dominican Republic)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_VENEZUELA\n");
	fprintf(kconfig, "\tbool \"Spanish (Venezuela)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_COLOMBIA\n");
	fprintf(kconfig, "\tbool \"Spanish (Colombia)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_PERU\n");
	fprintf(kconfig, "\tbool \"Spanish (Peru)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_ARGENTINA\n");
	fprintf(kconfig, "\tbool \"Spanish (Argentina)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_ECUADOR\n");
	fprintf(kconfig, "\tbool \"Spanish (Ecuador)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_CHILE\n");
	fprintf(kconfig, "\tbool \"Spanish (Chile)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_URUGUAY\n");
	fprintf(kconfig, "\tbool \"Spanish (Uruguay)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_PARAGUAY\n");
	fprintf(kconfig, "\tbool \"Spanish (Paraguay)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_BOLIVIA\n");
	fprintf(kconfig, "\tbool \"Spanish (Bolivia)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_EL_SALVADOR\n");
	fprintf(kconfig, "\tbool \"Spanish (El Salvador)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_HONDURAS\n");
	fprintf(kconfig, "\tbool \"Spanish (Honduras)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_NICARAGUA\n");
	fprintf(kconfig, "\tbool \"Spanish (Nicaragua)\"\n");
	fprintf(kconfig, "config USB_LANG_SPANISH_PUERTO_RICO\n");
	fprintf(kconfig, "\tbool \"Spanish (Puerto Rico)\"\n");
	fprintf(kconfig, "config USB_LANG_SUTU\n");
	fprintf(kconfig, "\tbool \"Sutu\"\n");
	fprintf(kconfig, "config USB_LANG_SWAHILI_KENYA\n");
	fprintf(kconfig, "\tbool \"Swahili (Kenya)\"\n");
	fprintf(kconfig, "config USB_LANG_SWEDISH\n");
	fprintf(kconfig, "\tbool \"Swedish\"\n");
	fprintf(kconfig, "config USB_LANG_SWEDISH_FINLAND\n");
	fprintf(kconfig, "\tbool \"Swedish (Finland)\"\n");
	fprintf(kconfig, "config USB_LANG_TAMIL\n");
	fprintf(kconfig, "\tbool \"Tamil.\"\n");
	fprintf(kconfig, "config USB_LANG_TATAR_TATARSTAN\n");
	fprintf(kconfig, "\tbool \"Tatar (Tatarstan)\"\n");
	fprintf(kconfig, "config USB_LANG_TELUGU\n");
	fprintf(kconfig, "\tbool \"Telugu.\"\n");
	fprintf(kconfig, "config USB_LANG_THAI\n");
	fprintf(kconfig, "\tbool \"Thai\"\n");
	fprintf(kconfig, "config USB_LANG_TURKISH\n");
	fprintf(kconfig, "\tbool \"Turkish\"\n");
	fprintf(kconfig, "config USB_LANG_UKRAINIAN\n");
	fprintf(kconfig, "\tbool \"Ukrainian\"\n");
	fprintf(kconfig, "config USB_LANG_URDU_PAKISTAN\n");
	fprintf(kconfig, "\tbool \"Urdu (Pakistan)\"\n");
	fprintf(kconfig, "config USB_LANG_URDU_INDIA\n");
	fprintf(kconfig, "\tbool \"Urdu (India)\"\n");
	fprintf(kconfig, "config USB_LANG_UZBEK_LATIN\n");
	fprintf(kconfig, "\tbool \"Uzbek (Latin)\"\n");
	fprintf(kconfig, "config USB_LANG_UZBEK_CYRILLIC\n");
	fprintf(kconfig, "\tbool \"Uzbek (Cyrillic)\"\n");
	fprintf(kconfig, "config USB_LANG_VIETNAMESE\n");
	fprintf(kconfig, "\tbool \"Vietnamese\"\n");
	fprintf(kconfig, "config USB_LANG_HID_USAGE_DATA_DESCRIPTOR\n");
	fprintf(kconfig, "\tbool \"HID (Usage Data Descriptor)\"\n");
	fprintf(kconfig, "config USB_LANG_HID_VENDOR_DEFINED_1\n");
	fprintf(kconfig, "\tbool \"HID (Vendor Defined 1)\"\n");
	fprintf(kconfig, "config USB_LANG_HID_VENDOR_DEFINED_2\n");
	fprintf(kconfig, "\tbool \"HID (Vendor Defined 2)\"\n");
	fprintf(kconfig, "config USB_LANG_HID_VENDOR_DEFINED_3\n");
	fprintf(kconfig, "\tbool \"HID (Vendor Defined 3)\"\n");
	fprintf(kconfig, "config USB_LANG_HID_VENDOR_DEFINED_4\n");
	fprintf(kconfig, "\tbool \"HID (Vendor Defined 4)\"\n");
	fprintf(kconfig, "endchoice\n");

	fprintf(kconfig, "if USB_LANG_USER_SELECT\n");
	fprintf(kconfig, "config USB_LANG_USER_VAL\n");
	fprintf(kconfig, "\thex \"User Selected Lang ID\"\n");
	fprintf(kconfig, "\tdefault 0x0000\n");
	fprintf(kconfig, "\trange  0 65535\n");
	fprintf(kconfig, "endif\n");

	fprintf(kconfig, "config USB_LANG_VAL\n");
	fprintf(kconfig, "\thex\n");
	fprintf(kconfig, "\tdefault USB_LANG_USER_VAL if USB_LANG_USER_SELECT\n");
	fprintf(kconfig, "\tdefault 0x0436 if USB_LANG_AFRIKAANS\n");
	fprintf(kconfig, "\tdefault 0x041c if USB_LANG_ALBANIAN\n");
	fprintf(kconfig, "\tdefault 0x0401 if USB_LANG_ARABIC_SAUDI_ARABIA\n");
	fprintf(kconfig, "\tdefault 0x0801 if USB_LANG_ARABIC_IRAQ\n");
	fprintf(kconfig, "\tdefault 0x0c01 if USB_LANG_ARABIC_EGYPT\n");
	fprintf(kconfig, "\tdefault 0x1001 if USB_LANG_ARABIC_LIBYA\n");
	fprintf(kconfig, "\tdefault 0x1401 if USB_LANG_ARABIC_ALGERIA\n");
	fprintf(kconfig, "\tdefault 0x1801 if USB_LANG_ARABIC_MOROCCO\n");
	fprintf(kconfig, "\tdefault 0x1c01 if USB_LANG_ARABIC_TUNISIA\n");
	fprintf(kconfig, "\tdefault 0x2001 if USB_LANG_ARABIC_OMAN\n");
	fprintf(kconfig, "\tdefault 0x2401 if USB_LANG_ARABIC_YEMEN\n");
	fprintf(kconfig, "\tdefault 0x2801 if USB_LANG_ARABIC_SYRIA\n");
	fprintf(kconfig, "\tdefault 0x2c01 if USB_LANG_ARABIC_JORDAN\n");
	fprintf(kconfig, "\tdefault 0x3001 if USB_LANG_ARABIC_LEBANON\n");
	fprintf(kconfig, "\tdefault 0x3401 if USB_LANG_ARABIC_KUWAIT\n");
	fprintf(kconfig, "\tdefault 0x3801 if USB_LANG_ARABIC_UAE\n");
	fprintf(kconfig, "\tdefault 0x3c01 if USB_LANG_ARABIC_BAHRAIN\n");
	fprintf(kconfig, "\tdefault 0x4001 if USB_LANG_ARABIC_QATAR\n");
	fprintf(kconfig, "\tdefault 0x042b if USB_LANG_ARMENIAN\n");
	fprintf(kconfig, "\tdefault 0x044d if USB_LANG_ASSAMESE\n");
	fprintf(kconfig, "\tdefault 0x042c if USB_LANG_AZERI_LATIN\n");
	fprintf(kconfig, "\tdefault 0x082c if USB_LANG_AZERI_CYRILLIC\n");
	fprintf(kconfig, "\tdefault 0x042d if USB_LANG_BASQUE\n");
	fprintf(kconfig, "\tdefault 0x0423 if USB_LANG_BELARUSSIAN\n");
	fprintf(kconfig, "\tdefault 0x0445 if USB_LANG_BENGALI\n");
	fprintf(kconfig, "\tdefault 0x0402 if USB_LANG_BULGARIAN\n");
	fprintf(kconfig, "\tdefault 0x0455 if USB_LANG_BURMESE\n");
	fprintf(kconfig, "\tdefault 0x0403 if USB_LANG_CATALAN\n");
	fprintf(kconfig, "\tdefault 0x0404 if USB_LANG_CHINESE_TAIWAN\n");
	fprintf(kconfig, "\tdefault 0x0804 if USB_LANG_CHINESE_PRC\n");
	fprintf(kconfig, "\tdefault 0x0c04 if USB_LANG_CHINESE_HONG_KONG_SAR_PRC\n");
	fprintf(kconfig, "\tdefault 0x1004 if USB_LANG_CHINESE_SINGAPORE\n");
	fprintf(kconfig, "\tdefault 0x1404 if USB_LANG_CHINESE_MACAU_SAR\n");
	fprintf(kconfig, "\tdefault 0x041a if USB_LANG_CROATIAN\n");
	fprintf(kconfig, "\tdefault 0x0405 if USB_LANG_CZECH\n");
	fprintf(kconfig, "\tdefault 0x0406 if USB_LANG_DANISH\n");
	fprintf(kconfig, "\tdefault 0x0413 if USB_LANG_DUTCH_NETHERLANDS\n");
	fprintf(kconfig, "\tdefault 0x0813 if USB_LANG_DUTCH_BELGIUM\n");
	fprintf(kconfig, "\tdefault 0x0409 if USB_LANG_ENGLISH_UNITED_STATES\n");
	fprintf(kconfig, "\tdefault 0x0809 if USB_LANG_ENGLISH_UNITED_KINGDOM\n");
	fprintf(kconfig, "\tdefault 0x0c09 if USB_LANG_ENGLISH_AUSTRALIAN\n");
	fprintf(kconfig, "\tdefault 0x1009 if USB_LANG_ENGLISH_CANADIAN\n");
	fprintf(kconfig, "\tdefault 0x1409 if USB_LANG_ENGLISH_NEW_ZEALAND\n");
	fprintf(kconfig, "\tdefault 0x1809 if USB_LANG_ENGLISH_IRELAND\n");
	fprintf(kconfig, "\tdefault 0x1c09 if USB_LANG_ENGLISH_SOUTH_AFRICA\n");
	fprintf(kconfig, "\tdefault 0x2009 if USB_LANG_ENGLISH_JAMAICA\n");
	fprintf(kconfig, "\tdefault 0x2409 if USB_LANG_ENGLISH_CARIBBEAN\n");
	fprintf(kconfig, "\tdefault 0x2809 if USB_LANG_ENGLISH_BELIZE\n");
	fprintf(kconfig, "\tdefault 0x2c09 if USB_LANG_ENGLISH_TRINIDAD\n");
	fprintf(kconfig, "\tdefault 0x3009 if USB_LANG_ENGLISH_ZIMBABWE\n");
	fprintf(kconfig, "\tdefault 0x3409 if USB_LANG_ENGLISH_PHILIPPINES\n");
	fprintf(kconfig, "\tdefault 0x0425 if USB_LANG_ESTONIAN\n");
	fprintf(kconfig, "\tdefault 0x0438 if USB_LANG_FAEROESE\n");
	fprintf(kconfig, "\tdefault 0x0429 if USB_LANG_FARSI\n");
	fprintf(kconfig, "\tdefault 0x040b if USB_LANG_FINNISH\n");
	fprintf(kconfig, "\tdefault 0x040c if USB_LANG_FRENCH_STANDARD\n");
	fprintf(kconfig, "\tdefault 0x080c if USB_LANG_FRENCH_BELGIAN\n");
	fprintf(kconfig, "\tdefault 0x0c0c if USB_LANG_FRENCH_CANADIAN\n");
	fprintf(kconfig, "\tdefault 0x100c if USB_LANG_FRENCH_SWITZERLAND\n");
	fprintf(kconfig, "\tdefault 0x140c if USB_LANG_FRENCH_LUXEMBOURG\n");
	fprintf(kconfig, "\tdefault 0x180c if USB_LANG_FRENCH_MONACO\n");
	fprintf(kconfig, "\tdefault 0x0437 if USB_LANG_GEORGIAN\n");
	fprintf(kconfig, "\tdefault 0x0407 if USB_LANG_GERMAN_STANDARD\n");
	fprintf(kconfig, "\tdefault 0x0807 if USB_LANG_GERMAN_SWITZERLAND\n");
	fprintf(kconfig, "\tdefault 0x0c07 if USB_LANG_GERMAN_AUSTRIA\n");
	fprintf(kconfig, "\tdefault 0x1007 if USB_LANG_GERMAN_LUXEMBOURG\n");
	fprintf(kconfig, "\tdefault 0x1407 if USB_LANG_GERMAN_LIECHTENSTEIN\n");
	fprintf(kconfig, "\tdefault 0x0408 if USB_LANG_GREEK\n");
	fprintf(kconfig, "\tdefault 0x0447 if USB_LANG_GUJARATI\n");
	fprintf(kconfig, "\tdefault 0x040d if USB_LANG_HEBREW\n");
	fprintf(kconfig, "\tdefault 0x0439 if USB_LANG_HINDI\n");
	fprintf(kconfig, "\tdefault 0x040e if USB_LANG_HUNGARIAN\n");
	fprintf(kconfig, "\tdefault 0x040f if USB_LANG_ICELANDIC\n");
	fprintf(kconfig, "\tdefault 0x0421 if USB_LANG_INDONESIAN\n");
	fprintf(kconfig, "\tdefault 0x0410 if USB_LANG_ITALIAN_STANDARD\n");
	fprintf(kconfig, "\tdefault 0x0810 if USB_LANG_ITALIAN_SWITZERLAND\n");
	fprintf(kconfig, "\tdefault 0x0411 if USB_LANG_JAPANESE\n");
	fprintf(kconfig, "\tdefault 0x044b if USB_LANG_KANNADA\n");
	fprintf(kconfig, "\tdefault 0x0860 if USB_LANG_KASHMIRI_INDIA\n");
	fprintf(kconfig, "\tdefault 0x043f if USB_LANG_KAZAKH\n");
	fprintf(kconfig, "\tdefault 0x0457 if USB_LANG_KONKANI\n");
	fprintf(kconfig, "\tdefault 0x0412 if USB_LANG_KOREAN\n");
	fprintf(kconfig, "\tdefault 0x0812 if USB_LANG_KOREAN_JOHAB\n");
	fprintf(kconfig, "\tdefault 0x0426 if USB_LANG_LATVIAN\n");
	fprintf(kconfig, "\tdefault 0x0427 if USB_LANG_LITHUANIAN\n");
	fprintf(kconfig, "\tdefault 0x0827 if USB_LANG_LITHUANIAN_CLASSIC\n");
	fprintf(kconfig, "\tdefault 0x042f if USB_LANG_MACEDONIAN\n");
	fprintf(kconfig, "\tdefault 0x043e if USB_LANG_MALAY_MALAYSIAN\n");
	fprintf(kconfig, "\tdefault 0x083e if USB_LANG_MALAY_BRUNEI_DARUSSALAM\n");
	fprintf(kconfig, "\tdefault 0x044c if USB_LANG_MALAYALAM\n");
	fprintf(kconfig, "\tdefault 0x0458 if USB_LANG_MANIPURI\n");
	fprintf(kconfig, "\tdefault 0x044e if USB_LANG_MARATHI\n");
	fprintf(kconfig, "\tdefault 0x0861 if USB_LANG_NEPALI_INDIA\n");
	fprintf(kconfig, "\tdefault 0x0414 if USB_LANG_NORWEGIAN_BOKMAL\n");
	fprintf(kconfig, "\tdefault 0x0814 if USB_LANG_NORWEGIAN_NYNORSK\n");
	fprintf(kconfig, "\tdefault 0x0448 if USB_LANG_ORIYA\n");
	fprintf(kconfig, "\tdefault 0x0415 if USB_LANG_POLISH\n");
	fprintf(kconfig, "\tdefault 0x0416 if USB_LANG_PORTUGUESE_BRAZIL\n");
	fprintf(kconfig, "\tdefault 0x0816 if USB_LANG_PORTUGUESE_STANDARD\n");
	fprintf(kconfig, "\tdefault 0x0446 if USB_LANG_PUNJABI\n");
	fprintf(kconfig, "\tdefault 0x0418 if USB_LANG_ROMANIAN\n");
	fprintf(kconfig, "\tdefault 0x0419 if USB_LANG_RUSSIAN\n");
	fprintf(kconfig, "\tdefault 0x044f if USB_LANG_SANSKRIT\n");
	fprintf(kconfig, "\tdefault 0x0c1a if USB_LANG_SERBIAN_CYRILLIC\n");
	fprintf(kconfig, "\tdefault 0x081a if USB_LANG_SERBIAN_LATIN\n");
	fprintf(kconfig, "\tdefault 0x0459 if USB_LANG_SINDHI\n");
	fprintf(kconfig, "\tdefault 0x041b if USB_LANG_SLOVAK\n");
	fprintf(kconfig, "\tdefault 0x0424 if USB_LANG_SLOVENIAN\n");
	fprintf(kconfig, "\tdefault 0x040a if USB_LANG_SPANISH_TRADITIONAL_SORT\n");
	fprintf(kconfig, "\tdefault 0x080a if USB_LANG_SPANISH_MEXICAN\n");
	fprintf(kconfig, "\tdefault 0x0c0a if USB_LANG_SPANISH_MODERN_SORT\n");
	fprintf(kconfig, "\tdefault 0x100a if USB_LANG_SPANISH_GUATEMALA\n");
	fprintf(kconfig, "\tdefault 0x140a if USB_LANG_SPANISH_COSTA_RICA\n");
	fprintf(kconfig, "\tdefault 0x180a if USB_LANG_SPANISH_PANAMA\n");
	fprintf(kconfig, "\tdefault 0x1c0a if USB_LANG_SPANISH_DOMINICAN_REPUBLIC\n");
	fprintf(kconfig, "\tdefault 0x200a if USB_LANG_SPANISH_VENEZUELA\n");
	fprintf(kconfig, "\tdefault 0x240a if USB_LANG_SPANISH_COLOMBIA\n");
	fprintf(kconfig, "\tdefault 0x280a if USB_LANG_SPANISH_PERU\n");
	fprintf(kconfig, "\tdefault 0x2c0a if USB_LANG_SPANISH_ARGENTINA\n");
	fprintf(kconfig, "\tdefault 0x300a if USB_LANG_SPANISH_ECUADOR\n");
	fprintf(kconfig, "\tdefault 0x340a if USB_LANG_SPANISH_CHILE\n");
	fprintf(kconfig, "\tdefault 0x380a if USB_LANG_SPANISH_URUGUAY\n");
	fprintf(kconfig, "\tdefault 0x3c0a if USB_LANG_SPANISH_PARAGUAY\n");
	fprintf(kconfig, "\tdefault 0x400a if USB_LANG_SPANISH_BOLIVIA\n");
	fprintf(kconfig, "\tdefault 0x440a if USB_LANG_SPANISH_EL_SALVADOR\n");
	fprintf(kconfig, "\tdefault 0x480a if USB_LANG_SPANISH_HONDURAS\n");
	fprintf(kconfig, "\tdefault 0x4c0a if USB_LANG_SPANISH_NICARAGUA\n");
	fprintf(kconfig, "\tdefault 0x500a if USB_LANG_SPANISH_PUERTO_RICO\n");
	fprintf(kconfig, "\tdefault 0x0430 if USB_LANG_SUTU\n");
	fprintf(kconfig, "\tdefault 0x0441 if USB_LANG_SWAHILI_KENYA\n");
	fprintf(kconfig, "\tdefault 0x041d if USB_LANG_SWEDISH\n");
	fprintf(kconfig, "\tdefault 0x081d if USB_LANG_SWEDISH_FINLAND\n");
	fprintf(kconfig, "\tdefault 0x0449 if USB_LANG_TAMIL\n");
	fprintf(kconfig, "\tdefault 0x0444 if USB_LANG_TATAR_TATARSTAN\n");
	fprintf(kconfig, "\tdefault 0x044a if USB_LANG_TELUGU\n");
	fprintf(kconfig, "\tdefault 0x041e if USB_LANG_THAI\n");
	fprintf(kconfig, "\tdefault 0x041f if USB_LANG_TURKISH\n");
	fprintf(kconfig, "\tdefault 0x0422 if USB_LANG_UKRAINIAN\n");
	fprintf(kconfig, "\tdefault 0x0420 if USB_LANG_URDU_PAKISTAN\n");
	fprintf(kconfig, "\tdefault 0x0820 if USB_LANG_URDU_INDIA\n");
	fprintf(kconfig, "\tdefault 0x0443 if USB_LANG_UZBEK_LATIN\n");
	fprintf(kconfig, "\tdefault 0x0843 if USB_LANG_UZBEK_CYRILLIC\n");
	fprintf(kconfig, "\tdefault 0x042a if USB_LANG_VIETNAMESE\n");
	fprintf(kconfig, "\tdefault 0x04ff if USB_LANG_HID_USAGE_DATA_DESCRIPTOR\n");
	fprintf(kconfig, "\tdefault 0xf0ff if USB_LANG_HID_VENDOR_DEFINED_1\n");
	fprintf(kconfig, "\tdefault 0xf4ff if USB_LANG_HID_VENDOR_DEFINED_2\n");
	fprintf(kconfig, "\tdefault 0xf8ff if USB_LANG_HID_VENDOR_DEFINED_3\n");
	fprintf(kconfig, "\tdefault 0xfcff if USB_LANG_HID_VENDOR_DEFINED_4\n");



	fprintf(kconfig, "menu \"USB Strings list\"\n");
	fprintf(kconfig, "config USB_NSTRINGS\n");
	fprintf(kconfig, "\tint \"Number of Strings\"\n");
	fprintf(kconfig, "\tdefault 1\n");

	for(int j=1; j<max_string; j++){
		fprintf(kconfig, "if USB_NSTRINGS >= %d\n", j);
		fprintf(kconfig, "config USB_STRING_INDEX_%d\n", j);
		fprintf(kconfig, "\tstring \"string at index %d\"\n", j);
		fprintf(kconfig, "endif\n");
	}
	fprintf(kconfig, "endmenu\n");



	for(int i=0; i< max_conf; i++){
		//fprintf(kconfig,"\tvisible if USB_DEVICE_NCONFIGS>%d\n", i);
		fprintf(kconfig, "if USB_DEVICE_NCONFIGS>%d\n", i);
		fprintf(kconfig, "menu \"USB Configuration No %d\"\n",i);
		fprintf(kconfig, "config USB_CONFIG%d_NINTERFACES\n", i);
		fprintf(kconfig, "\tint \"Number of Interfaces\"\n");
		fprintf(kconfig, "\trange 1 255\n");
		fprintf(kconfig, "\t---help---\n");
		fprintf(kconfig, "\t\tNumber of interfaces supported by this configuration\n");

		fprintf(kconfig, "config USB_CONFIG%d_CFGVALUE\n", i);
		fprintf(kconfig, "\tint \"Configuration Value\"\n");
		fprintf(kconfig, "\tdefault %d\n", i+1);
		fprintf(kconfig, "\t---help---\n");
		fprintf(kconfig, "\t\tValue to use as an argument to the SetConfiguration()\n\t\trequest to select this configuration\n");

		fprintf(kconfig, "config USB_CONFIG%d_ICFG\n",i);
		fprintf(kconfig, "\tint \"Configuration String Index\"\n");
		fprintf(kconfig, "\tdefault 0\n");
		fprintf(kconfig, "\t---help---\n");
		fprintf(kconfig, "\t\tIndex of string descriptor describing this configuration\n");


		fprintf(kconfig, "menu \"USB Attribute\"\n");
		fprintf(kconfig, "config USB_CONFIG%d_ATTR_D7\n", i);
		fprintf(kconfig, "\tbool \"Configuration Attribue D7\"\n");
		fprintf(kconfig, "\tdefault y\n");
		fprintf(kconfig, "\t---help---\n");
		fprintf(kconfig, "\t\tD7 Reserved (set to one) for historical reason\n");


		fprintf(kconfig, "config USB_CONFIG%d_ATTR_D6\n", i);
		fprintf(kconfig, "\tbool \"Self-Powered\"\n");
		fprintf(kconfig, "\tdefault y\n");
		fprintf(kconfig, "\t---help---\n");
		fprintf(kconfig, "\t\tA device configuration that uses power from\n");
		fprintf(kconfig, "\t\tthe bus and a local source reports a non-zero\n");
		fprintf(kconfig, "\t\tvalue in bMaxPower to indicate the amount of\n");
		fprintf(kconfig, "\t\tbus power required and sets D6. The actual\n");
		fprintf(kconfig, "\t\tpower source at runtime may be determined\n");
		fprintf(kconfig, "\t\tusing the GetStatus(DEVICE) request (see\n");
		fprintf(kconfig, "\t\tSection 9.4.5).\n");

		fprintf(kconfig, "config USB_CONFIG%d_ATTR_D5\n", i);
		fprintf(kconfig, "\tbool \"Remote Wakeup\"\n");
		fprintf(kconfig, "\tdefault y\n");
		fprintf(kconfig, "\t---help---\n");
		fprintf(kconfig, "\t\tIf a device configuration supports remote Wakeup\n");

		fprintf(kconfig, "config USB_CONFIG%d_ATTR_D4\n", i);
		fprintf(kconfig, "\tbool \"Configuration Attribue D4\"\n");
		fprintf(kconfig, "\tdefault n\n");
		fprintf(kconfig, "\t---help---\n");
		fprintf(kconfig, "\t\tD4-0 Reserved (set to zero)\n");

		fprintf(kconfig, "config USB_CONFIG%d_ATTR_D3\n", i);
		fprintf(kconfig, "\tbool \"Configuration Attribue D3\"\n");
		fprintf(kconfig, "\tdefault n\n");
		fprintf(kconfig, "\t---help---\n");
		fprintf(kconfig, "\t\tD4-0 Reserved (set to zero)\n");

		fprintf(kconfig, "config USB_CONFIG%d_ATTR_D2\n", i);
		fprintf(kconfig, "\tbool \"Configuration Attribue D2\"\n");
		fprintf(kconfig, "\tdefault n\n");
		fprintf(kconfig, "\t---help---\n");
		fprintf(kconfig, "\t\tD4-0 Reserved (set to zero)\n");

		fprintf(kconfig, "config USB_CONFIG%d_ATTR_D1\n", i);
		fprintf(kconfig, "\tbool \"Configuration Attribue D1\"\n");
		fprintf(kconfig, "\tdefault n\n");
		fprintf(kconfig, "\t---help---\n");
		fprintf(kconfig, "\t\tD4-0 Reserved (set to zero)\n");

		fprintf(kconfig, "config USB_CONFIG%d_ATTR_D0\n", i);
		fprintf(kconfig, "\tbool \"Configuration Attribue D0\"\n");
		fprintf(kconfig, "\tdefault n\n");
		fprintf(kconfig, "\t---help---\n");
		fprintf(kconfig, "\t\tD4-0 Reserved (set to zero)\n");

		fprintf(kconfig, "endmenu\n");

		fprintf(kconfig, "config USB_CONFIG%d_MXPOWER\n",i);
		fprintf(kconfig, "\thex \"Maximum Power\"\n");
		fprintf(kconfig, "\tdefault 0x30\n");
		fprintf(kconfig, "\t---help---\n");
		fprintf(kconfig, "\t\tMaximum power consumption of the USB\n");
		fprintf(kconfig, "\t\tdevice from the bus in this specific\n");
		fprintf(kconfig, "\t\tconfiguration when the device is fully\n");
		fprintf(kconfig, "\t\toperational. Expressed in 2 mA units\n");
		fprintf(kconfig, "\t\t(i.e., 50 = 100 mA).\n");
		fprintf(kconfig, "\t\tNote: A device configuration reports whether\n");
		fprintf(kconfig, "\t\tthe configuration is bus-powered or selfpowered.\n");
		fprintf(kconfig, "\t\tDevice status reports whether the\n");
		fprintf(kconfig, "\t\tdevice is currently self-powered. If a device is\n");
		fprintf(kconfig, "\t\tdisconnected from its external power source, it\n");
		fprintf(kconfig, "\t\tupdates device status to indicate that it is no\n");
		fprintf(kconfig, "\t\tlonger self-powered.\n");
		fprintf(kconfig, "\t\tA device may not increase its power draw\n");
		fprintf(kconfig, "\t\tfrom the bus, when it loses its external power\n");
		fprintf(kconfig, "\t\tsource, beyond the amount reported by its\n");
		fprintf(kconfig, "\t\tconfiguration.\n");
		fprintf(kconfig, "\t\tIf a device can continue to operate when\n");
		fprintf(kconfig, "\t\tdisconnected from its external power source, it\n");
		fprintf(kconfig, "\t\tcontinues to do so. If the device cannot\n");
		fprintf(kconfig, "\t\tcontinue to operate, it fails operations it can\n");
		fprintf(kconfig, "\t\tno longer support. The USB System Software\n");
		fprintf(kconfig, "\t\tmay determine the cause of the failure by\n");
		fprintf(kconfig, "\t\tchecking the status and noting the loss of the\n");


		for(int j=0;j<max_if;j++){
			fprintf(kconfig, "if USB_CONFIG%d_NINTERFACES>%d\n", i, j);
			fprintf(kconfig, "menu \"USB Interface No %d\"\n", j);


			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_IFNO\n", i, j);
			fprintf(kconfig, "\tint \"Interface Number\"\n");
			fprintf(kconfig, "\tdefault %d\n", j);
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tNumber of this interface. Zero-based\n");
			fprintf(kconfig, "\t\tvalue identifying the index in the array of\n");
			fprintf(kconfig, "\t\tconcurrent interfaces supported by this\n");
			fprintf(kconfig, "\t\tconfiguration.\n");


			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_ALT\n", i, j);
			fprintf(kconfig, "\tint \"Alt Setting\"\n");
			fprintf(kconfig, "\tdefault 0\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tValue used to select this alternate setting\n");
			fprintf(kconfig, "\t\tfor the interface identified in the prior field\n");


			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_NEPS\n", i, j);
			fprintf(kconfig, "\tint \"Number of Endpoints\"\n");
			fprintf(kconfig, "\tdefault 2\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tNumber of endpoints used by this\n");
			fprintf(kconfig, "\t\tinterface (excluding endpoint zero). If this\n");
			fprintf(kconfig, "\t\tvalue is zero, this interface only uses the\n");
			fprintf(kconfig, "\t\tDefault Control Pipe.\n");


			fprintf(kconfig, "choice\n");
			fprintf(kconfig, "\tprompt \"USB Interface Class\"\n");
			fprintf(kconfig, "\tdefault USB_CONFIG%d_INTERFACE%d_CLASS_VENDOR_SPECIFIC\n", i, j);

			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_USER\n", i, j);
			fprintf(kconfig, "\tbool \"Set Manually\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for vendors to use as \n");
			fprintf(kconfig, "\t\tthey please. These class codes can be used in both \n");
			fprintf(kconfig, "\t\tDevice and Interface Descriptors.\n");


			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_AUDIO\n", i, j);
			fprintf(kconfig, "\tbool \"Audio Class\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tAudio class\n");


			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_HID\n", i, j);
			fprintf(kconfig, "\tbool \"HID\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for devices that conform\n");
			fprintf(kconfig, "\t\tto the HID Device Class Specification found on the\n");
			fprintf(kconfig, "\t\tUSB-IF website. That specification defines the usable\n");
			fprintf(kconfig, "\t\tset of SubClass and Protocol values. Values outside\n");
			fprintf(kconfig, "\t\tof that defined spec are reserved. These class codes\n");
			fprintf(kconfig, "\t\tcan only be used in Interface Descriptors.\n");



			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_PHYSICAL\n", i, j);
			fprintf(kconfig, "\tbool \"Physical\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for devices that conform\n");
			fprintf(kconfig, "\t\tto the Physical Device Class Specification found on\n");
			fprintf(kconfig, "\t\tthe USB-IF website. That specification defines the\n");
			fprintf(kconfig, "\t\tusable set of SubClass and Protocol values. Values\n");
			fprintf(kconfig, "\t\toutside of that defined spec are reserved. These\n");
			fprintf(kconfig, "\t\tclass codes can only be used in Interface Descriptors.\n");

			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_IMAGE\n", i, j);
			fprintf(kconfig, "\tbool \"Still Image\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for devices that conform\n");
			fprintf(kconfig, "\t\tto the Imaging Device Class Specification found on\n");
			fprintf(kconfig, "\t\tthe USB-IF website. That specification defines the\n");
			fprintf(kconfig, "\t\tusable set of SubClass and Protocol values. Values\n");
			fprintf(kconfig, "\t\toutside of that defined spec are reserved.\n");


			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_PRINTER\n", i, j);
			fprintf(kconfig, "\tbool \"Printer\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for devices that conform\n");
			fprintf(kconfig, "\t\tto the Printer Device Class Specification found on\n");
			fprintf(kconfig, "\t\tthe USB-IF website. That specification defines the\n");
			fprintf(kconfig, "\t\tusable set of SubClass and Protocol values. Values\n");
			fprintf(kconfig, "\t\toutside of that defined spec are reserved. These\n");
			fprintf(kconfig, "\t\tclass codes can only be used in Interface Descriptors.\n");



			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_MSC\n", i, j);
			fprintf(kconfig, "\tbool \"Mass Storage\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for devices that conform\n");
			fprintf(kconfig, "\t\tto the Mass Storage Device Class Specification found\n");
			fprintf(kconfig, "\t\ton the USB-IF website. That specification defines the\n");
			fprintf(kconfig, "\t\tusable set of SubClass and Protocol values. Values\n");
			fprintf(kconfig, "\t\toutside of that defined spec are reserved. These\n");
			fprintf(kconfig, "\t\tclass codes can only be used in Interface Descriptors.\n");

			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_CDC_DATA\n", i, j);
			fprintf(kconfig, "\tbool \"CDC DATA\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for devices that conform to the\n");
			fprintf(kconfig, "\t\tCommunications Device Class Specification found on the\n");
			fprintf(kconfig, "\t\tUSB-IF website. That specification defines the usable\n");
			fprintf(kconfig, "\t\tset of SubClass and Protocol values.Values outside of\n");
			fprintf(kconfig, "\t\tthat defined spec are reserved. These class codes can\n");
			fprintf(kconfig, "\t\tonly be used in Interface Descriptors.\n");

			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_SMARTCARD\n", i, j);
			fprintf(kconfig, "\tbool \"Smart Card\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for devices that conform to\n");
			fprintf(kconfig, "\t\tthe Smart Card Device Class Specification found on the\n");
			fprintf(kconfig, "\t\tUSB-IF website. That specification defines the usable\n");
			fprintf(kconfig, "\t\tset of SubClass and Protocol values.Values outside of\n");
			fprintf(kconfig, "\t\tthat defined spec are reserved. These class codes can\n");
			fprintf(kconfig, "\t\tonly be used in Interface Descriptors.\n");


			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_CONTENT_SECURITY\n", i, j);
			fprintf(kconfig, "\tbool \"Content Security\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for devices that conform to\n");
			fprintf(kconfig, "\t\tthe Content Security Device Class Specification found\n");
			fprintf(kconfig, "\t\ton the USB-IF website. That specification defines the\n");
			fprintf(kconfig, "\t\tusable set of SubClass and Protocol values. Values\n");
			fprintf(kconfig, "\t\toutside of that defined spec are reserved. These class\n");
			fprintf(kconfig, "\t\tcodes can only be used in Interface Descriptors.\n");
			fprintf(kconfig, "\t\t\n");


			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_VIDEO\n", i, j);
			fprintf(kconfig, "\tbool \"Video\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for devices that conform to\n");
			fprintf(kconfig, "\t\tthe Video Device Class Specification found on the USB-IF\n");
			fprintf(kconfig, "\t\twebsite. That specification defines the usable set of\n");
			fprintf(kconfig, "\t\tSubClass and Protocol values. Values outside of that\n");
			fprintf(kconfig, "\t\tdefined spec are reserved. These class codes can only\n");
			fprintf(kconfig, "\t\tbe used in Interface Descriptors.\n");


			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_PERSONAL_HEALTHCARE\n", i, j);
			fprintf(kconfig, "\tbool \"Personal HealthCare\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for devices that conform to\n");
			fprintf(kconfig, "\t\tthe Personal Healthcare Class Specification found on the USB-IF\n");
			fprintf(kconfig, "\t\twebsite. That specification defines the usable set of\n");
			fprintf(kconfig, "\t\tSubClass and Protocol values. Values outside of that\n");
			fprintf(kconfig, "\t\tdefined spec are reserved. These class codes can only\n");
			fprintf(kconfig, "\t\tbe used in Interface Descriptors.\n");



			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_AV\n", i, j);
			fprintf(kconfig, "\tbool \"Audio-Video\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThe USB Audio/Video (AV) Device Class Definition describes\n");
			fprintf(kconfig, "\t\tthe methods used to communicate with devices or functions\n");
			fprintf(kconfig, "\t\tembedded in composite devices that are used to manipulate\n");
			fprintf(kconfig, "\t\taudio, video, voice, and all image- and sound-related\n");
			fprintf(kconfig, "\t\tfunctionality. That specification defines the usable set\n");
			fprintf(kconfig, "\t\tof SubClass and Protocol values. Values outside of that\n");
			fprintf(kconfig, "\t\tdefined spec are reserved. These class codes can only be\n");
			fprintf(kconfig, "\t\tused in Interface Descriptors.\n");



			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_TYPEC_BRIDGE\n", i, j);
			fprintf(kconfig, "\tbool \"USB Type-C Bridge Class\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tTODO write help.\n");


			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_DIAG\n", i, j);
			fprintf(kconfig, "\tbool \"Diagnostic Device\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for devices that diagnostic devices.\n");
			fprintf(kconfig, "\t\tThis class code can be used in Device or Interface Descriptors. \n");
			fprintf(kconfig, "\t\tTrace is a form of debugging where processor or system activity\n");
			fprintf(kconfig, "\t\tis made externally visible in real-time or stored and later\n");
			fprintf(kconfig, "\t\tretrieved for viewing by an applications developer, applications\n");
			fprintf(kconfig, "\t\tprogram, or, external equipment specializing observing system activity. \n");
			fprintf(kconfig, "\t\tDesign for Debug or Test (Dfx). This refers to a logic block\n");
			fprintf(kconfig, "\t\tthat provides debug or test support (E.g. via Test Access Port (TAP)). \n");
			fprintf(kconfig, "\t\tDvC: Debug Capability on the USB device (Device Capability) \n");


			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_WIRELESS\n", i, j);
			fprintf(kconfig, "\tbool \"Wireless Controller\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for devices that are Wireless\n");
			fprintf(kconfig, "\t\tcontrollers. Values not shown in the table below are reserved.\n");
			fprintf(kconfig, "\t\tThese class codes are to be used in Interface Descriptors, with\n");
			fprintf(kconfig, "\t\tthe exception of the Bluetooth class code which can also be\n");
			fprintf(kconfig, "\t\tused in a Device Descriptor.\n");



			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_MISC\n", i, j);
			fprintf(kconfig, "\tbool \"Miscellaneous\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for miscellaneous device definitions.\n");
			fprintf(kconfig, "\t\tValues not shown in the table below are reserved. The use of\n");
			fprintf(kconfig, "\t\tthese class codes (Device or Interface descriptor) are\n");
			fprintf(kconfig, "\t\tspecifically annotated in each entry below.\n");



			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_APP_SPECIFIC\n", i, j);
			fprintf(kconfig, "\tbool \"Application Specific\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for devices that conform to\n");
			fprintf(kconfig, "\t\tseveral class specifications found on the USB-IF website.\n");
			fprintf(kconfig, "\t\tThat specification defines the usable set of SubClass and\n");
			fprintf(kconfig, "\t\tProtocol values. Values outside of that defined spec are\n");
			fprintf(kconfig, "\t\treserved. These class codes can only be used in\n");
			fprintf(kconfig, "\t\tInterface Descriptors.\n");

			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_VENDOR_SPECIFIC\n", i, j);
			fprintf(kconfig, "\tbool \"Vendor Specific\"\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tThis base class is defined for vendors to use as \n");
			fprintf(kconfig, "\t\tthey please. These class codes can be used in both \n");
			fprintf(kconfig, "\t\tDevice and Interface Descriptors.\n");


			fprintf(kconfig, "endchoice\n");

			fprintf(kconfig, "if USB_CONFIG%d_INTERFACE%d_CLASS_USER\n", i, j);
			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_CUSTOM_VAL\n",i,j);
			fprintf(kconfig, "\thex \"Interface Class Value\"\n");
			fprintf(kconfig, "\trange 0 255\n");
			fprintf(kconfig, "\tdefault 0x00\n");
			fprintf(kconfig, "\tendif\n");

			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_CLASS_VAL\n", i, j);
			fprintf(kconfig, "\thex\n");
			fprintf(kconfig, "\trange 0 255\n");

			fprintf(kconfig, "\tdefault 0x00 if USB_CONFIG%d_INTERFACE%d_CLASS_USER\n", i, j);
			fprintf(kconfig, "\tdefault 0x01 if USB_CONFIG%d_INTERFACE%d_CLASS_AUDIO\n", i, j);
			fprintf(kconfig, "\tdefault 0x03 if USB_CONFIG%d_INTERFACE%d_CLASS_HID\n", i, j);
			fprintf(kconfig, "\tdefault 0x05 if USB_CONFIG%d_INTERFACE%d_CLASS_PHYSICAL\n", i, j);
			fprintf(kconfig, "\tdefault 0x06 if USB_CONFIG%d_INTERFACE%d_CLASS_IMAGE\n", i, j);
			fprintf(kconfig, "\tdefault 0x07 if USB_CONFIG%d_INTERFACE%d_CLASS_PRINTER\n", i, j);
			fprintf(kconfig, "\tdefault 0x08 if USB_CONFIG%d_INTERFACE%d_CLASS_MSC\n", i, j);
			fprintf(kconfig, "\tdefault 0x0a if USB_CONFIG%d_INTERFACE%d_CLASS_CDC_DATA\n", i, j);
			fprintf(kconfig, "\tdefault 0x0b if USB_CONFIG%d_INTERFACE%d_CLASS_SMARTCARD\n", i, j);
			fprintf(kconfig, "\tdefault 0x0d if USB_CONFIG%d_INTERFACE%d_CLASS_CONTENT_SECURITY\n", i, j);
			fprintf(kconfig, "\tdefault 0x0e if USB_CONFIG%d_INTERFACE%d_CLASS_VIDEO\n", i, j);
			fprintf(kconfig, "\tdefault 0x0f if USB_CONFIG%d_INTERFACE%d_CLASS_PERSONAL_HEALTHCARE\n", i, j);
			fprintf(kconfig, "\tdefault 0x10 if USB_CONFIG%d_INTERFACE%d_CLASS_AV\n", i, j);
			fprintf(kconfig, "\tdefault 0x12 if USB_CONFIG%d_INTERFACE%d_CLASS_TYPEC_BRIDGE\n", i, j);
			fprintf(kconfig, "\tdefault 0xdc if USB_CONFIG%d_INTERFACE%d_CLASS_DIAG\n", i, j);
			fprintf(kconfig, "\tdefault 0xe0 if USB_CONFIG%d_INTERFACE%d_CLASS_WIRELESS\n", i, j);
			fprintf(kconfig, "\tdefault 0xef if USB_CONFIG%d_INTERFACE%d_CLASS_MISC\n", i, j);
			fprintf(kconfig, "\tdefault 0xfe if USB_CONFIG%d_INTERFACE%d_CLASS_APP_SPECIFIC\n", i, j);
			fprintf(kconfig, "\tdefault 0xff if USB_CONFIG%d_INTERFACE%d_CLASS_VENDOR_SPECIFIC\n", i, j);
			fprintf(kconfig, "\tdefault USB_CONFIG%d_INTERFACE%d_CLASS_CUSTOM_VAL if USB_CONFIG%d_INTERFACE%d_CLASS_USER\n",i,j, i, j);



			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_SUBCLASS_VAL\n",i,j);
			fprintf(kconfig, "\tint \"Interface SubClass Value\"\n");
			fprintf(kconfig, "\trange 0 255\n");
			fprintf(kconfig, "\tdefault 0\n");

			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_PROTOCOL_VAL\n",i,j);
			fprintf(kconfig, "\tint \"Interface Protocol Value\"\n");
			fprintf(kconfig, "\trange 0 255\n");
			fprintf(kconfig, "\tdefault 0\n");

			fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_IIF\n",i, j);
			fprintf(kconfig, "\tint \"Interface String Index\"\n");
			fprintf(kconfig, "\tdefault 0\n");
			fprintf(kconfig, "\t---help---\n");
			fprintf(kconfig, "\t\tIndex of string descriptor describing this interface\n");

			for(int k = 0; k < max_ep; k++){
				fprintf(kconfig, "if USB_CONFIG%d_INTERFACE%d_NEPS>%d\n", i, j, k);
				fprintf(kconfig,"menu \"USB Endpoint %d\"\n", k);

				fprintf(kconfig,"config USB_CONFIG%d_INTERFACE%d_EP%d_ADDR\n",i,j,k);
				fprintf(kconfig,"\thex \"Endpoint Address\"\n");
				if(k > 15)
					fprintf(kconfig,"\tdefault 0x%02x\n", 0x80 | (k & 0xf)) ;
				else
					fprintf(kconfig,"\tdefault 0x%02x\n",  (k & 0xf) + 1);
				fprintf(kconfig, "\t---help---\n");
				fprintf(kconfig, "\t\tThe address of the endpoint on the USB device\n");
				fprintf(kconfig, "\t\tdescribed by this descriptor. The address is\n");
				fprintf(kconfig, "\t\tencoded as follows:\n");
				fprintf(kconfig, "\t\tBit 3...0: The endpoint number\n");
				fprintf(kconfig, "\t\tBit 6...4: Reserved, reset to zero\n");
				fprintf(kconfig, "\t\tBit 7: Direction, ignored for\n");
				fprintf(kconfig, "\t\tcontrol endpoints\n");
				fprintf(kconfig, "\t\t0 = OUT endpoint\n");
				fprintf(kconfig, "\t\t1 = IN endpoint\n");


				fprintf(kconfig, "choice\n");
				fprintf(kconfig, "prompt \"Transfer Type\" \n");
				fprintf(kconfig, "default USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_XFER_TYPE_BULK\n", i,j,k);

				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_XFER_TYPE_CONTROL\n",i,j, k);
				fprintf(kconfig, "\tbool \"Control\"\n");
				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_XFER_TYPE_ISOCHRONOUS\n",i,j, k);
				fprintf(kconfig, "\tbool \"Isochronous\"\n");
				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_XFER_TYPE_BULK\n", i,j,k);
				fprintf(kconfig, "\tbool \"Bulk\"\n");
				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_XFER_TYPE_INTERRUPT\n",i,j, k);
				fprintf(kconfig, "\tbool \"Interrupt\"\n");
				fprintf(kconfig, "endchoice\n");


				fprintf(kconfig, "choice\n");
				fprintf(kconfig, "prompt \"Synchronization Type\" \n");
				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_SYNC_TYPE_NO_SYNC\n",i,j, k);
				fprintf(kconfig, "\tbool \"No Synchronization\"\n");
				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_SYNC_TYPE_ASYNCHRONOUS\n",i,j, k);
				fprintf(kconfig, "\tbool \"Asynchronous\"\n");
				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_SYNC_TYPE_ADAPTIVE\n", i,j,k);
				fprintf(kconfig, "\tbool \"Adaptive\"\n");
				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_SYNC_TYPE_SYNCHRONOUS\n",i,j, k);
				fprintf(kconfig, "\tbool \"SYNCHRONOUS\"\n");
				fprintf(kconfig, "endchoice\n");


				fprintf(kconfig, "choice\n");
				fprintf(kconfig, "prompt \"USAGE Type\" \n");
				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_USAGE_TYPE_DATA\n",i,j, k);
				fprintf(kconfig, "\tbool \"Data\"\n");
				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_USAGE_TYPE_FEEDBACK\n",i,j, k);
				fprintf(kconfig, "\tbool \"Feedback\"\n");
				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_USAGE_TYPE_IMPL_FEEDBACK\n", i,j,k);
				fprintf(kconfig, "\tbool \"Implicit Feedback Data\"\n");
				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_USAGE_TYPE_RESERVED\n",i,j, k);
				fprintf(kconfig, "\tbool \"Reserved\"\n");
				fprintf(kconfig, "endchoice\n");

				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_NONE\n",i,j, k);
				fprintf(kconfig, "\tint \"Reserved Endpoint Attribute D6 D7\"\n");
				fprintf(kconfig, "\tdefault 0\n");
				fprintf(kconfig, "\trange 0 3\n");

				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_USAGE_TYPE_VAL\n",i,j, k);
				fprintf(kconfig, "\tint\n");
				fprintf(kconfig, "\tdefault 0 if USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_USAGE_TYPE_DATA\n",i,j, k);
				fprintf(kconfig, "\tdefault 1 if USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_USAGE_TYPE_FEEDBACK\n",i,j, k);
				fprintf(kconfig, "\tdefault 2 if USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_USAGE_TYPE_IMPL_FEEDBACK\n", i,j,k);
				fprintf(kconfig, "\tdefault 3 if USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_USAGE_TYPE_RESERVED\n",i,j, k);

				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_XFER_TYPE_VAL\n", i, j, k);
				fprintf(kconfig, "\tint\n");
				fprintf(kconfig, "\tdefault 0 if USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_XFER_TYPE_CONTROL\n",i,j, k);
				fprintf(kconfig, "\tdefault 1 if USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_XFER_TYPE_ISOCHRONOUS\n",i,j, k);
				fprintf(kconfig, "\tdefault 2 if USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_XFER_TYPE_BULK\n", i,j,k);
				fprintf(kconfig, "\tdefault 3 if USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_XFER_TYPE_INTERRUPT\n",i,j, k);


				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_SYNC_TYPE_VAL\n",i,j, k);
				fprintf(kconfig, "\tint\n");
				fprintf(kconfig, "\tdefault 0 if  USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_SYNC_TYPE_NO_SYNC\n",i,j, k);
				fprintf(kconfig, "\tdefault 1 if USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_SYNC_TYPE_ASYNCHRONOUS\n",i,j, k);
				fprintf(kconfig, "\tdefault 2 if  USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_SYNC_TYPE_ADAPTIVE\n", i,j,k);
				fprintf(kconfig, "\tdefault 3 if  USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_SYNC_TYPE_SYNCHRONOUS\n",i,j, k);



				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_MXPACKETSIZE\n",i,j, k);
				fprintf(kconfig, "\thex \"Maximum Packet Size\"\n");
				fprintf(kconfig, "\tdefault 0x200\n");
				fprintf(kconfig, "\trange 0 65535\n");
				fprintf(kconfig, "\t---help---\n");
				fprintf(kconfig, "\t\tMaximum packet size this endpoint is capable of\n");
				fprintf(kconfig, "\t\tsending or receiving when this configuration is\n");
				fprintf(kconfig, "\t\tselected.\n");
				fprintf(kconfig, "\t\tFor isochronous endpoints, this value is used to\n");
				fprintf(kconfig, "\t\treserve the bus time in the schedule, required for the\n");
				fprintf(kconfig, "\t\tper-(micro)frame data payloads. The pipe may, on an\n");
				fprintf(kconfig, "\t\tongoing basis, actually use less bandwidth than that\n");
				fprintf(kconfig, "\t\treserved. The device reports, if necessary, the actual\n");
				fprintf(kconfig, "\t\tbandwidth used via its normal, non-USB defined\n");
				fprintf(kconfig, "\t\tmechanisms.\n");
				fprintf(kconfig, "\t\tFor all endpoints, bits 10..0 specify the maximum\n");
				fprintf(kconfig, "\t\tpacket size (in bytes).\n");
				fprintf(kconfig, "\t\tFor high-speed isochronous and interrupt endpoints:\n");
				fprintf(kconfig, "\t\tBits 12..11 specify the number of additional transaction\n");
				fprintf(kconfig, "\t\topportunities per microframe:\n");
				fprintf(kconfig, "\t\t00 = None (1 transaction per microframe)\n");
				fprintf(kconfig, "\t\t01 = 1 additional (2 per microframe)\n");
				fprintf(kconfig, "\t\t10 = 2 additional (3 per microframe)\n");
				fprintf(kconfig, "\t\t11 = Reserved\n");
				fprintf(kconfig, "\t\tBits 15..13 are reserved and must be set to zero.\n");
				fprintf(kconfig, "\t\tRefer to Chapter 5 for more information.\n");


				fprintf(kconfig, "config USB_CONFIG%d_INTERFACE%d_EP%d_INTERVAL\n",i,j, k);
				fprintf(kconfig, "\tint \"Interval\"\n");
				fprintf(kconfig, "\tdefault 0\n");
				fprintf(kconfig, "\trange 0 255\n");
				fprintf(kconfig, "\t---help---\n");
				fprintf(kconfig, "\t\tInterval for polling endpoint for data transfers.\n");
				fprintf(kconfig, "\t\tExpressed in frames or microframes depending on the\n");
				fprintf(kconfig, "\t\tdevice operating speed (i.e., either 1 millisecond or\n");
				fprintf(kconfig, "\t\t125 µs units).\n");
				fprintf(kconfig, "\t\tFor full-/high-speed isochronous endpoints, this value\n");
				fprintf(kconfig, "\t\tmust be in the range from 1 to 16. The bInterval value\n");
				fprintf(kconfig, "\t\tis used as the exponent for a 2bInterval-1 value; e.g., a\n");
				fprintf(kconfig, "\t\tbInterval of 4 means a period of 8 (24-1).\n");
				fprintf(kconfig, "\t\tFor full-/low-speed interrupt endpoints, the value of\n");
				fprintf(kconfig, "\t\tthis field may be from 1 to 255.\n");
				fprintf(kconfig, "\t\tFor high-speed interrupt endpoints, the bInterval value\n");
				fprintf(kconfig, "\t\tis used as the exponent for a 2bInterval-1 value; e.g., a\n");
				fprintf(kconfig, "\t\tbInterval of 4 means a period of 8 (24-1). This value\n");
				fprintf(kconfig, "\t\tmust be from 1 to 16.\n");
				fprintf(kconfig, "\t\tFor high-speed bulk/control OUT endpoints, the\n");
				fprintf(kconfig, "\t\tbInterval must specify the maximum NAK rate of the\n");
				fprintf(kconfig, "\t\tendpoint. A value of 0 indicates the endpoint never\n");
				fprintf(kconfig, "\t\tNAKs. Other values indicate at most 1 NAK each\n");
				fprintf(kconfig, "\t\tbInterval number of microframes. This value must be\n");
				fprintf(kconfig, "\t\tin the range from 0 to 255.\n");
				fprintf(kconfig, "\t\tSee Chapter 5 description of periods for more detail.\n");


				fprintf(kconfig,"endmenu\n");
				fprintf(kconfig,"endif\n\n");
			}



			fprintf(kconfig,"endmenu\n");
			fprintf(kconfig,"endif\n\n");
		}
		fprintf(kconfig,"endmenu\n\n");
		fprintf(kconfig,"endif\n\n");

	}
	fclose(kconfig);
}



void generate_files(int max_conf, int max_if, int max_ep, int max_string)
{

	FILE *header;
	header = fopen("usbconf.h", "w");

	fprintf(header, "#include \"config.h\"\n#include \"usb.h\"\n\n");

	for(int i =0; i < max_conf; i++){
		fprintf(header, "#if CONFIG_USB_DEVICE_NCONFIGS > %d\n", i);
		fprintf(header, "struct usb_conf%d_s {\n", i);
		fprintf(header, "\tstruct usb_configuration_descriptor config;\n");
		for(int j = 0; j < max_if;j++){
			fprintf(header, "#if CONFIG_USB_CONFIG%d_NINTERFACES > %d\n", i, j);
			fprintf(header, "\tstruct usb_interface_descriptor interface%d;\n", j);
			fprintf(header, "\tstruct usb_endpoint_descriptor interface%d_eps[CONFIG_USB_CONFIG%d_INTERFACE%d_NEPS];\n", j, i , j);
			fprintf(header, "#endif\n");
		}
		fprintf(header,"}  __attribute__ ((packed));\n\n");
		fprintf(header, "#endif\n");
	}
	fprintf(header, "\n\n\n");
	fprintf(header, "struct usb_config_table_s {\n");
	fprintf(header, "\tvoid *config;\n");
	fprintf(header, "\tunsigned int len;\n");
	fprintf(header, "};\n\n");

	fprintf(header, "static char *usb_string_tab[] = {\n");
	for(int i=1; i < 32; i++){
		fprintf(header, "#if CONFIG_USB_NSTRINGS >= %d\n",i);
		fprintf(header, "\tCONFIG_USB_STRING_INDEX_%d,\n",i);
		fprintf(header, "#endif\n");
	}
	fprintf(header, "};\n\n");


//	fprintf(header, "#include <stdio.h>\n#include \"usbconf.h\"\n\n");

	fprintf(header, "struct usb_device_descriptor device_desc = {\n");
	fprintf(header, "\t.bLength = sizeof(struct usb_device_descriptor),\n");
	fprintf(header, "\t.bDescriptorType=1,\n");
	fprintf(header, "\t.bcdUSB=CONFIG_USB_DEVICE_USB_VERSION,\n");
	fprintf(header, "\t.bDeviceClass=CONFIG_USB_DEVICE_CLASS_VAL,\n");
	fprintf(header, "\t.bDeviceSubClass=CONFIG_USB_DEVICE_SUBCLASS,\n");
	fprintf(header, "\t.bDeviceProtocol=CONFIG_USB_DEVICE_PROTOCOL,\n");
	fprintf(header, "\t.bMaxPacketSize0=CONFIG_USB_DEVICE_MXPACKETSIZE,\n");
	fprintf(header, "\t.idVendor=CONFIG_USB_DEVICE_VENDORID,\n");
	fprintf(header, "\t.idProduct=CONFIG_USB_DEVICE_PRODUCTID,\n");
	fprintf(header, "\t.bcdDevice=CONFIG_USB_DEVICE_DEVICEID,\n");
	fprintf(header, "\t.iManufacturer=CONFIG_USB_DEVICE_IMFGR,\n");
	fprintf(header, "\t.iProduct=CONFIG_USB_DEVICE_IPRODUCT,\n");
	fprintf(header, "\t.iSerialNumber=CONFIG_USB_DEVICE_ISERNO,\n");
	fprintf(header, "\t.bNumConfigurations=CONFIG_USB_DEVICE_NCONFIGS,\n");
	fprintf(header, "};\n\n");


	fprintf(header, "struct usb_qualifier_descriptor qualifier_desc = {\n");
	fprintf(header, "\t.bLength = sizeof(struct usb_qualifier_descriptor),\n");
	fprintf(header, "\t.bDescriptorType=6,\n");
	fprintf(header, "\t.bcdUSB=CONFIG_USB_DEVICE_USB_VERSION,\n");
	fprintf(header, "\t.bDeviceClass=CONFIG_USB_DEVICE_CLASS_VAL,\n");
	fprintf(header, "\t.bDeviceSubClass=CONFIG_USB_DEVICE_SUBCLASS,\n");
	fprintf(header, "\t.bDeviceProtocol=CONFIG_USB_DEVICE_PROTOCOL,\n");
	fprintf(header, "\t.bMaxPacketSize0=CONFIG_USB_DEVICE_MXPACKETSIZE,\n");
	fprintf(header, "\t.bNumConfigurations=CONFIG_USB_DEVICE_NCONFIGS,\n");
	fprintf(header, "\t.bReserved=0,\n");
	fprintf(header, "};\n\n");



	fprintf(header, "unsigned char *string_tab[] = {\n");
	fprintf(header, "\tNULL,\n");
	for(int i=0; i< max_string; i++){
		fprintf(header, "#if CONFIG_USB_NSTRINGS >  %d\n", i);
		fprintf(header, "\tCONFIG_USB_STRING_INDEX_%d,\n",i+1);
		fprintf(header, "#endif\n");
	}
	fprintf(header, "};\n\n");




	for(int i =0; i < max_conf; i++){
		fprintf(header, "#if CONFIG_USB_DEVICE_NCONFIGS > %d\n", i);
		fprintf(header, "static struct usb_conf%d_s conf%d = {\n", i, i);
		fprintf(header, "\t.config = {\n");
		fprintf(header, "\t\t.bLength = sizeof(struct usb_configuration_descriptor),\n");
		fprintf(header, "\t\t.bDescriptorType = 2,\n");
		fprintf(header, "\t\t.wTotalLength = sizeof(struct usb_conf%d_s),\n", i);
		fprintf(header, "\t\t.bNumInterfaces = CONFIG_USB_CONFIG%d_NINTERFACES,\n", i);
		fprintf(header, "\t\t.bConfigurationValue=CONFIG_USB_CONFIG%d_CFGVALUE,\n", i);
		fprintf(header, "\t\t.iConfiguration=CONFIG_USB_CONFIG0_ICFG,\n");
		fprintf(header, "\t\t.bmAttributes = 0\n");
		for(int tmp = 0; tmp < 8; tmp++){
			fprintf(header, "#ifdef CONFIG_USB_CONFIG%d_ATTR_D%d\n", i, tmp);
			fprintf(header, "\t\t| %d\n", (1 << tmp));
			fprintf(header, "#endif\n");
		}
		fprintf(header, "\t\t,\n");
		fprintf(header, "\t\t.bMaxPower=CONFIG_USB_CONFIG%d_MXPOWER\n", i);
		fprintf(header, "\t},\n");


		for(int j=0; j<max_if; j++){
			fprintf(header, "#if CONFIG_USB_CONFIG%d_NINTERFACES > %d\n", i, j);
			fprintf(header, "\t.interface%d = {\n", j);
			fprintf(header, "\t\t.bLength=sizeof(struct usb_interface_descriptor),\n");
			fprintf(header, "\t\t.bDescriptorType=4,\n");
			fprintf(header, "\t\t.bInterfaceNumber=CONFIG_USB_CONFIG%d_INTERFACE%d_IFNO,\n", i, j);
			fprintf(header, "\t\t.bAlternateSetting=CONFIG_USB_CONFIG%d_INTERFACE%d_ALT,\n", i, j);
			fprintf(header, "\t\t.bNumEndpoints=CONFIG_USB_CONFIG%d_INTERFACE%d_NEPS,\n",  i, j);
			fprintf(header, "\t\t.bInterfaceClass=CONFIG_USB_CONFIG%d_INTERFACE%d_CLASS_VAL,\n",i,j);
			fprintf(header, "\t\t.bInterfaceSubClass=CONFIG_USB_CONFIG%d_INTERFACE%d_SUBCLASS_VAL,\n", i, j);
			fprintf(header, "\t\t.bInterfaceProtocol=CONFIG_USB_CONFIG%d_INTERFACE%d_PROTOCOL_VAL,\n", i, j);
			fprintf(header, "\t\t.iInterface=CONFIG_USB_CONFIG%d_INTERFACE%d_IIF,\n", i, j);
			fprintf(header, "\t},\n");

			for(int k=0; k < max_ep; k++){
				fprintf(header, "#if CONFIG_USB_CONFIG%d_INTERFACE%d_NEPS > %d\n", i, j, k);

				fprintf(header, "\t.interface%d_eps[%d] = {\n",j, k);
				fprintf(header, "\t\t.bLength=sizeof(struct usb_endpoint_descriptor),\n");
				fprintf(header, "\t\t.bDescriptorType=5,\n");
				fprintf(header, "\t\t.bEndpointAddress=CONFIG_USB_CONFIG%d_INTERFACE%d_EP%d_ADDR,\n", i, j, k);
				fprintf(header, "\t\t.bmAttributes=(CONFIG_USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_NONE << 6)\n\t\t | (CONFIG_USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_USAGE_TYPE_VAL << 4)\n\t\t | (CONFIG_USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_SYNC_TYPE_VAL << 2)\n\t\t | CONFIG_USB_CONFIG%d_INTERFACE%d_EP%d_ATTR_XFER_TYPE_VAL,\n", i,j,k,i,j,k,i,j,k,i,j,k);
				fprintf(header, "\t\t.wMaxPacketSize=CONFIG_USB_CONFIG%d_INTERFACE%d_EP%d_MXPACKETSIZE,\n",i ,j , k);
				fprintf(header, "\t\t.bInterval=CONFIG_USB_CONFIG%d_INTERFACE%d_EP%d_INTERVAL,\n", i,j,k);
				fprintf(header, "\t},\n");

				fprintf(header, "#endif\n");
			}
			fprintf(header, "#endif\n");
		}


		//fprintf(header, "\t.,\n");


		fprintf(header, "};\n");
		fprintf(header, "#endif\n\n");
	}

	fprintf(header, "\n\n\n");
	fprintf(header, "struct usb_config_table_s usb_config_table[] = {\n");
	for(int i=0; i< max_conf; i++){
		fprintf(header, "#if CONFIG_USB_DEVICE_NCONFIGS > %d\n", i);
		fprintf(header, "\t{\n");
		fprintf(header, "\t\t.config = &conf%d,\n", i);
		fprintf(header, "\t\t.len = sizeof(conf%d)\n", i);
		fprintf(header, "\t},\n");
		fprintf(header, "#endif\n");
	}
	fprintf(header, "\t{\n");
	fprintf(header, "\t\t.config = NULL,\n");
	fprintf(header, "\t\t.len = 0\n");
	fprintf(header, "\t}\n");

	fprintf(header, "};\n");
	fclose(header);
}

int main()
{
	generate_kconfig(2, 32, 32, 32);
	//generate_headers(2, 32, 32, 32);
	generate_files(2, 32, 32, 32);
}
