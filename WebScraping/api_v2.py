from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

@app.route('/otoendeks/arama', methods=['GET'])
def otoendeks_arama():
    marka = request.args.get('marka', '').lower()
    model = request.args.get('model', '').lower()
    yil = request.args.get('yil', '')

    if not all([marka, model, yil]):
        return jsonify({'error': 'Eksik parametre. marka, model, yil zorunludur.'}), 400

    url = f"https://otoendeks.com/arabam-ne-kadar/{marka}-{model}/{yil}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({'error': 'Sayfa yüklenemedi'}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.find_all("div", class_="itm-link-container")
    if not items:
        return jsonify({'error': 'Araç seçenekleri bulunamadı'}), 404

    sonuçlar = []
    for idx, item in enumerate(items):
        a_tag = item.find("a", class_="pc")
        if not a_tag:
            continue
        href = a_tag.get("href")
        model_name = a_tag.find("span", class_="itm-link-main-txt").text.strip()
        features = a_tag.find("span", class_="itm-link-sub-txt").text.strip()

        sonuçlar.append({
            "id": idx,
            "model": model_name,
            "ozellikler": features,
            "url": "https://otoendeks.com" + href
        })

    return jsonify(sonuçlar)


@app.route('/otoendeks/sonuc', methods=['GET'])
def otoendeks_sonuc():
    secilen_url = request.args.get('url', '')
    if not secilen_url or not secilen_url.startswith("https://otoendeks.com"):
        return jsonify({'error': 'Geçerli bir URL giriniz'}), 400

    try:
        # Aracın detay sayfasını al
        response2 = requests.get(secilen_url, headers=headers)
        soup2 = BeautifulSoup(response2.text, 'html.parser')

        devam_div = soup2.find("div", class_="col-12 col-lg-6 offset-lg-3")
        a_tag = devam_div.find("a", id="devam_et") if devam_div else None
        if not a_tag:
            return jsonify({'error': 'Devam Et linki bulunamadı'}), 500

        devam_href = "https://otoendeks.com" + a_tag.get("href")
        sonuc_url = devam_href + "-sonuc"

        response4 = requests.get(sonuc_url, headers=headers)
        if response4.status_code != 200:
            return jsonify({'error': 'Sonuç sayfası yüklenemedi'}), 500

        soup4 = BeautifulSoup(response4.text, 'html.parser')

        arac = soup4.find("h1", class_="scontent-deger").text.strip()
        otoendeks = soup4.find("span", class_="dgr").text.strip()
        kasko = soup4.find_all("span", class_="ext-scontent-deger")[1].text.strip()

        return jsonify({
            "arac": arac,
            "otoendeks_degeri": otoendeks,
            "kasko_degeri": kasko
        })

    except Exception as e:
        return jsonify({'error': 'İşlem sırasında hata oluştu', 'detail': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
