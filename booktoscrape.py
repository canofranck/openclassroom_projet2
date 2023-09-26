# Importation des bibliothèques nécessaires
import re
import requests
from bs4 import BeautifulSoup
import csv
import os
import time

# Définition de la fonction pour nettoyer un nom de fichier
def nettoyer_nom_fichier(titre):
 # Remplacer tous les caractères non autorisés par des tirets
    titre_nettoye = re.sub('[^a-zA-Z0-9 \n]', '-', titre)
 # Limiter la longueur du nom de fichier à 255 caractères
    titre_nettoye = titre_nettoye[:255]
    return titre_nettoye

# Fonction pour extraire les catégories depuis la page d'accueil
def extract_categories(base_url):
    categories = []
    try:
        # Effectuer une requête HTTP pour récupérer la page d'accueil du site
        response = requests.get(base_url)
        response.raise_for_status()  # Lèvera une exception si la requête échoue
        if response.ok:
            # Analyser la page avec BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            categorie_ul = soup.find('ul', {"class": "nav-list"})
            # Trouver la section qui contient la liste des catégories
            ul = categorie_ul.find('ul')
            # Extraire la liste des catégories en parcourant les éléments de la liste
            liste_categorie = ul.find_all('li')
            for li in liste_categorie:
                lien_categorie = li.find('a')['href'].split('/')[3]
                text_categorie = lien_categorie.split("_")[0]
                categories.append(lien_categorie)
    except requests.exceptions.RequestException as e:
        print(f"Une erreur s'est produite lors de la requête HTTP : {e}")
        

    return categories

# Fonction pour extraire les liens des livres d'une catégorie donnée
def extract_books_in_category(category_url):
    books = []
    
    try:
        # Effectuer une requête HTTP pour récupérer la page de la catégorie
        response = requests.get(category_url)
        response.raise_for_status()  # Lèvera une exception si la requête échoue
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Trouver la pagination s'il y en a une
            page = (soup.find("li", {"class": "current"}))

            if page is None:
                titre_livre = soup.find_all('h3')
                for h3 in titre_livre:
                    lien_livres = h3.select('a')
                    for a in lien_livres:
                        lien_livre = a['href'].strip('../../../')
                        url_livre = 'https://books.toscrape.com/catalogue/' + lien_livre
                        books.append(url_livre)
            else:
                # S'il y a plusieurs pages, déterminez le nombre de pages et extrayez les liens des livres de chaque page
                page = str(page)
                page = page.split()[5]
                nombre_pages = int(page)
                
                for i in range(1, nombre_pages + 1):  # Commencez à partir de 1 au lieu de 0
                    url = category_url.replace('index.html', '')
                    url = url + "page-" + str(i) + ".html"
                    response = requests.get(url)
                    response.raise_for_status()  # Lèvera une exception si la requête échoue
                    if response.ok:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        titre_livre = soup.find_all('h3')
                        for h3 in titre_livre:
                            lien_livres = h3.select('a')
                            for a in lien_livres:
                                lien_livre = a['href'].strip('../../../')
                                url_livre = 'https://books.toscrape.com/catalogue/' + lien_livre
                                books.append(url_livre)
    except requests.exceptions.RequestException as e:
        print(f"Une erreur s'est produite lors de la requête HTTP : {e}")
       

    return books

# Fonction pour extraire les données d'un livre à partir de son URL 
def extract_book_data(book_url):
    book_data = {}
    try:
        # Effectuer une requête HTTP pour récupérer la page du livre
        response = requests.get(book_url)
        response.raise_for_status()  # Lèvera une exception si la requête échoue
        if response.ok:
            # Analyser la page avec BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            # Trouver le titre du livre dans la balise <title>
            title = soup.find('title')
            page_title = title.text.split(' | ')[0].strip()
            # Trouver la description du produit
            description_div = soup.find('div', {'id': 'product_description'})
            if description_div is None:
                description = ""
            else:
                description_paragraph = description_div.find_next('p')
                description = description_paragraph.text

            # Trouver la table contenant les informations du produit
            product_table = soup.find('table', {'class': 'table table-striped'})

            # Trouver le review_rating
            review_rating = soup.find('p', class_='star-rating').get('class')[1]

            # Trouver la balise <ul> avec la classe 'breadcrumb'
            breadcrumb_ul = soup.find('ul', class_='breadcrumb')

            # Trouver le dernier lien <a> à l'intérieur de la balise <ul>
            if breadcrumb_ul:
                category_link = breadcrumb_ul.find_all('a')[-1]

                # Extrait le texte du lien, qui représente la catégorie du livre
                category = category_link.text.strip()

            # Trouver l'id product gallery
            product_gallery = soup.find('div', id='product_gallery')
            if product_gallery:
                image_src = product_gallery.find('img')
                image_url = image_src.get('src')

            if product_table:
                # Initialiser des variables pour stocker les valeurs des balises <th>
                upc = None
                product_type = None
                price_excl_tax = None
                price_incl_tax = None
                availability = None

                # Chercher toutes les lignes (balise <tr>) dans la table
                rows = product_table.find_all('tr')

                for row in rows:
                    # Chercher toutes les cellules d'en-tête (balise <th>) dans la ligne
                    header_cells = row.find_all('th')
                    if len(header_cells) == 1:
                        # Extraire le texte de la première cellule d'en-tête et le stocker dans la variable correspondante
                        header_text = header_cells[0].text
                        if "UPC" in header_text:
                            upc = row.find('td').text
                        elif "Price (excl. tax)" in header_text:
                            price_excl_tax = row.find('td').text

                        elif "Price (incl. tax)" in header_text:
                            price_incl_tax = row.find('td').text

                        elif "Availability" in header_text:
                            availability = row.find('td').text
        # Appeler la fonction de nettoyage pour préparer les données                                           
        book_data=clean_data(book_url, upc, page_title, price_incl_tax, price_excl_tax, availability, description,category,
            review_rating, image_url)
      
    except requests.exceptions.RequestException as e:
        print(f"Une erreur s'est produite lors de la requête HTTP : {e}")
        
    return book_data

def clean_data(book_url, upc, page_title, price_incl_tax, price_excl_tax, availability, description,category,
            review_rating, image_url):
    # Créer un dictionnaire de correspondance chiffre en lettre , en chiffre
    chiffre_en_lettre = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5}
    # Nettoyer le titre
    page_title = nettoyer_nom_fichier(page_title)


    # Convertir la notation de la note en chiffre si elle est en texte
    chiffre = chiffre_en_lettre.get(review_rating.lower())  # Utilisez .lower() pour être insensible à la casse

    if chiffre is not None:
        review_rating = chiffre
    else:
        review_rating= ""
    # Extraire le nom du fichier image à partir de son URL
    nom_fichier_image = image_url.split('/')[-1]
    nettoi_url = image_url.replace("../../", "")
    chemin_image = "http://books.toscrape.com/" + nettoi_url
    image_url = chemin_image
    # Générer le nom final du fichier image en utilisant le titre nettoyé
    nom_fichier_image_final = page_title
    nom_fichier_image_final = nettoyer_nom_fichier(nom_fichier_image_final)
    nom_fichier_image_final = nom_fichier_image_final + ".jpg"
    
    
     # Utilisez une expression régulière pour rechercher un ou plusieurs chiffres dans la chaîne
    resultat = re.search(r'\d+', availability)
    # Vérifiez si un résultat a été trouvé
    if resultat:
         nombre_disponible = int(resultat.group())
    else:
        nombre_disponible = 0
    availability = nombre_disponible
    # Rassembler toutes les données nettoyées dans un tuple                     
    book_data = (
             book_url, upc, page_title, price_incl_tax, price_excl_tax, availability, description,category,
            review_rating, image_url, nom_fichier_image_final
     )  
    return book_data

# Fonction pour sauvegarder les données dans un fichier CSV
def save_data_to_csv( book_data):
    try:
     csv_file_path = os.path.join('data', f'data_{book_data[7]}.csv')
     # Vérifiez si le répertoire "data" existe, sinon, on le crée
     if not os.path.exists('data'):
        os.makedirs('data')

     # Vérifiez si le fichier CSV existe, sinon, créez-le
     if not os.path.exists(csv_file_path):
        # Si le fichier n'existe pas, création et écrire les données
        with open(csv_file_path, 'w', newline='', encoding="utf-8-sig") as csv_file:
            # Écrire les en-têtes de colonnes
            csv_file.write("product_page_url,universal_product_code,title,price_including_tax,price_excluding_tax,number_available,product_description,category,review_rating,image_url\n")

     # Répertoire pour les images
     if book_data[9]:  # Vérifiez si image_url n'est pas vide
        image_url = book_data[9]
        path = os.path.join('data', book_data[7])
        if not os.path.exists(path):
            os.makedirs(path)
        path_image = os.path.join(path, book_data[10])  # Utilisez l'indice 11 pour le nom du fichier image
        
        # Vérifiez si le fichier image existe déjà, si oui, ne le téléchargez pas à nouveau
        if not os.path.exists(path_image):
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(path_image, "wb") as file:
                 file.write(response.content)
            else:
                    print(f"Échec du téléchargement de l'image pour {book_data[2]}")
     # Ouvrez le fichier CSV en mode "a" pour ajouter des données
     with open(csv_file_path, 'a', newline='', encoding="utf-8-sig") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            book_data[0],  # product_page_url
            book_data[1],  # universal_product_code
            book_data[2],  # title
            book_data[3],  # price_including_tax
            book_data[4],  # price_excluding_tax
            book_data[5],  # number_available
            book_data[6],  # product_description
            book_data[7],  # category
            book_data[8],  # review_rating
            book_data[9],  # image_url
        ])
       # print(f"Données pour {book_data[2]} enregistrées dans {csv_file_path}")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la sauvegarde des données : {e}")
           
# Fonction principale pour exécuter l'ensemble du pipeline ETL
print("Début de l'extraction des catégories")
base_url = "http://books.toscrape.com/"
categories = extract_categories(base_url)
start_time = time.time()
for category in categories:
     
     category_url = base_url + "catalogue/category/books/" + category + "/index.html"
     books = extract_books_in_category(category_url)

     for book_url in books:
         book_data = extract_book_data(book_url)
         save_data_to_csv( book_data)
end_time = time.time()  # Enregistrez le temps à la fin de la boucle
elapsed_time = end_time - start_time  # Calculez le temps écoulé
print(f"Extraction et sauvegarde des données terminées en : {elapsed_time} secondes")

