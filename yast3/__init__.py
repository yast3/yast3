"""YaST3 Qt6 settings application."""

import builtins

from . import i18n

i18n.init_i18n()
builtins.__dict__["_"] = i18n.gettext_func()

