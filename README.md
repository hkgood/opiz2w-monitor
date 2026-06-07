# Orange Pi Zero 2W LCD Monitor

A system monitoring display for Orange Pi Zero 2W using Waveshare 1.3inch LCD HAT (ST7789VM, 240x240).

## Features

- Real-time system metrics (CPU, RAM, Temperature, Disk)
- Hermes Agent status monitoring
- Network information display
- Service status monitoring
- Clock display with auto-sleep
- Button navigation (Joystick + 3 keys)
- Auto-start on boot via systemd
- Apple / Dieter Rams minimalist design
- Chinese text support

## Hardware Requirements

- Orange Pi Zero 2W
- Waveshare 1.3inch LCD HAT

## Installation

### 1. Enable SPI1 Interface

```bash
sudo ./enable_spi1.sh
sudo reboot
```

### 2. Install Monitor

```bash
sudo ./install.sh
```

### 3. Start Service

```bash
sudo systemctl start lcd-monitor
sudo systemctl enable lcd-monitor  # Auto-start on boot
```

## Usage

### Button Controls

| Button | Action |
|--------|--------|
| Joystick Up | Previous page |
| Joystick Down | Next page |
| KEY1 | Previous page |
| KEY2 | Next page |
| KEY3 | Enter sleep mode |
| Any button | Wake from sleep |

### Pages

1. **System Overview** - CPU, RAM, Temperature, Disk, Uptime
2. **Hermes Agent** - Process status, Memory, CPU, Gateway
3. **Network** - WiFi status, IP, Signal, Speed
4. **Services** - Systemd service status
5. **Clock** - Time, Date, IP (auto-sleep screen)

### Manual Run

```bash
# Run with hardware
sudo python3 /opt/opiz2w-monitor/monitor.py

# Simulation mode (no hardware required)
python3 /opt/opiz2w-monitor/monitor.py --sim
```

## Project Structure

```
opiz2w-monitor/
├── monitor.py          # Main application
├── config.py           # Configuration
├── drivers/
│   ├── lcd.py          # ST7789VM LCD driver
│   └── buttons.py      # Button input handler
├── pages/
│   ├── base.py         # Page base class
│   ├── system.py       # System overview
│   ├── hermes.py       # Hermes Agent status
│   ├── network.py      # Network info
│   ├── services.py     # Service status
│   └── clock.py        # Clock display
├── utils/
│   ├── metrics.py      # System metrics
│   └── hermes_stats.py # Hermes statistics
├── install.sh          # Installation script
├── enable_spi1.sh      # SPI1 setup script
└── requirements.txt    # Python dependencies
```

## Configuration

Edit `config.py` to customize:

- Display settings (rotation, offsets)
- GPIO pin mapping
- Refresh rates
- Colors
- Monitored services

## Troubleshooting

### Display not working

1. Verify SPI1 is enabled: `ls -la /dev/spidev1.*`
2. Check GPIO connections
3. Check service logs: `sudo journalctl -u lcd-monitor`

### Colors inverted

Set `DISPLAY_BGR = True` in `config.py`

## License

MIT
