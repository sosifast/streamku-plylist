
import json
import requests
import time

# Konfigurasi API
API_URL = "https://reelshort-unofficial-api.p.rapidapi.com/reelshort/episode"
HEADERS = {
    "x-rapidapi-host": "reelshort-unofficial-api.p.rapidapi.com",
    "x-rapidapi-key": "8a4050d6c0msh88ab499efb777a0p1f20edjsne9b08be76c66",
    "Content-Type": "application/json"
}

# Baca data.json
with open("data.json", "r", encoding="utf-8") as f:
    data_list = json.load(f)

all_results = []
episode_list = []

for item in data_list:
    keyword = item["keyword"]
    total_episode = int(item["total_episode"])
    
    print(f"Memproses series dengan keyword: {keyword}")
    print(f"Total episode: {total_episode}")
    
    # Buat daftar episode untuk episode.json
    ep_data = {}
    series_results = []
    
    for ep_no in range(1, total_episode + 1):
        # Ganti episode-1- menjadi episode-X-
        episode_id = keyword.replace("episode-1-", f"episode-{ep_no}-")
        
        print(f"Mengambil episode {ep_no}...")
        
        try:
            # Panggil API
            payload = {"episode_id": episode_id}
            response = requests.post(API_URL, json=payload, headers=HEADERS)
            
            if response.status_code == 200:
                result = response.json()
                series_results.append(result)
                
                # Tambahkan ke episode_data
                ep_key = f"s{ep_no}"
                ep_data[ep_key] = result.get("data", {}).get("video_url", "")
            else:
                print(f"Error untuk episode {ep_no}: Status {response.status_code}")
                ep_key = f"s{ep_no}"
                ep_data[ep_key] = ""
            
            # Beri jeda untuk menghindari rate limit
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error untuk episode {ep_no}: {str(e)}")
            ep_key = f"s{ep_no}"
            ep_data[ep_key] = ""
    
    all_results.extend(series_results)
    episode_list.append(ep_data)

# Simpan ke result.json
with open("result.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

# Simpan ke episode.json
with open("episode.json", "w", encoding="utf-8") as f:
    json.dump(episode_list, f, indent=2, ensure_ascii=False)

print("Selesai! Data telah disimpan ke result.json dan episode.json")
