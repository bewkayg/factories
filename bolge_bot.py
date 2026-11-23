import os
import random
import time
from urllib.parse import quote_plus

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


# =============================================================================
# BÖLGE -> İL -> SANAYİ BÖLGELERİ / OSB ARAMA LİSTESİ
# =============================================================================
BOLGELER = {
    "Ege": {
        "Manisa": [
            "Manisa Organize Sanayi Bölgesi fabrikalar",
            "Manisa Muradiye sanayi fabrikalar",
            "Manisa Turgutlu Organize Sanayi Bölgesi fabrikalar",
            "Manisa Akhisar Organize Sanayi Bölgesi fabrikalar",
            "Manisa Salihli Organize Sanayi Bölgesi fabrikalar",
            "Manisa Soma fabrikalar",
        ],
        "Denizli": [
            "Denizli Organize Sanayi Bölgesi fabrikalar",
            "Denizli Merkezefendi tekstil fabrikaları",
            "Denizli Honaz fabrikalar",
            "Denizli Çardak Organize Sanayi Bölgesi fabrikalar",
            "Denizli Pamukkale sanayi fabrikalar",
        ],
        "Aydın": [
            "Aydın ASTİM Organize Sanayi Bölgesi fabrikalar",
            "Aydın Umurlu Organize Sanayi Bölgesi fabrikalar",
            "Aydın Söke Organize Sanayi Bölgesi fabrikalar",
            "Aydın Nazilli Organize Sanayi Bölgesi fabrikalar",
            "Aydın Ortaklar Organize Sanayi Bölgesi fabrikalar",
        ],
        "Uşak": [
            "Uşak Organize Sanayi Bölgesi fabrikalar",
            "Uşak Deri Karma Organize Sanayi Bölgesi fabrikalar",
            "Uşak Banaz fabrikalar",
        ],
        "Afyonkarahisar": [
            "Afyonkarahisar Organize Sanayi Bölgesi fabrikalar",
            "Afyonkarahisar İscehisar mermer fabrikaları",
            "Afyonkarahisar Bolvadin fabrikalar",
            "Afyonkarahisar Sandıklı fabrikalar",
        ],
        "Kütahya": [
            "Kütahya Organize Sanayi Bölgesi fabrikalar",
            "Kütahya Tavşanlı Organize Sanayi Bölgesi fabrikalar",
            "Kütahya Gediz Organize Sanayi Bölgesi fabrikalar",
            "Kütahya Zafer Organize Sanayi Bölgesi fabrikalar",
        ],
        "Muğla": [
            "Muğla Milas Organize Sanayi Bölgesi fabrikalar",
            "Muğla Yatağan sanayi fabrikalar",
            "Muğla Menteşe sanayi fabrikalar",
            "Muğla Fethiye sanayi fabrikalar",
            "Muğla Bodrum sanayi imalat",
        ],
    },
    "Marmara": {
        "İstanbul": [
            "İstanbul İkitelli Organize Sanayi Bölgesi fabrikalar",
            "İstanbul Tuzla Organize Sanayi Bölgesi fabrikalar",
            "İstanbul Dudullu Organize Sanayi Bölgesi fabrikalar",
            "İstanbul Beylikdüzü Organize Sanayi Bölgesi fabrikalar",
            "İstanbul Hadımköy fabrikalar",
            "İstanbul Esenyurt fabrikalar",
            "İstanbul Pendik Kurtköy fabrikalar",
            "İstanbul Silivri fabrikalar",
            "İstanbul Çatalca fabrikalar",
            "İstanbul Başakşehir fabrikalar",
            "İstanbul Sancaktepe fabrikalar",
            "İstanbul Bayrampaşa imalat fabrikalar",
        ],
        "Kocaeli": [
            "Kocaeli Gebze Organize Sanayi Bölgesi fabrikalar",
            "Kocaeli Dilovası Organize Sanayi Bölgesi fabrikalar",
            "Kocaeli Dilovası İMES Makine OSB fabrikalar",
            "Kocaeli Gebze Güzeller OSB fabrikalar",
            "Kocaeli Gebze Plastikçiler OSB fabrikalar",
            "Kocaeli Çayırova TAYSAD OSB fabrikalar",
            "Kocaeli İzmit Arslanbey OSB fabrikalar",
            "Kocaeli Kartepe Köseköy fabrikalar",
            "Kocaeli Başiskele fabrikalar",
        ],
        "Bursa": [
            "Bursa Organize Sanayi Bölgesi fabrikalar",
            "Bursa Nilüfer NOSAB fabrikalar",
            "Bursa Demirtaş DOSAB fabrikalar",
            "Bursa İnegöl Organize Sanayi Bölgesi fabrikalar",
            "Bursa Hasanağa Organize Sanayi Bölgesi fabrikalar",
            "Bursa Kayapa Organize Sanayi Bölgesi fabrikalar",
            "Bursa Kestel Organize Sanayi Bölgesi fabrikalar",
            "Bursa Gemlik fabrikalar",
            "Bursa Orhangazi fabrikalar",
            "Bursa Mustafakemalpaşa OSB fabrikalar",
        ],
        "Tekirdağ": [
            "Tekirdağ Çerkezköy Organize Sanayi Bölgesi fabrikalar",
            "Tekirdağ Velimeşe Organize Sanayi Bölgesi fabrikalar",
            "Tekirdağ Ergene Avrupa Serbest Bölge fabrikalar",
            "Tekirdağ Çorlu fabrikalar",
            "Tekirdağ Kapaklı Organize Sanayi Bölgesi fabrikalar",
            "Tekirdağ Muratlı fabrikalar",
            "Tekirdağ Hayrabolu Organize Sanayi Bölgesi fabrikalar",
        ],
        "Sakarya": [
            "Sakarya 1. Organize Sanayi Bölgesi fabrikalar",
            "Sakarya Hendek 2. Organize Sanayi Bölgesi fabrikalar",
            "Sakarya Söğütlü 3. Organize Sanayi Bölgesi fabrikalar",
            "Sakarya Arifiye fabrikalar",
            "Sakarya Erenler sanayi fabrikalar",
            "Sakarya Ferizli Karasu fabrikalar",
        ],
        "Balıkesir": [
            "Balıkesir Organize Sanayi Bölgesi fabrikalar",
            "Balıkesir Bandırma Organize Sanayi Bölgesi fabrikalar",
            "Balıkesir Gönen fabrikalar",
            "Balıkesir Susurluk fabrikalar",
            "Balıkesir Edremit sanayi fabrikalar",
        ],
        "Yalova": [
            "Yalova Makine İhtisas Organize Sanayi Bölgesi fabrikalar",
            "Yalova Altınova tersane ve fabrikalar",
            "Yalova Çiftlikköy fabrikalar",
            "Yalova Merkez sanayi fabrikalar",
        ],
        "Bilecik": [
            "Bilecik 1. Organize Sanayi Bölgesi fabrikalar",
            "Bilecik 2. Organize Sanayi Bölgesi fabrikalar",
            "Bilecik Bozüyük Organize Sanayi Bölgesi fabrikalar",
            "Bilecik Osmaneli fabrikalar",
        ],
        "Çanakkale": [
            "Çanakkale Organize Sanayi Bölgesi fabrikalar",
            "Çanakkale Biga Organize Sanayi Bölgesi fabrikalar",
            "Çanakkale Çan fabrikalar",
            "Çanakkale Ezine Gıda Organize Sanayi Bölgesi fabrikalar",
        ],
        "Kırklareli": [
            "Kırklareli Organize Sanayi Bölgesi fabrikalar",
            "Kırklareli Lüleburgaz Büyükkarıştıran fabrikalar",
            "Kırklareli Babaeski fabrikalar",
        ],
        "Edirne": [
            "Edirne Organize Sanayi Bölgesi fabrikalar",
            "Edirne Keşan fabrikalar",
            "Edirne Uzunköprü fabrikalar",
        ],
    },
    "Akdeniz": {
        "Adana": [
            "Adana Hacı Sabancı Organize Sanayi Bölgesi fabrikalar",
            "Adana Seyhan sanayi fabrikalar",
            "Adana Yüreğir sanayi fabrikalar",
            "Adana Ceyhan fabrikalar",
            "Adana Kozan Organize Sanayi Bölgesi fabrikalar",
        ],
        "Mersin": [
            "Mersin Tarsus Organize Sanayi Bölgesi fabrikalar",
            "Mersin Serbest Bölge fabrikalar",
            "Mersin Akdeniz sanayi fabrikalar",
            "Mersin Tarsus fabrikalar",
            "Mersin Silifke Organize Sanayi Bölgesi fabrikalar",
        ],
        "Antalya": [
            "Antalya Organize Sanayi Bölgesi fabrikalar",
            "Antalya Serbest Bölge fabrikalar",
            "Antalya Döşemealtı fabrikalar",
            "Antalya Kepez sanayi fabrikalar",
            "Antalya Aksu fabrikalar",
            "Antalya Manavgat sanayi fabrikalar",
        ],
        "Hatay": [
            "Hatay İskenderun Organize Sanayi Bölgesi fabrikalar",
            "Hatay Payas Organize Sanayi Bölgesi fabrikalar",
            "Hatay Antakya Organize Sanayi Bölgesi fabrikalar",
            "Hatay Dörtyol fabrikalar",
            "Hatay Erzin fabrikalar",
        ],
        "Kahramanmaraş": [
            "Kahramanmaraş Organize Sanayi Bölgesi fabrikalar",
            "Kahramanmaraş Türkoğlu Organize Sanayi Bölgesi fabrikalar",
            "Kahramanmaraş Tomsuklu OSB fabrikalar",
            "Kahramanmaraş Erkenez sanayi fabrikalar",
            "Kahramanmaraş Elbistan fabrikalar",
        ],
        "Osmaniye": [
            "Osmaniye Organize Sanayi Bölgesi fabrikalar",
            "Osmaniye Kadirli Organize Sanayi Bölgesi fabrikalar",
        ],
        "Isparta": [
            "Isparta Süleyman Demirel Organize Sanayi Bölgesi fabrikalar",
            "Isparta Merkez sanayi fabrikalar",
            "Isparta Yalvaç fabrikalar",
        ],
        "Burdur": [
            "Burdur Organize Sanayi Bölgesi fabrikalar",
            "Burdur 2. Organize Sanayi Bölgesi fabrikalar",
            "Burdur Bucak mermer ve OSB fabrikalar",
        ],
    },
}

