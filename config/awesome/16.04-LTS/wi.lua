local awful = require("awful")
local wibox = require("wibox")
local beautiful = require("beautiful")
local vicious = require("vicious")
local naughty = require("naughty")



-- CONSTANTS
-- -----------------------------------------------------------------------
local HOME  = os.getenv('HOME')

local ICONS = '.config/awesome/themes/default/icons/'

local COLOR_TITLE  = '#D6CCDC'
local COLOR_COLD   = '#AECF96'
local COLOR_WARM   = '#FF5656'
local COLOR_WARMER = '#C45E5E'
local COLOR_HOT    = '#E80D0D'


-- utility functions
-- -----------------------------------------------------------------------
local function colorize(color, string)
    return '<span color="'..color..'">'..string..'</span>'
end

local function menuitem(title, color, value)
    if title == '' then return colorize(color, value)
    else return colorize(COLOR_TITLE, title) .. ' ' .. colorize(color, value)
    end
end

local function colorizer(title)
    return (
        function (widget, args)
            if     args[1] >= 75 then return menuitem(title, COLOR_HOT,    args[1] .. '%')
            elseif args[1] >= 50 then return menuitem(title, COLOR_WARM,   args[1] .. '%')
            elseif args[1] >= 25 then return menuitem(title, COLOR_WARMER, args[1] .. '%')
            elseif args[1] >= 0  then return menuitem(title, COLOR_COLD,   args[1] .. '%')
            end
        end
    )
end

local function shell(cmd)
    return "x-terminal-emulator -e " .. cmd
end

local function action_icon(name, cmd)
    icon = wibox.widget.imagebox()
    icon:set_image(ICONS .. name .. '.png')
    icon:buttons( awful.button({ }, 1,
        function () awful.util.spawn(cmd) end) 
    )
    return icon
end

local function action_bar(widget, format, interval, cmd)
    bar = awful.widget.progressbar()
    bar:set_width(8)
    bar:set_height(10)
    bar:set_ticks(true)
    bar:set_ticks_size(2)
    bar:set_vertical(true)
    bar:set_background_color(beautiful.fg_off_widget)
    bar:set_color(beautiful.fg_widget)
    -- bar from green to red
    bar:set_color({ 
        type = "linear", 
        from = { 0, 0 }, 
        to   = { 0, 30 },
        -- stops = { { 0, "#AECF96" }, { 1, "#FF5656" } } 
        stops = { { 0, COLOR_COLD }, { 1, COLOR_WARM } } 
    })
    box = wibox.layout.margin(bar, 2, 2, 4, 4)
    box:buttons( awful.button({ }, 1,
        function () awful.util.spawn(cmd) end)
    )
    vicious.register(bar, widget, format, interval)
    return box
end


-- spacers
-- -----------------------------------------------------------------------
spacer = wibox.widget.textbox()
spacer:set_text(' | ')

space = wibox.widget.textbox()
space:set_text(" ")

-- icons
-- -----------------------------------------------------------------------
icon_clock  = action_icon('clock', shell('date'))
icon_cpu    = action_icon('cpu',   shell('htop'))
icon_mem    = action_icon('mem',   shell('htop'))
icon_net_up = action_icon('up',    shell('htop'))
icon_net_dw = action_icon('down',  shell('htop'))
icon_disk   = action_icon('disk',  shell('htop'))

-- text widgets
-- -----------------------------------------------------------------------
cputxt = wibox.widget.textbox()
vicious.register(cputxt,
                 vicious.widgets.cpu,
                 colorizer(''),
                 3)

memtxt = wibox.widget.textbox()
vicious.register(memtxt,
                 vicious.widgets.mem,
                 colorizer(''),
                 3)

nettxt = wibox.widget.textbox()
vicious.register(nettxt,
                 vicious.widgets.net,
                 "▼ ${ens33 down_kb} ▲ ${ens33 up_kb}",
                 3)

disktxt = wibox.widget.textbox()
vicious.register(disktxt,
                 vicious.widgets.fs,
                 "${/ used_p}%",
                 60)


-- progress bars
-- -----------------------------------------------------------------------

bar_cpu  = action_bar(vicious.widgets.cpu,  "$1",           5, shell('htop'))
bar_mem  = action_bar(vicious.widgets.mem,  "$1",           5, shell('htop'))
bar_fs   = action_bar(vicious.widgets.fs,   "${/ used_p}", 60, shell('ncdu')) 


