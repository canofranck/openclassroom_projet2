import requests
from bs4 import BeautifulSoup
import csv #gestion des fichier csv
import os  # gere les operations sur fichier et repertoire


# Créer un dictionnaire de correspondance chiffre en lettre , en chiffre
chiffre_en_lettre = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5
}
product_page_url="http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
response=requests.get(product_page_url)
if response.ok:
    soup=BeautifulSoup(response.text,'html.parser')
    title=soup.find('title')
    page_title=title.text.strip()
    
    
    #trouver la description du produit
    description_div = soup.find('div', {'id': 'product_description'})
    description_paragraph = description_div.find_next('p')
    description = description_paragraph.text
         
    # Trouver la table contenant les informations du produit
    product_table = soup.find('table', {'class': 'table table-striped'})
    
    #trouver le review_rating
    review_rating = soup.find('p', class_='star-rating').get('class')[1]
    
    # Utiliser le dictionnaire pour obtenir le chiffre correspondant
    chiffre = chiffre_en_lettre.get(review_rating.lower())  # Utilisez .lower() pour être insensible à la casse

    if chiffre is not None:
     review_rating=chiffre
    else:
     review_rating=""
     
 # Trouvez la balise <ul> avec la classe 'breadcrumb'
    breadcrumb_ul = soup.find('ul', class_='breadcrumb')
    
    # Trouvez le dernier lien <a> à l'intérieur de la balise <ul>
    if breadcrumb_ul:
        category_link = breadcrumb_ul.find_all('a')[-1]
        
        # Extrait le texte du lien, qui représente la catégorie du livre
        category = category_link.text.strip()
 
    #trouvez l id product gallery
    product_gallery=soup.find('div',id='product_gallery')
    if product_gallery:
        image_src=product_gallery.find('img')
        image_url=image_src.get('src')
    
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
                    price_excl_tax = row.find('td').text.strip()
                    price_excl_tax =  price_excl_tax.replace("Â", "") #nettoie la chaine de caractere
                elif "Price (incl. tax)" in header_text:
                    price_incl_tax = row.find('td').text.strip()
                    price_incl_tax=price_incl_tax.replace("Â", "")
                elif "Availability" in header_text:
                    availability = row.find('td').text
                
        
        # Afficher les valeurs extraites
        """ print(f"Product_page_url : {product_page_url}")
        print(f"UPC: {upc}")
        print(f"titre du livre:  {page_title}")
        print(f"Price (incl. tax): {price_incl_tax}")
        print(f"Price (excl. tax): {price_excl_tax}")
        print(f"Number Available: {availability}")
        print(f"Description {description}")
        print(f"Catégorie du livre: {category}")
        print(f"Review Rating: {review_rating}")
        print(f"image_url : {image_url}") """

        
# Repertoire du fichier CSV
csv_file_path = 'data/data.csv'

# Vérifiez si le répertoire "data" existe, sinon, on le crée
data_directory = os.path.dirname(csv_file_path)
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

# Vérifiez si le fichier CSV existe, sinon, one le crée
if not os.path.exists(csv_file_path):
    # Si le fichier n'existe pas, création et écrire les données
    with open(csv_file_path, 'w', newline='') as csv_file:
        # definir objet writer CSV
        csv_writer = csv.writer(csv_file)

        # Écrire les en-têtes de colonnes
        csv_file.write("product_page_url,universal_product_code,title,price_including_tax,price_excluding_tax,number_available,product_description,category,review_rating,image_url: \n")

        # Écrire les données dans le fichier CSV

        csv_writer.writerow(
                    [product_page_url,upc,page_title,price_incl_tax,price_excl_tax,availability,description,category,review_rating,image_url])


    