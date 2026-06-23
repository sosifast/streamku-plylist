import json
import os
import urllib.request
import urllib.parse
from html.parser import HTMLParser

class OpenDirParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    # Abaikan link parent directory atau query string sorting
                    if value in ("../", "/", "?C=N;O=D", "?C=M;O=A", "?C=S;O=A", "?C=D;O=A") or value.startswith("?"):
                        continue
                    full_url = urllib.parse.urljoin(self.base_url, value)
                    self.links.append((value, full_url))

def crawl_directory(url, results=None):
    if results is None:
        results = []
    
    # Mencegah endless loop jika ada link yang aneh
    if not url.endswith('/'):
        url += '/'
        
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            parser = OpenDirParser(url)
            parser.feed(html)
            
            for href, full_url in parser.links:
                # Jika link berupa direktori (biasanya diakhiri dengan '/')
                if href.endswith('/'):
                    print(f"Mencari di dalam folder: {full_url}")
                    crawl_directory(full_url, results)
                else:
                    # Cek ekstensi file
                    ext = os.path.splitext(urllib.parse.urlparse(full_url).path)[1].lower()
                    if ext in ('.mp4', '.mkv', '.ts'):
                        # Decode nama file dari format URL (misalnya %20 menjadi spasi)
                        movie_name = urllib.parse.unquote(href)
                        results.append({
                            "movie_name": movie_name,
                            "link": full_url
                        })
                        print(f"Ditemukan: {movie_name}")
    except Exception as e:
        print(f"Error saat memproses {url}: {e}")
        
    return results

def main():
    link_file = r"d:\python\getlink\link.txt"
    result_file = r"d:\python\getlink\result.json"
    
    # Membaca URL dari link.txt
    urls_to_crawl = []
    if os.path.exists(link_file):
        with open(link_file, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("url="):
                    urls_to_crawl.append(line[4:])
                elif line.startswith("http"):
                    urls_to_crawl.append(line)
    
    if not urls_to_crawl:
        print("Tidak ada URL yang valid di link.txt")
        return
        
    all_results = []
    for url in urls_to_crawl:
        print(f"Memulai crawl pada: {url}")
        results = crawl_directory(url)
        all_results.extend(results)
        
    # Menyimpan ke result.json
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)
        
    print(f"\nCrawl selesai! Berhasil menyimpan {len(all_results)} file ke {result_file}")

if __name__ == "__main__":
    main()
