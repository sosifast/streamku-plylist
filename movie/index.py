import json
import requests
import time
import os

# ==================== KONFIGURASI TMDB ====================
# Dapatkan API Key di https://www.themoviedb.org/settings/api
TMDB_API_KEY = "4eb4d8a4aab96ac282350e006213a02f"  # <-- Ganti dengan API Key TMDB kamu!
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
TMDB_IMAGE_BASE_ORIGINAL = "https://image.tmdb.org/t/p/original"

# Konfigurasi pengambilan data
MAX_PAGES = 1000  # Jumlah halaman yang akan diambil (setiap halaman ~20 film)
LANGUAGE = "en-us"  # Bahasa Indonesia (ganti ke "en-US" untuk Inggris)
REGION = "ID"  # Region Indonesia
SORT_BY = "popularity.desc"  # Urutkan berdasarkan popularitas
MAX_ACTORS = 20  # Maksimal aktor yang diambil per film
MAX_CREW = 10  # Maksimal kru yang diambil per film

# ==================== FUNGSI UTAMA ====================
def get_movies_from_tmdb():
    all_movies = []
    
    print("=" * 60)
    print("📽️  MENGAMBIL DATA FILM DARI TMDB")
    print("=" * 60)
    print(f"API Key: {TMDB_API_KEY[:10]}...")
    print(f"Max Pages: {MAX_PAGES}")
    print(f"Bahasa: {LANGUAGE}")
    print(f"Region: {REGION}")
    print("=" * 60)
    
    for page in range(1, MAX_PAGES + 1):
        print(f"\n📄 Mengambil halaman {page}/{MAX_PAGES}...")
        
        try:
            # Panggil TMDB Discover API
            url = f"{TMDB_BASE_URL}/discover/movie"
            params = {
                "api_key": TMDB_API_KEY,
                "language": LANGUAGE,
                "region": REGION,
                "sort_by": SORT_BY,
                "page": page,
                "include_adult": "false"
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                movies = data.get("results", [])
                
                if not movies:
                    print(f"⚠️  Halaman {page} tidak ada film, berhenti...")
                    break
                
                # Proses setiap film dengan detail lengkap
                for idx, movie in enumerate(movies):
                    movie_id = movie.get("id")
                    print(f"  🎬 Memproses film {idx + 1}/{len(movies)} (ID: {movie_id})...")
                    
                    processed_movie = process_movie_data(movie)
                    all_movies.append(processed_movie)
                
                print(f"✅ Berhasil mengambil {len(movies)} film dari halaman {page}")
                print(f"📊 Total film sejauh ini: {len(all_movies)}")
                
            else:
                print(f"❌ Error halaman {page}: Status {response.status_code}")
                print(f"Pesan: {response.text}")
                break
            
            # Jeda untuk menghindari rate limit
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Error halaman {page}: {str(e)}")
            break
    
    return all_movies

def get_movie_details(movie_id):
    """Ambil detail film lengkap dan credits (aktor & sutradara)"""
    details = {}
    credits = {}
    
    try:
        # Ambil detail film
        detail_url = f"{TMDB_BASE_URL}/movie/{movie_id}"
        detail_params = {
            "api_key": TMDB_API_KEY,
            "language": LANGUAGE,
            "append_to_response": "videos,keywords,similar,recommendations"
        }
        
        detail_response = requests.get(detail_url, params=detail_params, timeout=30)
        if detail_response.status_code == 200:
            details = detail_response.json()
        
        # Ambil credits (aktor & kru)
        credits_url = f"{TMDB_BASE_URL}/movie/{movie_id}/credits"
        credits_params = {
            "api_key": TMDB_API_KEY,
            "language": LANGUAGE
        }
        
        credits_response = requests.get(credits_url, params=credits_params, timeout=30)
        if credits_response.status_code == 200:
            credits = credits_response.json()
            
    except Exception as e:
        print(f"    ⚠️  Gagal mengambil detail film: {str(e)}")
    
    return details, credits

def process_movie_data(movie):
    """Proses data film mentah dari TMDB menjadi format yang diinginkan"""
    
    movie_id = movie.get("id")
    
    # Ambil detail dan credits
    details, credits = get_movie_details(movie_id)
    
    # Ambil data dasar
    title = movie.get("title", "")
    original_title = movie.get("original_title", "")
    overview = movie.get("overview", details.get("overview", ""))
    release_date = movie.get("release_date", details.get("release_date", ""))
    poster_path = movie.get("poster_path", details.get("poster_path", ""))
    backdrop_path = movie.get("backdrop_path", details.get("backdrop_path", ""))
    vote_average = movie.get("vote_average", details.get("vote_average", 0))
    vote_count = movie.get("vote_count", details.get("vote_count", 0))
    popularity = movie.get("popularity", details.get("popularity", 0))
    genre_ids = movie.get("genre_ids", [])
    
    # Data tambahan dari detail
    runtime = details.get("runtime", 0)
    tagline = details.get("tagline", "")
    status = details.get("status", "")
    budget = details.get("budget", 0)
    revenue = details.get("revenue", 0)
    imdb_id = details.get("imdb_id", "")
    homepage = details.get("homepage", "")
    
    # Genres dari detail
    genres = details.get("genres", [])
    
    # Videos
    videos = details.get("videos", {}).get("results", [])
    trailer = next((v for v in videos if v.get("type") == "Trailer"), None)
    
    # Keywords
    keywords = details.get("keywords", {}).get("keywords", [])
    
    # Proses aktor
    cast = credits.get("cast", [])
    actors = []
    for actor in cast[:MAX_ACTORS]:
        actors.append({
            "id": actor.get("id"),
            "name": actor.get("name"),
            "character": actor.get("character"),
            "profile_path": f"{TMDB_IMAGE_BASE}{actor.get('profile_path')}" if actor.get("profile_path") else "",
            "order": actor.get("order")
        })
    
    # Proses sutradara dan kru
    crew = credits.get("crew", [])
    directors = []
    writers = []
    producers = []
    
    for member in crew:
        job = member.get("job", "")
        member_data = {
            "id": member.get("id"),
            "name": member.get("name"),
            "job": job,
            "department": member.get("department"),
            "profile_path": f"{TMDB_IMAGE_BASE}{member.get('profile_path')}" if member.get("profile_path") else ""
        }
        
        if job == "Director":
            directors.append(member_data)
        elif job in ["Screenplay", "Writer", "Author"]:
            writers.append(member_data)
        elif job == "Producer":
            producers.append(member_data)
    
    # Buat URL gambar
    poster_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else ""
    backdrop_url = f"{TMDB_IMAGE_BASE}{backdrop_path}" if backdrop_path else ""
    
    # Buat SEO fields
    seo_title = f"{title} - Nonton Film Online Gratis"
    desc_title = f"Nonton {title} secara online gratis di Streamku. Film dengan rating {vote_average}/10. Tonton sekarang!"
    
    # Buat slug
    slug = title.lower().replace(" ", "-").replace(":", "").replace("'", "").replace('"', "")
    
    # Format tanggal rilis
    year = release_date.split("-")[0] if release_date else ""
    
    # Return dalam format terstruktur
    return {
        "id": movie_id,
        "title": title,
        "original_title": original_title,
        "slug": slug,
        "seo_title": seo_title,
        "desc_title": desc_title,
        "overview": overview,
        "tagline": tagline,
        "release_date": release_date,
        "year": year,
        "runtime": runtime,
        "status": status,
        "budget": budget,
        "revenue": revenue,
        "imdb_id": imdb_id,
        "homepage": homepage,
        "poster_url": poster_url,
        "backdrop_url": backdrop_url,
        "vote_average": vote_average,
        "vote_count": vote_count,
        "popularity": popularity,
        "genre_ids": genre_ids,
        "genres": genres,
        "adult": movie.get("adult", False),
        "actors": actors,
        "directors": directors,
        "writers": writers,
        "producers": producers,
        "trailer": trailer,
        "keywords": keywords
    }

def save_movies_to_database(movies):
    """Simpan film ke database.json"""
    
    output_path = os.path.join(os.path.dirname(__file__), "database.json")
    
    print(f"\n💾 Menyimpan {len(movies)} film ke {output_path}...")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Berhasil menyimpan {len(movies)} film!")

def main():
    # Periksa apakah API Key sudah diisi
    if TMDB_API_KEY == "GANTI_DENGAN_API_KEY_KAMU":
        print("❌ ERROR: Silakan ganti TMDB_API_KEY dengan API Key TMDB kamu!")
        print("\n📝 Cara mendapatkan API Key TMDB:")
        print("1. Buka https://www.themoviedb.org/")
        print("2. Daftar/login akun")
        print("3. Buka Settings > API")
        print("4. Buat API Key baru (pilih Developer)")
        print("5. Salin API Key dan ganti di variabel TMDB_API_KEY\n")
        return
    
    # Ambil semua film
    movies = get_movies_from_tmdb()
    
    if movies:
        # Simpan ke database
        save_movies_to_database(movies)
        
        print("\n" + "=" * 60)
        print(f"🎉 SELESAI! {len(movies)} film berhasil diambil!")
        print("=" * 60)
    else:
        print("\n❌ Tidak ada film yang berhasil diambil.")

if __name__ == "__main__":
    main()
