#!/bin/bash
# Orange Pi Zero 2W - Enable SPI1 for LCD HAT
# This script enables SPI1 interface for Waveshare LCD HAT

set -e

echo "=========================================="
echo "  Enabling SPI1 for LCD HAT"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: Please run as root (sudo ./enable_spi1.sh)"
    exit 1
fi

# Backup original device tree
echo "[1/4] Backing up device tree..."
DTB_PATH="/boot/dtb/allwinner/sun50i-h618-orangepi-zero2w.dtb"
if [ -f "$DTB_PATH" ] && [ ! -f "${DTB_PATH}.bak" ]; then
    cp "$DTB_PATH" "${DTB_PATH}.bak"
    echo "  Backup created: ${DTB_PATH}.bak"
fi

# Create overlay directory
echo "[2/4] Creating overlay directory..."
OVERLAY_DIR="/boot/dtb/allwinner/overlay"
mkdir -p "$OVERLAY_DIR"

# Create SPI1 overlay device tree source
echo "[3/4] Creating SPI1 overlay..."
cat > /tmp/spi1-lcd.dts << 'EOF'
/dts-v1/;
/plugin/;

/ {
    compatible = "allwinner,sun50i-h618";

    fragment@0 {
        target = <&spi1>;
        __overlay__ {
            status = "okay";
            pinctrl-names = "default";
            pinctrl-0 = <&spi1_pins>, <&spi1_cs1_pin>;
            
            spidev@1 {
                compatible = "rohm,dh2228fv";
                reg = <1>;
                spi-max-frequency = <20000000>;
            };
        };
    };

    fragment@1 {
        target = <&pio>;
        __overlay__ {
            spi1_pins: spi1-pins {
                pins = "PH6", "PH7", "PH8";
                function = "spi1";
            };
            
            spi1_cs1_pin: spi1-cs1-pin {
                pins = "PH9";
                function = "spi1";
            };
        };
    };
};
EOF

# Compile overlay
echo "  Compiling overlay..."
dtc -@ -I dts -O dtb -o "${OVERLAY_DIR}/spi1-lcd.dtbo" /tmp/spi1-lcd.dts

# Update armbianEnv.txt
echo "[4/4] Updating boot configuration..."
ENV_FILE="/boot/armbianEnv.txt"

# Check if overlay already enabled
if grep -q "spi1-lcd" "$ENV_FILE" 2>/dev/null; then
    echo "  SPI1 overlay already enabled in armbianEnv.txt"
else
    # Add overlay if not present
    if grep -q "^overlays=" "$ENV_FILE" 2>/dev/null; then
        # Append to existing overlays line
        sed -i 's/^overlays=.*/& spi1-lcd/' "$ENV_FILE"
    else
        echo "overlays=spi1-lcd" >> "$ENV_FILE"
    fi
    echo "  Added spi1-lcd overlay to armbianEnv.txt"
fi

# Enable SPI device
echo ""
echo "Verifying SPI1 configuration..."
if [ -e /dev/spidev1.0 ] || [ -e /dev/spidev1.1 ]; then
    echo "  SPI1 device found!"
else
    echo "  SPI1 device will be available after reboot."
fi

echo ""
echo "=========================================="
echo "  Setup complete!"
echo "=========================================="
echo ""
echo "  Please REBOOT the system for changes to take effect:"
echo "    sudo reboot"
echo ""
echo "  After reboot, verify SPI1 is working:"
echo "    ls -la /dev/spidev1.*"
echo ""
echo "=========================================="
