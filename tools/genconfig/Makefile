.PHONY: all menuconfig clean

all: config.py

usbconf.h Kconfig: createconfig
	./createconfig

menuconfig .config: Kconfig
	kconfig-mconf Kconfig

config.h: .config generate.sh
	sh generate.sh

genpy: genpy.c config.h usbconf.h
	$(LINK.c) $< -o $@

config.py: genpy
	./genpy

clean:
	$(RM) createconfig usbconf.h Kconfig .config config.h genpy config.py