# =============================================================================
# AYARLAR
# =============================================================================
# Hangi bölgeleri taramak istediğinizi buradan seçebilirsiniz.
# Örnek: Sadece Ege için ["Ege"] yazın; hepsi için ["Ege", "Marmara", "Akdeniz"]
HEDEF_BOLGELER = ["Ege", "Marmara", "Akdeniz"]

# Sadece belirli illeri taramak isterseniz doldurun; boş [] bırakırsanız seçili bölgedeki tüm illeri tarar.
# Örnek: ["Manisa", "Denizli"]
HEDEF_ILLER = []

ANA_KLASOR = "veriler"
TAMAMLANANLAR_DOSYASI = os.path.join(ANA_KLASOR, "tamamlanan_iller.txt")


def dosya_adi_temizle(metin):
    cevirme = str.maketrans("çğıöşüÇĞİÖŞÜ ", "cgiosuCGIOSU_")
    return metin.translate(cevirme)


def tamamlanan_illeri_oku():
    if not os.path.exists(TAMAMLANANLAR_DOSYASI):
        return set()
    with open(TAMAMLANANLAR_DOSYASI, "r", encoding="utf-8") as f:
        return {satir.strip() for satir in f if satir.strip()}


def ili_tamamlandi_isaretle(anahtar):
    os.makedirs(ANA_KLASOR, exist_ok=True)
    with open(TAMAMLANANLAR_DOSYASI, "a", encoding="utf-8") as f:
        f.write(f"{anahtar}\n")


