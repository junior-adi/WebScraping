import requests
import re
import json
import csv
import os
from bs4 import BeautifulSoup

def get_csv_links(url):
    base_url = "https://football-data.co.uk/"
    response = requests.get(url).content
    soup = BeautifulSoup(response, 'html.parser')
    csv_links = []

    for img in soup.find_all('img'):
        img_link = img.find_next_sibling('a')
        if img_link and img_link.get('href', '').endswith('.csv'):
            csv_links.append({
                "href": base_url + img_link["href"],
                "text": img_link.get_text() or img.get("alt"),
            })

    return csv_links

def split_link(link, separator='/'):
    path_components = link.split(separator)
    path_components = [component for component in path_components if component]
    return path_components

def transform_to_years(years):
    years_str = str(years)
    if len(years_str) == 4:
        start_year = int(years_str[:2])
        end_year = int(years_str[2:])

        if start_year >=70 or end_year >=70:
            start_year = 1900 + start_year
            end_year = start_year + 1
            return f"{start_year}/{end_year}"
        else:
            start_year = 2000 + start_year
            end_year = start_year + 1
            return f"{start_year}/{end_year}"
    else:
        return

def seasonify_from(csv_link):
    return transform_to_years(split_link(csv_link)[-2])

def get_all_csvlinks_webpages_as_dictionnary(base_url):
    html_content = requests.get(base_url).content
    soup = BeautifulSoup(html_content, 'html.parser')
    table_body = soup.find_all('div', class_="menus")
    links = []
    links_dict = {}

    for div in table_body:
        a_tag = div.find('a')
        if a_tag and a_tag.has_attr('href'):
            a_tag_link = a_tag['href']
            links.append(a_tag_link)

    regex = re.compile(r'^https://www\.football-data\.co\.uk\/(?!data\.php|books\.php|links\.php|matches\.php|downloadm\.php)([a-z]{1,12})\.php$')

    for link in links:
        match = regex.match(link)

        if match:
            country_name = match.group(1).rstrip("m")
            links_dict[link] = country_name

    return links_dict

def process_weblink(football_data_co_uk_link):
    all_links_dict = get_all_csvlinks_webpages_as_dictionnary(football_data_co_uk_link)
    football_data = {}

    for link, country_name in all_links_dict.items():
        csv_links_list_dict = get_csv_links(link)

        for entry in csv_links_list_dict:
            link = entry['href']
            text = entry['text']
            season = seasonify_from(link)
            season_formatted = f"Season {season}"

            if country_name not in football_data:
                football_data[country_name] = {}

            if season_formatted not in football_data[country_name]:
                football_data[country_name][season_formatted] = []
            
            final_csv_file_name = [country_name + "_" + text.replace(' ', '_') + "_"+ season.replace('/', '-') + '.csv', link]
            football_data[country_name][season_formatted].append(final_csv_file_name)

    return football_data

def save_data_in_file(output_folder, data_structure, filetype='json'):
    if filetype not in ['json', 'csv', 'txt']:
        print("Invalid file type. Supported types are 'json', 'csv', and 'txt'.")
        return

    output_file = os.path.join(output_folder, f'data_structure.{filetype}')

    if filetype == 'json':
        with open(output_file, 'w') as json_file:
            json.dump(data_structure, json_file, indent=4)
        print(f"Data structure saved to {output_file}")

    elif filetype == 'csv':
        with open(output_file, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for country, seasons in data_structure.items():
                for season, csv_files in seasons.items():
                    for csv_file in csv_files:
                        csv_writer.writerow([country, season] + csv_file)
        print(f"Data structure saved to {output_file}")

    elif filetype == 'txt':
        with open(output_file, 'w') as txt_file:
            for country, seasons in data_structure.items():
                txt_file.write(f"{country}:\n")
                for season, csv_files in seasons.items():
                    txt_file.write(f"  {season}:\n")
                    for csv_file in csv_files:
                        txt_file.write(f"    {', '.join(csv_file)}\n")
        print(f"Data structure saved to {output_file}")

def print_data_structure(data_structure):
    for country, seasons in data_structure.items():
        print(f"Country: {country}")
        for season, csv_files in seasons.items():
            print(f"  Season: {season}")
            for csv_file in csv_files:
                file_name, file_url = csv_file
                print(f"    {file_name}: {file_url}")

def download_csv_files(data_structure, output_folder):
    download_notes_file()
    for country, seasons in data_structure.items():
        for season, csv_files in seasons.items():
            for csv_file in csv_files:
                file_name, file_url = csv_file
                output_path = os.path.join(output_folder, country, season, file_name)

                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                response = requests.get(file_url)
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {file_name}")
                else:
                    print(f"Failed to download: {file_name}")

def download_csv_files_by_country_and_season(data_structure, output_folder):
    for country, seasons in data_structure.items():
        for season, csv_files in seasons.items():
            season_folder = os.path.join(output_folder, country, season.replace('/', '_'))
            os.makedirs(season_folder, exist_ok=True)

            for csv_file in csv_files:
                file_name, file_url = csv_file
                output_path = os.path.join(season_folder, file_name)

                response = requests.get(file_url)
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {country}/{season}/{file_name}")
                else:
                    print(f"Failed to download: {country}/{season}/{file_name}")

def download_notes_file():
    response = requests.get("https://www.football-data.co.uk/notes.txt")
    if response.status_code == 200:
        with open(".", 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: Notes.txt (text file key to the data files and data source acknowledgements)")
    else:
        print(f"Failed to download: Notes.txt (text file key to the data files and data source acknowledgements)")

def run():
    # CHANGES NEEDED HERE !
    # Please change these variables values before executing the run() function !
    output_folder = "."

    # DON'T TOUCH ANYTHING HERE
    mandatory_base_url = "https://football-data.co.uk/data.php"
    structured_data = process_weblink(mandatory_base_url)
    #print_data_structure(structured_data)
    save_data_in_file(output_folder, structured_data, filetype='json')
    download_csv_files_by_country_and_season(structured_data, output_folder)

if __name__ == "__main__":

    """
    The refactoring and clean code for creating main.py
    Actually, the script will :
      - web scrape the website "https://football-data.co.uk/data.php"
      - store data into a data structure named "data_structure" or what you want
      - save all downloaded files by country and season
      - download the description file which describes and explain the data and variable names
        stored at "https://www.football-data.co.uk/notes.txt"

      Enjoy !

    """
    run()
