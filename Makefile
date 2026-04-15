.DEFAULT_GOAL := help

.PHONY: help clean FORCE

Makefile: ;

help:
	@echo "Usage: make <folder-name>"

%: FORCE
	@if [ ! -d "$@" ]; then \
		echo "Error: folder '$@' does not exist."; \
		exit 1; \
	fi
	@echo "Packaging $@..."
	@rm -f "$@.zip"
	@cd "$@" && zip -rq "../$@.zip" . -x "*.DS_Store"
	@echo "Successfully created $@.zip."

clean:
	@echo "Cleaning up..."
	@rm -f *.zip

FORCE:
