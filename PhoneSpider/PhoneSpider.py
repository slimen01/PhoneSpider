import csv
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy import signals
import pandas as pd
from pymongo import MongoClient
class PhoneSpider(scrapy.Spider):
    name = "Phone"
    allowed_domains = ["mytek.tn"]
    start_urls = ["https://www.mytek.tn/telephonie-tunisie/smartphone-mobile-tunisie/telephone-portable.html"]

    def parse(self, response):
        for selector in response.css('li.product-item'):
            yield {
                'title': selector.css('a.product-item-link::text').get(),
                'price': selector.css('span.price::text').get(),
                'reference': selector.css('div.skuDesktop::text').get(),
                'description': selector.css('div.product-item-description::text').get()
            }

        next_page_link = response.css('li.pages-item-next > a::attr(href)').get()
        if next_page_link:
            yield response.follow(next_page_link, callback=self.parse)
        else:
            self.log('No more pages to scrape.')

def phone_spider_result():
    phone_results = []

    def crawler_results(item, **kwargs):
        phone_results.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_scraped)
    crawler_process = CrawlerProcess()
    crawler_process.crawl(PhoneSpider)
    crawler_process.start()
    return phone_results

if __name__ == "__main__":
    phone_data = phone_spider_result()

    if phone_data:
        keys = phone_data[0].keys()
        with open('My_Tek_Phones.csv', 'w', newline='', encoding='utf-8') as output_file_name:
            writer = csv.DictWriter(output_file_name, fieldnames=keys)
            writer.writeheader()
            writer.writerows(phone_data)
    else:
        print("No data to write.")


# Charger les données pour les téléphones
mytek_phone_data = pd.read_csv("My_Tek_Phones.csv")
mytek_data = pd.read_csv("My_Tek.csv")

# Supprimer les doublons basés sur la référence
mytek_phone_data.drop_duplicates(subset="reference", inplace=True)
mytek_data.drop_duplicates(subset="reference", inplace=True)

# Fonction de nettoyage des données
def clean_data(data, site_name):
    print(f"[INFO] Nettoyage des données pour {site_name}...")
    # Nettoyer la colonne prix
    data['price'] = (
        data['price']
        .str.replace(r'[^\d.]', '', regex=True)  # Supprimer tout sauf chiffres et points
        .astype(float)  # Convertir en float
    )
    # Nettoyer et standardiser la colonne titre
    data['title'] = data['title'].str.lower().str.strip()
    # Remplacer les valeurs manquantes
    data.fillna({"title": "unknown", "price": 0.0, "reference": "N/A"}, inplace=True)
    print(f"[INFO] Nettoyage terminé pour {site_name}.")
    return data

# Appliquer le nettoyage aux deux ensembles de données
mytek_phone_data = clean_data(mytek_phone_data, "MyTek")


# Afficher un échantillon des données nettoyées
print("[MyTek Phone Data Sample]")
print(mytek_phone_data.head())


# Exporter les données nettoyées
mytek_phone_data.to_csv("cleaned_mytek_phones.csv", index=False)


print("[INFO] Données nettoyées exportées avec succès.")


# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client["mytek_database"]
collection = db["cleaned_phones"]  # Collection pour les données nettoyées

# Insérer les données nettoyées dans MongoDB
cleaned_phone_data = mytek_phone_data.to_dict('records')  # Convertir DataFrame en liste de dictionnaires
collection.insert_many(cleaned_phone_data)

print("[INFO] Données nettoyées insérées dans MongoDB avec succès.")
