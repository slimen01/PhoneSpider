from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client["mytek_database"]
collection = db["cleaned_phones"]

@app.route("/", methods=["GET", "POST"])
def index():
    query = request.args.get("query")  # Récupérer le paramètre de la requête
    phones = []

    if query:
        # Recherche dans MongoDB avec la requête de l'utilisateur
        phones = list(collection.find({
            "$text": {"$search": query}  # Recherche de texte dans MongoDB
        }))
    else:
        # Afficher tous les téléphones si aucune recherche
        phones = list(collection.find())

    return render_template("index.html", phones=phones)

if __name__ == "__main__":
    app.run(debug=True)
