import json
import os

stream_path = r'd:\installer\laragon\www\api\stream.json'

# Load stream.json
with open(stream_path, 'r', encoding='utf-8') as f:
    streams = json.load(f)

# Find all SportsGrid entries
target_name = "SportsGrid"
sportsgrid_entries = []
other_entries = []

for s in streams:
    if s.get("name", "").strip().lower() == target_name.lower():
        sportsgrid_entries.append(s)
    else:
        other_entries.append(s)

if not sportsgrid_entries:
    print("No SportsGrid entries found.")
    exit()

print(f"Found {len(sportsgrid_entries)} SportsGrid entries.")

# Collect all unique URLs
urls = []
def add_url(u):
    if u and u not in urls:
        urls.append(u)

for s in sportsgrid_entries:
    # Check all possible url fields
    for i in range(1, 10):
        key = f"url_stream_{i}"
        if key in s:
            add_url(s[key])
    if "url_stream" in s:
        add_url(s["url_stream"])

print(f"Found {len(urls)} unique URLs: {urls}")

# Take the first entry as the template
merged_entry = sportsgrid_entries[0].copy()

# Remove old url fields from template
keys_to_remove = ["url_stream"] + [f"url_stream_{i}" for i in range(1, 10)]
for k in keys_to_remove:
    if k in merged_entry:
        del merged_entry[k]

# Add merged URLs
if len(urls) == 1:
    merged_entry["url_stream"] = urls[0]
else:
    for i, url in enumerate(urls, 1):
        merged_entry[f"url_stream_{i}"] = url

# Put back together
new_streams = []
# We keep the relative order of other entries, but where should we put the merged one?
# Let's put it where the first one was.
first_index = -1
for i, s in enumerate(streams):
    if s.get("name", "").strip().lower() == target_name.lower():
        first_index = i
        break

for i, s in enumerate(streams):
    if i == first_index:
        new_streams.append(merged_entry)
    elif s.get("name", "").strip().lower() != target_name.lower():
        new_streams.append(s)

# Save
with open(stream_path, 'w', encoding='utf-8') as f:
    json.dump(new_streams, f, indent=2)

print("Merged SportsGrid entries.")
