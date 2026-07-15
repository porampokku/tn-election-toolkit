from src.scraper import discover_year
from src.downloader import download_all
from src.analyser import analyse

records = discover_year(2026)

download_all(records)

success, failed, scanned = analyse(records)

print()

print("Digital Success :", len(success))
print("Digital Failed  :", len(failed))
print("Scanned         :", len(scanned))
