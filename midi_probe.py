"""Read-only ALSA raw MIDI endpoint inventory. Never opens a MIDI device."""
from pathlib import Path
import re

def inventory(dev_root=Path("/dev/snd"), cards_file=Path("/proc/asound/cards")):
    try:
        cards=cards_file.read_text(errors="replace")
    except OSError:
        cards=""
    devices=[]
    try:
        paths=sorted(dev_root.glob("midiC*D*"))
    except OSError:
        paths=[]
    for path in paths:
        match=re.fullmatch(r"midiC(\d+)D(\d+)",path.name)
        if not match: continue
        card=int(match.group(1))
        device=int(match.group(2))
        label="unknown"
        for line in cards.splitlines():
            if re.match(r"^\s*"+str(card)+r"\s+\[",line):
                label=line.strip().split(":",1)[-1].strip()
                break
        devices.append({"card":card,"device":device,"label":label,
                        "readable":path.exists()})
    return {"midi_devices":devices,"monitoring":False,"writes_enabled":False}
