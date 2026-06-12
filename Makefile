PYTHON ?= python3
PIP := $(PYTHON) -m pip

.PHONY: install install-system dist clean

define update_desktop_database
	@if command -v update-desktop-database >/dev/null 2>&1 && [ -d "$(1)" ]; then \
		update-desktop-database "$(1)" >/dev/null 2>&1 || true; \
	fi
endef

install:
	$(PIP) install --upgrade --user .
	$(call update_desktop_database,$${XDG_DATA_HOME:-$$HOME/.local/share}/applications)

install-system:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: install-system requires root privileges." >&2; \
		exit 1; \
	fi
	$(PIP) install --upgrade .
	$(call update_desktop_database,/usr/local/share/applications)

dist: clean
	$(PIP) install --upgrade build
	$(PYTHON) -m build --outdir dist .

clean:
	rm -rf build dist *.egg-info
