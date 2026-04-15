import json
import re

api_image_path = r'd:\installer\laragon\www\api\api_image.json'
stream_path = r'd:\installer\laragon\www\api\stream.json'

base_url = "https://jaruba.github.io/channel-logos/export/transparent-color"

# Load api_image.json
with open(api_image_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    data = json.loads("".join(lines[3:]))

# Load stream.json
with open(stream_path, 'r', encoding='utf-8') as f:
    streams = json.load(f)

# Cleaned keys
data_lower = {k.lower(): v for k, v in data.items()}
sorted_keys = sorted(data_lower.keys(), key=len, reverse=True)

# Special logos
cbn_logo = data_lower.get("christian broadcasting network")
# tvri_logo = None # Still can't find it

def clean(name):
    name = name.lower()
    # Remove common prefixes/suffixes
    name = re.sub(r'\bwatch\b', '', name)
    name = re.sub(r'\bon streamku\b', '', name)
    name = re.sub(r'\blive tv\b', '', name)
    name = re.sub(r'\bhd\b', '', name)
    name = re.sub(r'\bstreaming\b', '', name)
    name = re.sub(r'[^\w\s]', ' ', name) # Remove punctuation
    return " ".join(name.split())

stats = {"updated": 0, "cbn": 0, "already_jaruba": 0}

for s in streams:
    original_name = s.get("name", "")
    original_url = s.get("image_url", "")
    
    # If already a jaruba link, skip unless it's a special rule
    # Actually, user says "cek ulang", so let's re-verify all.
    
    name_clean = clean(original_name)
    
    found = False
    
    # TVRI special rule
    if "tvri" in name_clean:
        # Since we don't have tvri logo in api_image, 
        # let's look for any key that might be it.
        # Maybe "television of republic of indonesia"? No.
        pass

    # CBN special rule
    if "cbn" in name_clean:
        if cbn_logo:
            s["image_url"] = f"{base_url}{cbn_logo}"
            stats["cbn"] += 1
            found = True
    
    if not found:
        # 1. Exact match cleaned
        if name_clean in data_lower:
            s["image_url"] = f"{base_url}{data_lower[name_clean]}"
            stats["updated"] += 1
            found = True
        
    if not found:
        # 2. Key in name
        for k in sorted_keys:
            if len(k) < 4: continue
            if k in name_clean:
                s["image_url"] = f"{base_url}{data_lower[k]}"
                stats["updated"] += 1
                found = True
                break
                
    if not found:
        # 3. Name in key (e.g. "Antv" in "Antv Indonesia")
        for k in sorted_keys:
            if len(name_clean) < 4: continue
            if name_clean in k:
                s["image_url"] = f"{base_url}{data_lower[k]}"
                stats["updated"] += 1
                found = True
                break

# Save
with open(stream_path, 'w', encoding='utf-8') as f:
    json.dump(streams, f, indent=2)

print(json.dumps(stats))