def tarayici_baslat(driver_path):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--lang=tr")
    # Arka planda (pencere açmadan) çalıştırmak isterseniz alttaki satırın başındaki # işaretini kaldırın:
    # options.add_argument("--headless=new")
    return webdriver.Chrome(service=Service(driver_path), options=options)


def il_tara(driver_path, bolge, il, arama_listesi):
    bolge_klasoru = os.path.join(ANA_KLASOR, dosya_adi_temizle(bolge))
    os.makedirs(bolge_klasoru, exist_ok=True)

    csv_yolu = os.path.join(bolge_klasoru, f"{dosya_adi_temizle(il)}_fabrikalar.csv")

    # Yarıda kalmış bir il tekrar başlatılırsa mevcut kayıtları koru
    tum_veriler = []
    gorulen_linkler = set()
    if os.path.exists(csv_yolu):
        try:
            mevcut_df = pd.read_csv(csv_yolu, sep=";", encoding="utf-8-sig")
            tum_veriler = mevcut_df.to_dict("records")
            gorulen_linkler = set(mevcut_df["Harita Linki"].dropna().tolist())
            print(f"  -> Mevcut dosyadan {len(tum_veriler)} kayıt yüklendi, kaldığı yerden devam ediliyor.")
        except Exception:
            pass

    driver = tarayici_baslat(driver_path)
    cerez_gecildi = False

    try:
        for sira, query in enumerate(arama_listesi, start=1):
            print(f"  [{sira}/{len(arama_listesi)}] Taranıyor: {query}")
            url = f"https://www.google.com/maps/search/{quote_plus(query)}"
            driver.get(url)

            if not cerez_gecildi:
                try:
                    accept_btn = WebDriverWait(driver, 4).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//button[.//span[contains(text(), "Tümünü kabul et") or contains(text(), "Accept all")]]')
                        )
                    )
                    accept_btn.click()
                    time.sleep(2)
                except Exception:
                    pass
                cerez_gecildi = True

            try:
                scrollable_div = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]'))
                )
            except Exception:
                print("    -> Liste yüklenemedi, sonraki aramaya geçiliyor.")
                continue

            last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            same_height_count = 0

            while same_height_count < 3:
                driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[0].scrollHeight);",
                    scrollable_div
                )
                time.sleep(random.uniform(2.0, 3.2))
                new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

                if new_height == last_height:
                    same_height_count += 1
                else:
                    same_height_count = 0
                    last_height = new_height

            businesses = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
            yeni_eklenen = 0

            for business in businesses:
                try:
                    name = business.get_attribute("aria-label")
                    link = business.get_attribute("href")

                    if not name or not link or link in gorulen_linkler:
                        continue
                    gorulen_linkler.add(link)

                    try:
                        card_text = business.find_element(By.XPATH, "./..").text.replace("\n", " | ")
                    except Exception:
                        card_text = ""

                    tum_veriler.append({
                        "Bölge": bolge,
                        "İl": il,
                        "Arama Sorgusu": query,
                        "Firma Adı": name,
                        "Özet Bilgi": card_text,
                        "Harita Linki": link,
                    })
                    yeni_eklenen += 1
                except Exception:
                    continue

            print(f"    -> +{yeni_eklenen} yeni kayıt (İl toplamı: {len(tum_veriler)})")

            if tum_veriler:
                df = pd.DataFrame(tum_veriler)
                df.to_csv(csv_yolu, index=False, encoding="utf-8-sig", sep=";")

            time.sleep(random.uniform(3.0, 5.0))

    finally:
        driver.quit()

    print(f"TAMAMLANDI: {bolge} / {il} -> {len(tum_veriler)} kayıt '{csv_yolu}' dosyasına kaydedildi.\n")


def main():
    os.makedirs(ANA_KLASOR, exist_ok=True)
    driver_path = ChromeDriverManager().install()
    tamamlananlar = tamamlanan_illeri_oku()

    for bolge in HEDEF_BOLGELER:
        if bolge not in BOLGELER:
            print(f"Uyarı: '{bolge}' bölgesi bulunamadı, atlanıyor.")
            continue

        print(f"\n==================== {bolge.upper()} BÖLGESİ BAŞLIYOR ====================")
        for il, arama_listesi in BOLGELER[bolge].items():
            if HEDEF_ILLER and il not in HEDEF_ILLER:
                continue

            anahtar = f"{bolge}|{il}"
            if anahtar in tamamlananlar:
                print(f"[ATLANDI] {bolge} / {il} daha önce tamamlanmış.")
                continue

            print(f"\n>>> {bolge} / {il} taranıyor ({len(arama_listesi)} bölge/OSB)...")
            il_tara(driver_path, bolge, il, arama_listesi)
            ili_tamamlandi_isaretle(anahtar)

            # İller arası kısa mola
            time.sleep(random.uniform(5.0, 8.0))

    print("\nSeçili tüm bölge ve illerin taraması tamamlandı!")


if __name__ == "__main__":
    main()