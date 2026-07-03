"""UI components for the Proxy module (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.core.proxy import ProxyConfig

PROXY_FILE = "/etc/sysconfig/proxy"


class ProxyWindow(Gtk.ApplicationWindow):
    config: ProxyConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(640, 360)
        self.set_title(_("Proxy Configuration — YaST3"))

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.main_box.set_margin_top(12)
        self.main_box.set_margin_bottom(12)
        self.main_box.set_margin_start(12)
        self.main_box.set_margin_end(12)

        self.enabled_check = Gtk.CheckButton(label=_("Enable Proxy"))
        self.main_box.append(self.enabled_check)

        self.http_entry = self._build_input_row(_("HTTP Proxy"), _("http://host:port"))
        self.https_entry = self._build_input_row(_("HTTPS Proxy"), _("http://host:port"))
        self.ftp_entry = self._build_input_row(_("FTP Proxy"), _("http://host:port"))
        self.no_proxy_entry = self._build_input_row(
            _("No Proxy"),
            _("localhost,127.0.0.1,.example.com"),
        )

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_halign(Gtk.Align.END)

        self.save_btn = Gtk.Button(label=_("Save"))
        self.save_btn.add_css_class("suggested-action")
        self.save_btn.connect("clicked", self._on_save_clicked)
        button_box.append(self.save_btn)

        self.main_box.append(button_box)
        self.set_child(self.main_box)

        self._load_config()

    def _build_input_row(self, label_text: str, placeholder: str) -> Gtk.Entry:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        label = Gtk.Label(label=label_text)
        label.set_size_request(140, -1)
        label.set_halign(Gtk.Align.START)
        row.append(label)

        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder)
        entry.set_hexpand(True)
        row.append(entry)

        self.main_box.append(row)
        return entry

    def _load_config(self) -> None:
        try:
            self.config = ProxyConfig()
            self.enabled_check.set_active(self.config.get("PROXY_ENABLED") == "yes")
            self.http_entry.set_text(str(self.config.get("HTTP_PROXY", "")))
            self.https_entry.set_text(str(self.config.get("HTTPS_PROXY", "")))
            self.ftp_entry.set_text(str(self.config.get("FTP_PROXY", "")))
            self.no_proxy_entry.set_text(str(self.config.get("NO_PROXY", "")))
        except FileNotFoundError:
            self._show_message_dialog(
                Gtk.MessageType.WARNING,
                _("Error"),
                _("{0} not found.").format(PROXY_FILE),
            )
        except PermissionError:
            self._show_message_dialog(
                Gtk.MessageType.WARNING,
                _("Error"),
                _("Cannot read {0}. Root permission required.").format(PROXY_FILE),
            )
        except Exception as e:
            self._show_message_dialog(
                Gtk.MessageType.WARNING,
                _("Error"),
                _("Failed to load proxy configuration: {0}").format(str(e)),
            )

    def _on_save_clicked(self, button: Gtk.Button) -> None:
        self.config.update({
            "PROXY_ENABLED": "yes" if self.enabled_check.get_active() else "no",
            "HTTP_PROXY": self.http_entry.get_text().strip(),
            "HTTPS_PROXY": self.https_entry.get_text().strip(),
            "FTP_PROXY": self.ftp_entry.get_text().strip(),
            "NO_PROXY": self.no_proxy_entry.get_text().strip(),
        })

        try:
            self.config.write_pkexec()
            self._show_message_dialog(
                Gtk.MessageType.INFO,
                _("Success"),
                _("Proxy configuration saved successfully."),
            )
            self.close()
        except PermissionError:
            self._show_message_dialog(
                Gtk.MessageType.ERROR,
                _("Error"),
                _("Permission denied. Root permission required."),
            )
        except Exception as e:
            self._show_message_dialog(
                Gtk.MessageType.ERROR,
                _("Error"),
                _("Failed to save proxy configuration: {0}").format(str(e)),
            )

    def _show_message_dialog(self, msg_type: Gtk.MessageType, title: str, message: str) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=msg_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()
