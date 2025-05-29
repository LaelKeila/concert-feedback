from flask import Flask, render_template, request
import csv
import json
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Configuration Google Sheets
SPREADSHEET_ID = "125j7an51V7_3E-Mx-gjUXSyo3nJ06VOl_JGgMMHhvvY"
SHEET_NAME = "Feuille 1"

# Authentification avec credentials.json stocké dans /etc/secrets/
credentials_path = '/etc/secrets/credentials.json'
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulaire')
def formulaire():
    anonyme = request.args.get('anonyme')
    return render_template('formulaire.html', anonyme=anonyme)

@app.route('/merci', methods=['POST'])
def merci():
    nom = request.form.get('nom', 'Anonyme')
    telephone = request.form.get('telephone', 'Anonyme')
    note = request.form['note']
    temoignage = request.form.get('temoignage', '')
    recommandations = request.form.get('recommandations', '')
    date_heure = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Sauvegarde locale CSV
    dossier_data = os.path.join('data')
    os.makedirs(dossier_data, exist_ok=True)
    csv_path = os.path.join(dossier_data, 'retours_experience.csv')
    write_header = not os.path.exists(csv_path)
    with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if write_header:
            writer.writerow(['Nom', 'Téléphone', 'Note', 'Témoignage', 'Recommandations', 'Date'])
        writer.writerow([nom, telephone, note, temoignage, recommandations, date_heure])

    # Sauvegarde locale JSON
    json_path = os.path.join(dossier_data, 'retours_experience.json')
    new_entry = {
        "nom": nom,
        "telephone": telephone,
        "note": note,
        "temoignage": temoignage,
        "recommandations": recommandations,
        "date": date_heure
    }

    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
    else:
        data = []

    data.append(new_entry)

    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

    # Ajout dans Google Sheet
    try:
        sheet.append_row([nom, telephone, note, temoignage, recommandations, date_heure])
    except Exception as e:
        print("Erreur lors de l'ajout dans Google Sheets :", e)

    return render_template('remerciement.html')

if __name__ == '__main__':
    app.run(debug=True)
