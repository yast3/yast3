# The default target of this Makefile is...
.PHONY: all
all::

INSTALL = install
FIND = find
MKDIR_P = mkdir -p
PIP = $(PYTHON) -m pip
PYTHON ?= python3
RM = rm -f
RM_R = rm -fr
XARGS = xargs

prefix ?= $(HOME)/.local
datadir ?= $(prefix)/share
appdir ?= $(datadir)/applications

install_args =
ifdef DESTDIR
	install_args += --root="$(DESTDIR)"
endif
install_args += --prefix="$(prefix)"
install_args += --disable-pip-version-check
install_args += --upgrade

PYTHON_DIRS = yast3
PYTHON_DIRS += tests

.PHONY: install install-desktop-files install-system dist clean
.PHONY: i18n-update i18n-compile

install:: all install-desktop-files
	$(PIP) install $(install_args) .

install-desktop-files::
	$(MKDIR_P) "$(DESTDIR)$(appdir)"
	$(INSTALL) -m 644 packaging/yast3.desktop "$(DESTDIR)$(appdir)"

install-system::
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: install-system must be run as root (for example: sudo make install-system)." >&2; \
		exit 1; \
	fi
	$(MAKE) prefix=/usr/local install

dist:: clean
	$(PIP) install --upgrade build
	$(PYTHON) -m build --outdir dist .

clean::
	$(FIND) $(PYTHON_DIRS) -name '*.py[cod]' -print0 | $(XARGS) -0 $(RM)

i18n-update::
	pybabel extract -F babel.cfg -o locale/yast3.pot yast3/
	pybabel update -i locale/yast3.pot -d locale -D yast3

i18n-compile::
	pybabel compile -d locale -D yast3
