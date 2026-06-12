PYTHON ?= python3
PIP := $(PYTHON) -m pip

.PHONY: install install-system dist clean

install:
	$(PIP) install --upgrade --user .
	@applications_dir="$${XDG_DATA_HOME:-$$HOME/.local/share}/applications"; \
	if command -v update-desktop-database >/dev/null 2>&1 && [ -d "$$applications_dir" ]; then \
		update-desktop-database "$$applications_dir" >/dev/null 2>&1 || true; \
	fi

install-system:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: install-system requires root privileges." >&2; \
		exit 1; \
	fi
	$(PIP) install --upgrade .
	@if command -v update-desktop-database >/dev/null 2>&1 && [ -d "/usr/local/share/applications" ]; then \
		update-desktop-database /usr/local/share/applications >/dev/null 2>&1 || true; \
	fi

dist: clean
	$(PIP) install --upgrade build
	$(PYTHON) -m build --outdir dist .

clean:
	rm -rf build dist *.egg-info
