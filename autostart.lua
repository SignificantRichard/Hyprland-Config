---- AUTOSTART ----

hl.on("hyprland.start", function ()
	hl.exec_cmd("waybar &")
	hl.exec_cmd("kdeconnectd &")
	hl.exec_cmd("hyprpaper &")
	hl.exec_cmd("mako &")
	hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")
end)
