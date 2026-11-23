import glob
import os
import pandas as pd

dosyalar = glob.glob("veriler/*/*_fabrikalar.csv")

# Daha önce oluşturduğunuz İzmir dosyası ana klasördeyse onu da dahil eder
if os.path.exists("izmir_fabrikalar.csv"):
    dosyalar.append("izmir_fabrikalar.csv")

tablolar = []
for dosya in dosyalar:
    df = pd.read_csv(dosya, sep=";", encoding="utf-8-sig")
    if "İl" not in df.columns:  # Eski İzmir dosyası için Bölge/İl sütunu ekle
        df.insert(0, "Bölge", "Ege")
        df.insert(1, "İl", "İzmir")
    print(f"{os.path.basename(dosya)}: {len(df)} kayıt")
    tablolar.append(df)

ana_df = pd.concat(tablolar, ignore_index=True).drop_duplicates(subset=["Harita Linki"])
ana_df.to_csv("TUM_FABRIKALAR_ANA_LISTE.csv", index=False, encoding="utf-8-sig", sep=";")

print(f"\nToplam {len(ana_df)} benzersiz işletme 'TUM_FABRIKALAR_ANA_LISTE.csv' dosyasında birleştirildi.")