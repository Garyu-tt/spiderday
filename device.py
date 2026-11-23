"""Read-only Linux USB inventory for Spider V 20. Never opens audio or MIDI endpoints."""
from pathlib import Path

VENDOR = "0e41"
PRODUCT = "506f"

def probe_usb(root="/sys/bus/usb/devices"):
    matches = []
    for entry in sorted(Path(root).glob("*")):
        try:
            vendor = (entry / "idVendor").read_text().strip().lower()
            product = (entry / "idProduct").read_text().strip().lower()
            if vendor != VENDOR or product != PRODUCT:
                continue
            def read(name):
                try:
                    return (entry / name).read_text().strip()
                except (OSError, UnicodeError):
                    return None
            matches.append({"sysfs": entry.name, "vendor_id": vendor,
                            "product_id": product, "manufacturer": read("manufacturer"),
                            "product": read("product"), "serial": read("serial"),
                            "busnum": read("busnum"), "devnum": read("devnum")})
        except (OSError, UnicodeError):
            continue
    return matches
