# waypomo

A simple and lightweight Pomodoro timer for Waybar written in Python. It syncs directly with the system clock so it never drifts, and sends desktop notifications when a phase ends. All cycle settings are stored in a plain JSON file that you can easily edit.

<img width="96" height="92" alt="image" src="https://github.com/user-attachments/assets/6d02be93-5867-4409-8421-afa986048f43" />

## Controls
* **Left click:** start or pause.
* **Right click:** skip the current phase.
* **Middle click:** reset the timer.

## Installation

```bash
git clone https://github.com/vintikzq/waypomo.git
cd waypomo
uv tool install .
```

## Waybar Setup

Add the module to your Waybar config (`~/.config/waybar/config.jsonc`):

```jsonc
"custom/waypomo": {
    "format": "{}",
    "return-type": "json",
    "exec": "waypomo",
    "interval": 1,
    "signal": 8,
    "on-click": "waypomo toggle && pkill -RTMIN+8 waybar",
    "on-click-right": "waypomo next && pkill -RTMIN+8 waybar",
    "on-click-middle": "waypomo reset && pkill -RTMIN+8 waybar"
}
```

## Timer Config

On the first run, the config file is created automatically at `~/.config/pomo/config.json`:

```json
{
  "work_min": 45,
  "short_break_min": 15,
  "long_break_min": 60,
  "cycles_before_long": 4,
  "total_cycles": 7
}
```
