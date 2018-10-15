NO_COLOR    = \x1b[0m
COMPILE_COLOR    = \x1b[32;01m
LINK_COLOR    = \x1b[31;01m

	
all:
	@echo -e '$(LINK_COLOR)* Building [$@]$(NO_COLOR)'
	@$(MAKE) -C rsrc/ -j2 $@

clean:
	@echo -e '$(LINK_COLOR)* Cleaning [$@]$(NO_COLOR)'
	@$(MAKE) -C rsrc/ $@

install: all
	@echo -e '$(LINK_COLOR)* Installing [$@]$(NO_COLOR)'
	mkdir -p $(DESTDIR)/usr/share/banners/lliurex-neu
	cp rsrc/*.png $(DESTDIR)/usr/share/banners/lliurex-neu/
