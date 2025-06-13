import requests
from bs4 import BeautifulSoup

# Kullanıcıdan bilgi al (sadece marka, model, yıl)
marka = input("Marka: ").lower()
model = input("Model: ").lower()
yil = input("Yıl: ")

# URL oluştur (motor, kasa, yakıt olmadan)
url = f"https://otoendeks.com/arabam-ne-kadar/{marka}-{model}/{yil}"
print(f"\n[+] Sayfa açılıyor: {url}")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Sayfayı çek
response = requests.get(url, headers=headers)
if response.status_code != 200:
    print("❌ Sayfa yüklenemedi:", response.status_code)
    exit()

soup = BeautifulSoup(response.text, "html.parser")

# Araç seçeneklerini bul
items = soup.find_all("div", class_="itm-link-container")
if not items:
    print("❌ Araç seçenekleri bulunamadı.")
    exit()

print("\n🔍 Bulunan Araç Seçenekleri:\n")
araçlar = []
for i, item in enumerate(items):
    a = item.find("a", class_="pc")
    if not a:
        continue
    href = a.get("href")
    text_main = a.find("span", class_="itm-link-main-txt").text.strip()
    text_sub = a.find("span", class_="itm-link-sub-txt").text.strip()
    print(f"{i+1}. {text_main} | {text_sub}")
    araçlar.append(("https://otoendeks.com" + href, text_main, text_sub))

# Kullanıcıdan seçim al
secim = int(input("\nSeçmek istediğiniz aracın numarasını girin: ")) - 1
secilen_url = araçlar[secim][0]
print(f"\n[+] Seçilen araç URL'si: {secilen_url}")

# Seçilen aracın sayfasını çek
response2 = requests.get(secilen_url, headers=headers)
if response2.status_code != 200:
    print("❌ Seçilen sayfa yüklenemedi.")
    exit()

soup2 = BeautifulSoup(response2.text, "html.parser")

# "Devam Et" linkini yakala
devam_div = soup2.find("div", class_="col-12 col-lg-6 offset-lg-3")
if devam_div:
    a_tag = devam_div.find("a", id="devam_et")
    if a_tag:
        devam_href = "https://otoendeks.com" + a_tag.get("href")
        print(f"[+] Devam Et linki bulundu: {devam_href}")
    else:
        print("❌ 'Devam Et' linki bulunamadı.")
        exit()
else:
    print("❌ Devam Et container bulunamadı.")
    exit()

# Devam Et sayfasını çek (tramer girişi olan sayfa)
response3 = requests.get(devam_href, headers=headers)
if response3.status_code != 200:
    print("❌ Tramer sayfası yüklenemedi.")
    exit()

# Tramer input'undan linkin temelini oluştur
sonuc_url = devam_href + "-sonuc"
print(f"[+] Sonuç sayfası: {sonuc_url}")

# Sonuç sayfasını çek
response4 = requests.get(sonuc_url, headers=headers)
if response4.status_code != 200:
    print("❌ Sonuç sayfası yüklenemedi.")
    exit()

soup4 = BeautifulSoup(response4.text, "html.parser")

# Sonuç bilgilerini çıkar
print("\n📊 OtoEndeks Değer Bilgileri:")

try:
    arac = soup4.find("h1", class_="scontent-deger").text.strip()
    otoendeks = soup4.find("span", class_="dgr").text.strip()
    kasko = soup4.find_all("span", class_="ext-scontent-deger")[1].text.strip()

    print("Araç:", arac)
    print("Otoendeks Değeri:", otoendeks)
    print("Kasko Değeri:", kasko)
except Exception as e:
    print("❌ Bilgiler alınamadı — HTML yapısı değişmiş olabilir.")
    print("Hata:", e)
