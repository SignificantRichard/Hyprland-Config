hl.config({
	general = {
		gaps_in  = 0,
		gaps_out = 0,

		border_size = 2,

		col = {
			active_border   = { colors = {"rgba(ffffff88)", "rgba(ffffffff)", "rgba(ffffff88)"}, angle = 45 },
			inactive_border = "rgba(595959aa)",
		},

		-- Set to true to enable resizing windows by clicking and dragging on borders and gaps
		resize_on_border = false,

		-- Please see https://wiki.hypr.land/Configuring/Advanced-and-Cool/Tearing/ before you turn this on
		allow_tearing = false,

		layout = "dwindle",
	},

	decoration = {
		rounding       = 0,
		rounding_power = 1,

		-- Change transparency of focused and unfocused windows
		active_opacity   = 1.0,
		inactive_opacity = 1.0,

		shadow = {
			enabled      = false,
			range        = 4,
			render_power = 3,
			color        = 0xee1a1a1a,
		},

		blur = {
			enabled   = true,
			size      = 3,
			passes    = 1,
			vibrancy  = 0.1696,
			popups = true,
			
		},
		
	},

	animations = {
		enabled = true,
	},
})
