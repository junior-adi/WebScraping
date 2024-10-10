import requests
import re
import json
import csv
import os
from bs4 import BeautifulSoup

# Constantes
BASE_URL = "https://football-data.co.uk/"
NOTES_URL = "https://www.football-data.co.uk/notes.txt"

def fetch_html(url):
    """Récupère et retourne le contenu HTML d'une URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération de {url}: {e}")
        return None

def get_csv_links(url):
    """Récupère tous les liens CSV présents sur une page donnée."""
    response = fetch_html(url)
    if not response:
        return []

    soup = BeautifulSoup(response, 'html.parser')
    csv_links = [
        {
            "href": BASE_URL + img_link["href"],
            "text": img_link.get_text() or img.get("alt")
        }
        for img in soup.find_all('img')
        if (img_link := img.find_next_sibling('a')) and img_link.get('href', '').endswith('.csv')
    ]
    return csv_links

def split_link(link, separator='/'):
    """Divise un lien en ses composants et retourne les composants non vides."""
    return [component for component in link.split(separator) if component]

def transform_to_years(years):
    """Transforme une chaîne de 4 chiffres en format d'année 'YYYY/YYYY'."""
    years_str = str(years)
    if len(years_str) != 4:
        return None
    
    start_year = int(years_str[:2])
    end_year = int(years_str[2:])
    
    if start_year >= 70 or end_year >= 70:
        start_year += 1900
    else:
        start_year += 2000
    end_year = start_year + 1
    
    return f"{start_year}/{end_year}"

def seasonify_from(csv_link):
    """Extrait et retourne la saison formatée à partir du lien CSV."""
    return transform_to_years(split_link(csv_link)[-2])

def get_csv_pages_links(base_url):
    """Récupère et retourne tous les liens vers les pages de téléchargement de CSV."""
    response = fetch_html(base_url)
    if not response:
        return {}

    soup = BeautifulSoup(response, 'html.parser')
    links = [
        a_tag['href']
        for div in soup.find_all('div', class_="menus")
        if (a_tag := div.find('a')) and a_tag.has_attr('href')
    ]

    regex = re.compile(r'^https://www\.football-data\.co\.uk\/(?!data|books|links|matches|downloadm)\w+\.php$')
    return {link: link.split('/')[-1].split('.')[0] for link in links if regex.match(link)}

def process_weblink(football_data_co_uk_link):
    """Traite les liens et construit la structure des données."""
    all_links_dict = get_csv_pages_links(football_data_co_uk_link)
    football_data = {}

    for link, country_name in all_links_dict.items():
        csv_links_list = get_csv_links(link)
        for entry in csv_links_list:
            csv_link = entry['href']
            season = seasonify_from(csv_link)
            season_formatted = f"Season {season}" if season else "Unknown Season"

            if country_name not in football_data:
                football_data[country_name] = {}

            if season_formatted not in football_data[country_name]:
                football_data[country_name][season_formatted] = []
            
            final_csv_file_name = f"{country_name}_{entry['text'].replace(' ', '_')}_{season.replace('/', '-')}.csv"
            football_data[country_name][season_formatted].append([final_csv_file_name, csv_link])

    return football_data

def save_data_in_file(output_folder, data_structure, filetype='json'):
    """Sauvegarde la structure de données dans un fichier du type spécifié."""
    if filetype not in ['json', 'csv', 'txt']:
        print("Type de fichier invalide. Utilisez 'json', 'csv', ou 'txt'.")
        return

    output_file = os.path.join(output_folder, f'data_structure.{filetype}')

    if filetype == 'json':
        with open(output_file, 'w') as json_file:
            json.dump(data_structure, json_file, indent=4)
    elif filetype == 'csv':
        with open(output_file, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for country, seasons in data_structure.items():
                for season, csv_files in seasons.items():
                    for csv_file in csv_files:
                        csv_writer.writerow([country, season] + csv_file)
    elif filetype == 'txt':
        with open(output_file, 'w') as txt_file:
            for country, seasons in data_structure.items():
                txt_file.write(f"{country}:\n")
                for season, csv_files in seasons.items():
                    txt_file.write(f"  {season}:\n")
                    for csv_file in csv_files:
                        txt_file.write(f"    {', '.join(csv_file)}\n")

    print(f"Structure de données sauvegardée dans {output_file}")

def download_csv_files(data_structure, output_folder):
    """Télécharge les fichiers CSV en fonction de la structure de données."""
    download_notes_file()
    for country, seasons in data_structure.items():
        for season, csv_files in seasons.items():
            for file_name, file_url in csv_files:
                output_path = os.path.join(output_folder, country, season.replace('/', '_'), file_name)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                response = requests.get(file_url)
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Téléchargé : {output_path}")
                else:
                    print(f"Échec du téléchargement : {file_name}")

def download_notes_file():
    """Télécharge le fichier notes.txt qui explique les données CSV."""
    response = requests.get(NOTES_URL)
    if response.status_code == 200:
        with open("notes.txt", 'wb') as f:
            f.write(response.content)
        print("Téléchargé : notes.txt")
    else:
        print("Échec du téléchargement : notes.txt")

def run():
    """Fonction principale pour l'exécution du script."""
    output_folder = "./output"
    os.makedirs(output_folder, exist_ok=True)

    mandatory_base_url = "https://football-data.co.uk/data.php"
    structured_data = process_weblink(mandatory_base_url)
    
    save_data_in_file(output_folder, structured_data, filetype='json')
    download_csv_files(structured_data, output_folder)

if __name__ == "__main__":
    run()
