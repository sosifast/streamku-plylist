import json
import requests
import os

# ==================== KONFIGURASI TMDB ====================
TMDB_API_KEY = "4eb4d8a4aab96ac282350e006213a02f"  # <-- Ganti dengan API Key TMDB kamu!
TMDB_BASE_URL = "https://api.themoviedb.org/3"
LANGUAGE = "en-US"

def get_genres():
    print("🎭 MENGAMBIL DATA GENRE FILM DARI TMDB")
    print("=" * 60)
    
    try:
        url = f"{TMDB_BASE_URL}/genre/movie/list"
        params = {
            "api_key": TMDB_API_KEY,
            "language": LANGUAGE
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            genres = data.get("genres", [])
            
            # Simpan ke genres.json
            output_path = os.path.join(os.path.dirname(__file__), "genres.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(genres, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Berhasil mengambil {len(genres)} genre!")
            print(f"💾 Disimpan ke: {output_path}")
            print("\nDaftar Genre:")
            for genre in genres:
                print(f"  - {genre['id']}: {genre['name']}")
                
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"Pesan: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    if TMDB_API_KEY == "GANTI_DENGAN_API_KEY_KAMU":
        print("❌ ERROR: Silakan ganti TMDB_API_KEY dengan API Key TMDB kamu terlebih dahulu!")
    else:
        get_genres()
