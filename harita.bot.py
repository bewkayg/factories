from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote_plus
import pandas as pd
import random
import time


# İzmir'in başlıca sanayi bölgeleri ve ilçeleri (istediğiniz gibi ekleyip çıkarabilirsiniz)
IZMIR_ARAMALARI = [
    "İzmir Atatürk Organize Sanayi Bölgesi fabrikalar",
    "İzmir Kemalpaşa Organize Sanayi Bölgesi fabrikalar",
    "İzmir Torbalı fabrikalar",
    "İzmir Pancar Organize Sanayi Bölgesi fabrikalar",
    "İzmir İTOB Organize Sanayi Bölgesi fabrikalar",
    "İzmir Gaziemir Ege Serbest Bölgesi fabrikalar",
    "İzmir Bornova Pınarbaşı fabrikalar",
    "İzmir Aliağa Organize Sanayi Bölgesi fabrikalar",
    "İzmir Menemen fabrikalar",
    "İzmir Çiğli fabrikalar",
    "İzmir Tire Organize Sanayi Bölgesi fabrikalar",
    "İzmir Karabağlar sanayi fabrikalar",
    "İzmir Buca fabrikalar",
    "İzmir Ödemiş fabrikalar",
    "İzmir Bergama fabrikalar",
]


def scrape_izmir_fabrikalar(arama_listesi, cikti_dosyasi="izmir_fabrikalar.csv"):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--lang=tr")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    tum_veriler = []
    gorulen_linkler = set()
    cerez_gecildi = False

    try:
        for sira, query in enumerate(arama_listesi, start=1):
            print(f"[{sira}/{len(arama_listesi)}] Taranıyor: {query}")
            url = f"https://www.google.com/maps/search/{quote_plus(query)}"
            driver.get(url)

            # İlk açılışta çerez ekranı çıkarsa kabul et
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

            # Sol sonuç panelini bekle
            try:
                scrollable_div = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]'))
                )
            except Exception:
                print(f"  -> Liste bulunamadı, sonraki bölgeye geçiliyor: {query}")
                continue

            # Paneli sonuna kadar kaydır
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

            # İşletmeleri topla
            businesses = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
            yeni_eklenen = 0

            for business in businesses:
                try:
                    name = business.get_attribute("aria-label")
                    link = business.get_attribute("href")

                    if not name or link in gorulen_linkler:
                        continue
                    gorulen_linkler.add(link)

                    card_text = business.find_element(By.XPATH, "./..").text.replace("\n", " | ")

                    tum_veriler.append({
                        "Arama Bölgesi": query,
                        "Firma Adı": name,
                        "Özet Bilgi": card_text,
                        "Harita Linki": link
                    })
                    yeni_eklenen += 1
                except Exception:
                    continue

            print(f"  -> {yeni_eklenen} yeni fabrika eklendi. (Toplam: {len(tum_veriler)})")

            # Her bölge bittiğinde CSV'yi güncelle (yarıda kesilirse veri kaybı olmaz)
            if tum_veriler:
                df = pd.DataFrame(tum_veriler)
                df.to_csv(cikti_dosyasi, index=False, encoding="utf-8-sig", sep=";")

            # Google engeline takılmamak için bölgeler arası kısa bekleme
            time.sleep(random.uniform(3.0, 5.0))

    finally:
        driver.quit()

    print(f"\nTamamlandı! Toplam {len(tum_veriler)} benzersiz işletme '{cikti_dosyasi}' dosyasına kaydedildi.")


if __name__ == "__main__":
    scrape_izmir_fabrikalar(IZMIR_ARAMALARI, cikti_dosyasi="izmir_fabrikalar.csv")