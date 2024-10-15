all: plugin

plugin:
	$(MAKE) -C inst_pass/
	$(MAKE) -C clang-examples/FloatGuard-plugin

clean:
	$(MAKE) -C inst_pass/ clean
	$(MAKE) -C clang-examples/FloatGuard-plugin clean

cleanall:
	$(MAKE) -C inst_pass/ cleanall
	$(MAKE) -C clang-examples/FloatGuard-plugin cleanall