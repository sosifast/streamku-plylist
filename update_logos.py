import json
import os

api_image_path = r'd:\installer\laragon\www\api\api_image.json'
stream_path = r'd:\installer\laragon\www\api\stream.json'

header_lines = 3
base_url = "https://jaruba.github.io/channel-logos/export/transparent-color"

# Load api_image.json
with open(api_image_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    json_str = "".join(lines[header_lines:])
    api_images = json.loads(json_str)

# Load stream.json
with open(stream_path, 'r', encoding='utf-8') as f:
    streams = json.load(f)

# Normalize api_images keys to lowercase
api_images_lower = {k.lower(): v for k, v in api_images.items()}

# Find special logos
cbn_logo_path = api_images_lower.get("christian broadcasting network")
tvri_logo_path = None
# Check if there's any key that is exactly 'tvri' or contains it
for k, v in api_images_lower.items():
    if k == "tvri":
        tvri_logo_path = v
        break

# If not found exactly, maybe look for common variations
if not tvri_logo_path:
    for k, v in api_images_lower.items():
        if "tvri" in k:
            tvri_logo_path = v
            break

# If still not found, we will report it.
# But for now, let's apply the rule for CBN at least.

stats = {
    "updated": 0,
    "cbn_applied": 0,
    "tvri_applied": 0
}

for s in streams:
    name = s.get("name", "").lower()
    updated = False
    
    # TVRI special rule: "meski ada nama tvri papua, tvri jakarta, tvri sport"
    if "tvri" in name:
        if tvri_logo_path:
            s["image_url"] = f"{base_url}{tvri_logo_path}"
            stats["tvri_applied"] += 1
            updated = True
        # If no TVRI logo found in api_image.json, we can't change it to a Jaruba link.
        # However, the user might want us to use a specific one if it's there.
    
    # CBN special rule: "cbn us tetap di pakai cbn"
    # Even if we don't find a direct match for 'cbn us', we use 'cbn'
    if not updated and "cbn" in name:
        if cbn_logo_path:
            s["image_url"] = f"{base_url}{cbn_logo_path}"
            stats["cbn_applied"] += 1
            updated = True
            
    # Regular matching if not special case
    if not updated:
        # Check for direct match
        if name in api_images_lower:
            s["image_url"] = f"{base_url}{api_images_lower[name]}"
            stats["updated"] += 1
            updated = True
        else:
            # Check if name is in api_images (sometimes name in stream.json is more complex)
            # e.g. "Watch RCTI Live TV" vs "rcti"
            for k, v in api_images_lower.items():
                if k in name and len(k) > 3: # Avoid matching very short strings like 'tv'
                    # But only if it's a "clean" match (e.g. 'rcti' in 'Watch RCTI Live TV')
                    # Actually, let's be conservative to avoid wrong logos.
                    pass

# Save updated stream.json
with open(stream_path, 'w', encoding='utf-8') as f:
    json.dump(streams, f, indent=2)

print(f"Stats: {stats}")
if not tvri_logo_path:
    print("Warning: TVRI logo not found in api_image.json")
if not cbn_logo_path:
    print("Warning: CBN logo (christian broadcasting network) not found in api_image.json")
