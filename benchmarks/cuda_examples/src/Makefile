# Get a list of all subdirectories, one level deep
SUBDIRS := $(wildcard */)

.PHONY: all clean $(SUBDIRS)

# Default target: run make in all subdirectories
all: $(SUBDIRS)

# Rule to run make in each subdirectory
$(SUBDIRS):
	@echo "Entering directory $@"
	@$(MAKE) -C $@

# Clean target: run make clean in all subdirectories
clean:
	@for dir in $(SUBDIRS); do \
		if [ -f "$$dir/Makefile" ]; then \
			echo "Cleaning in $$dir"; \
			$(MAKE) -C $$dir clean; \
		else \
			echo "No Makefile in $$dir, skipping clean"; \
		fi; \
	done

# Run target: run make run in all subdirectories
run:
	@for dir in $(SUBDIRS); do \
		if [ -f "$$dir/Makefile" ]; then \
			echo "Running in $$dir"; \
			$(MAKE) -C $$dir run; \
		else \
			echo "No Makefile in $$dir, skipping clean"; \
		fi; \
	done