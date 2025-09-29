import requests
from bs4 import BeautifulSoup
import pandas as pd

urls = [
    "https://www.detik.com/jabar/budaya/d-7754945/40-kata-kata-kasar-di-sunda-dan-artinya-jangan-diucapkan",
    "https://www.detik.com/sumut/berita/d-7149551/16-bahasa-medan-kasar-dan-kotor-beserta-artinya",
    "https://id.wiktionary.org/wiki/Kategori:id:Istilah_kasar",
    "https://www.detik.com/bali/budaya/d-7008641/15-kata-kasar-dalam-bahasa-bali-beserta-artinya-hati-hati-mengucapkan",
    "https://www.detik.com/bali/budaya/d-7170831/biar-nggak-asal-sebut-ini-15-kata-kasar-dalam-bahasa-bali-dan-artinya",
    "https://www.kamusbesar.com/daftar-kata-kata-kasar",
    # hapus atau ganti domain yang mati
    # "https://www.katabahasa.com/daftar-kata-kasar-bahasa-indonesia",
    "https://mamikos.com/info/contoh-kata-kasar-di-beberapa-daerah-gnr/",
    "https://www.liputan6.com/hot/read/5556487/20-kata-kasar-bahasa-inggris-yang-sering-digunakan-dan-perlu-dihindari",
    "https://www.detik.com/bali/nusra/d-7021728/kata-kata-kasar-dalam-bahasa-daerah-di-ntt-jangan-asal-sebut",
    "https://www.idntimes.com/men/attitude/bahasa-jawa-kasar-yang-bermakna-umpatan-q9t03-00-qftxr-qlpt4h",
    "https://tesaurus.kemdikbud.go.id/tematis/lema/kasar",
    "https://www.rukita.co/stories/kata-kasar-dalam-bahasa-daerah"

]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/126.0.0.0 Safari/537.36"
}

all_words = []

for url in urls:
    print(f"Mengambil {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Gagal mengambil {url}: {e}")
        continue  # lanjut ke URL berikutnya

    soup = BeautifulSoup(resp.text, "html.parser")

    for li in soup.select("li"):
        text = li.get_text(strip=True)
        if text and len(text.split()) < 6:
            all_words.append(text)

    for p in soup.select("p"):
        text = p.get_text(strip=True)
        if text and len(text.split()) < 6:
            all_words.append(text)

df = pd.DataFrame(sorted(set(all_words)), columns=["kata_kotor"])

df.to_csv("./dataset/kata_kotor.csv", index=False, encoding="utf-8")
df.to_excel("./dataset/kata_kotor.xlsx", index=False)

print(f"Berhasil scraping {len(df)} kata/frasa unik. File kata_kotor.csv dan kata_kotor.xlsx disimpan.")
