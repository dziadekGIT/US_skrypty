"""
UŚ - skrypty dla pracowników działu IT

1. Zainstaluj pythona.
2. W terminalu instalujesz biblioteki które skrypciki wymagają komendą "pip install", np "pip install pandas"
3. Tweakujesz sobie wedle uznania skrypty i odpalasz z maina odkomentowując odpowiedni 
"""

# import this
import pandas as pd  #pandas to fajna biblioteka do pracy nad DataFrame - taki rodzaj tablic
import re #obsługa regexów -> polecam regex 101 do sprawdzania jak działają <-
import os 
from PyPDF2 import PdfReader #biblioteka do obsługi pdfów
from docx import Document   #biblioteka do obsługi wordów
import warnings
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin


# ------------------- Globalne ściezki -------------------


# Tutaj sobie konfigurujesz ściezki do plików
uczelnie = "/Users/epizode/Desktop/US_Projects/Uczelnie/UCZELNIE.csv"
uczelnie_filie = "/Users/epizode/Desktop/US_Projects/Uczelnie/UCZELNIE_FILIE.csv"
uczelnie_niepubliczne = "/Users/epizode/Desktop/US_Projects/Uczelnie/UCZELNIE_NP.csv"
path_to_template = '/Users/epizode/Desktop/US_Projects/Bazy teleadresowe(Uczelnie).csv'

# ------------------- Skrypty -------------------

warnings.filterwarnings('ignore')

def csv_uczelni(): 
    """
    Zamiana i przygotowanie CSV danych Uczelni Wyzszych z bazy danych "Polon"
    do importu w systemie EZD Uniwersytetu.
    """
    df = pd.read_csv(uczelnie) #czyta CSV i tworzy DataFrame
    df_unique = df.drop_duplicates(subset="Nazwa instytucji", keep='first') #dropuje duplikaty
    columns_to_drop = [1, 3, 4, 5, 6, 7, 8, 9, 11, 14, 15, 16, 17, 28, 29] + list(range(30, 60)) + [61, 62, 63] #lista niepotrzebnych kolumn do dropa
    columns_to_drop = [i for i in columns_to_drop if i < len(df_unique.columns)] 
    df_unique = df_unique.drop(df_unique.columns[columns_to_drop], axis=1) #dropy
    df_unique = df_unique.drop('Strona www', axis=1)
    df_unique = df_unique.drop('Telefon', axis=1)
    df_unique = df_unique.drop('Województwo', axis=1)
    df_unique['REGON'] = df_unique['REGON'].fillna(0).map(lambda x: int(x)) #zamiana pustych w pisów na 0 i parsowanie do inta
    df_unique['NIP'] = df_unique['NIP'].fillna(0).map(lambda x: int(x))


    #Przypisanie nazw odpowiednio do nazw bazy danych uczelni
    df_unique = df_unique.rename(columns= {'Nazwa instytucji':'Nazwa', 'Adres e-mail':'AdresEmail','Adres skrzynki podawczej' : 'AdresOdpowiedziEpuap',
                                        'Adres - ulica':'Ulica', 'Adres - numer':'NumerBudynku', 'Adres - kod pocztowy':'KodPocztowy','Typ uczelni':'Typ' , 'Adres - miasto':'Miejscowosc' })

    #zaczytanie template z bazy danych uczelni
    df_template = pd.read_csv(path_to_template, sep=";")
    columns_to_copy = ['Nazwa','REGON','NIP','AdresEmail','AdresOdpowiedziEpuap','Kraj','Ulica','NumerBudynku','KodPocztowy','Typ', 'Miejscowosc']
    
    #skopiowanie wartości w templejtkę
    for i in columns_to_copy:
        df_template[i]=df_unique[i].copy()

    #kopia adresów epuap 
    df_template['IdentyfikatorEpuap'] = df_template['AdresOdpowiedziEpuap'].copy()
    df_template.to_csv("/Users/epizode/Desktop/US_Projects/Uczelnie/baza_teleatresowa_uczelnie.csv", index = False, encoding="utf-8")

def csv_filie():
    """
    Zamiana i przygotowanie CSV danych Filii Uczelni Wyzszych z bazy danych "Polon"
    do importu w systemie EZD Uniwersytetu.
    """
    df_unique = pd.read_csv(uczelnie_filie)
    # df_unique = df.drop_duplicates(subset="Nazwa filii", keep='first')

    columns_to_drop = [1, 3, 5, 6, 7, 8, 11, 12, 14, 22, 23, 24 ,25, 26, 27]
    df_unique = df_unique.drop(df_unique.columns[columns_to_drop], axis=1)
    df_unique['REGON'] = df_unique['REGON'].fillna(0).map(lambda x: int(x))
    df_unique['NIP'] = df_unique['NIP'].fillna(0).map(lambda x: int(x))

    df_unique = df_unique.rename(columns= {'Nazwa filii':'Nazwa', 'Adres e-mail':'AdresEmail','Adres skrzynki podawczej' : 'AdresOdpowiedziEpuap',
                                        'Adres - ulica':'Ulica', 'Adres - numer':'NumerBudynku', 'Adres - kod pocztowy':'KodPocztowy' , 'Adres - miasto':'Miejscowosc', 'Nazwa instytucji głównej':'Nazwisko' })

    # print(df_unique['Nazwisko'][0])

    # przypisałem do kolumny 'Nazwisko' nazwy uczelni, jest niekonsekwencja w bazie danych POLON,
    # dlatego sprawdzam czy nazwa uczelni zawiera się w nazwie filli, jezeli tak to usuwam, bo potem bede te kolumny scalał
    for i in df_unique['Nazwisko'].index:
        pattern = df_unique.loc[i, 'Nazwisko']
        if pattern in df_unique.loc[i,'Nazwa']:
            df_unique.loc[i, 'Nazwa'] = df_unique.loc[i, 'Nazwa'].replace(pattern, "")

    #tutaj regexem usuwam śmieci po skasowaniu nazwy uczelni przed słowem "Filia"
    for i in df_unique.index:
        text = df_unique.loc[i, 'Nazwa']
        if re.search(r'^.{0,10}Filia', text):
            df_unique.loc[i, 'Nazwa'] = re.sub(r'^.*?(Filia.*)', r'\1', text)
        else:
            df_unique.loc[i, 'Nazwa'] = text
    #tutaj regexem usuwam śmieci po skasowaniu nazwy uczelni przed słowem "filia"
    for i in df_unique.index:
        text = df_unique.loc[i, 'Nazwa']
        if re.search(r'^.{0,10}filia', text):
            df_unique.loc[i, 'Nazwa'] = re.sub(r'^.*?(filia.*)', r'\1', text)
        else:
            df_unique.loc[i, 'Nazwa'] = text
    #to jest taki myk zeby pierwsza litere w stringu zrobic duzą.
    for i in df_unique['Nazwa'].index:
        text = df_unique.loc[i, 'Nazwa'] 
        parts = text.split(maxsplit=1)  
        if parts:  
            first_word = parts[0].capitalize()  # Zmienia pierwszą literę pierwszego słowa na wielką
            if len(parts) > 1:
                df_unique.loc[i, 'Nazwa']  = first_word + ' ' + parts[1]  
            else:
                df_unique.loc[i, 'Nazwa']  = first_word  
        else:
            df_unique.loc[i, 'Nazwa']  = text  
    
    #tutaj łączysz nazwę filii zawartą w "Nazwa" i łączysz z nazwą uczelni przypisaną do kolumny "Nazwisko" w kolumnie "Nazwa"
    df_unique['Nazwa'] = df_unique['Nazwisko'] + ". " + df_unique['Nazwa']
    df_template = pd.read_csv(path_to_template, sep=";")
    columns_to_copy = ['Nazwisko','Nazwa','REGON','NIP','AdresEmail','AdresOdpowiedziEpuap','Kraj','Ulica','NumerBudynku','KodPocztowy', 'Miejscowosc']
   
    for i in columns_to_copy:
        df_template[i]=df_unique[i].copy()
    df_template['IdentyfikatorEpuap'] = df_template['AdresOdpowiedziEpuap'].copy()
    df_template.to_csv("/Users/epizode/Desktop/US_Projects/Uczelnie/baza_teleatresowa_uczelnie_filie.csv", index = False, encoding="utf-8")

def csv_uczelnie_niepubliczne():
    """
    Zamiana i przygotowanie CSV danych Filii Uczelni Wyzszych z bazy danych "Polon"
    do importu w systemie EZD Uniwersytetu.
    """

    df = pd.read_csv(uczelnie_niepubliczne)

    # Dropujesz duplikaty, oni mieli w bazie przy kazdej zmianie ewidencji nowy rejestr
    df_unique = df.drop_duplicates(subset="Nazwa uczelni", keep='first').copy()

    # Tutaj na parsujesz na stringa bo jest jakaś kaszana w regonie, spacje i inne śmieci
    df_unique['REGON'] = df_unique['REGON'].astype(str).str.strip()
    df_unique['REGON'] = df_unique['REGON'].str.replace('-', '')
    df_unique['REGON'] = df_unique['REGON'].str.replace('(', '')
    df_unique['REGON'] = df_unique['REGON'].str.replace(')', '')

    # Drop pustych i zamiana na 0. Parsujesz tutaj na inta bo nie chcemy mieć w regonie liczby zmiennoprzecikowej.
    df_unique['REGON'] = df_unique['REGON'].replace('nan', 0).astype(float).astype(int)

    df_unique.to_csv("/Users/epizode/Desktop/US_Projects/Uczelnie/baza_teleatresowa_uczelnie_nipubliczne2.csv", index = False, encoding="utf-8")

def scopus_csv():
    """
    Prościutka zamiana separatorów na ";" - bezpośrednio ze Scopusa źle się wczytuje do Excela
    """
    path = '/Users/epizode/Downloads/scopus.csv'
    df = pd.read_csv(path)
    df.to_csv('/Users/epizode/Downloads/scopus_test.csv', sep=";")

def listy_seryjne():
    """
    Czyszczenie dostarczonych plików pod wysyłkę seryjną w systemie EZD
    """
    #ściezka csv
    path = "/Users/epizode/Documents/certyfikaty_luty_2024.csv"
    #excel jako separator bierze ; więc tak importuje
    df = pd.read_csv(path, sep=';')

    #usuwam białe znaki prostą funkcją anonimową która sprawdza ze jezeli element to string to stripuje.
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    #zamieniem NaN na 0
    df['NR LOKALU'] = df['NR LOKALU'].fillna(0)
    #parsuje do inta
    df['NR LOKALU'] = df['NR LOKALU'].astype('int64')
    #zamieniam tez pandasowe NaN na 0
    df['NR LOKALU'] = df['NR LOKALU'].replace(0, pd.NA, inplace= False)
    
    #upewniam się ze nazwy wlasne są z duzej litery
    df['IMIE'] = df['IMIE'].map(lambda x : x.title())
    df['NAZWISKO'] = df['NAZWISKO'].map(lambda x : x.title())
    df['MIASTO'] = df['MIASTO'].map(lambda x : x.title())
    df['ULICA'] = df['ULICA'].map(lambda x : x.title())

    #sprawdzenie czy nie ma kaszany 
    print(df.head)

    #ściezka zapisu
    # df.to_csv("/Users/epizode/Documents/certyfikaty_luty_2024_poprawione.csv", index = False, encoding="utf-8", sep=";")

def pdf_docx_counter():
    """
    Zlicza ilość stron i plików w katalogach.
    """
    path = "/Users/epizode/Desktop/US_e_listy/"
    records = []

    #os.walk łazi ci po katalogach z path
    for root, dirs, files in os.walk(path):
        #to ci łazi po poszczególnych plikach
        for file in files:
            full_path = os.path.join(root, file)
            #.. i tu wchodzi jak wyłazony plik to pdf 
            if file.endswith(".pdf"):
                try:
                    #zaczytuje pdfy
                    pdf = PdfReader(open(full_path, 'rb'))
                    #appenduje do recordsów dane
                    records.append([file, full_path, len(pdf.pages)])
                except Exception as e:
                
                    print(f"Error : {full_path}: {str(e)}")
                    
            #.... a tu jak docx        
            elif file.endswith(".docx"):
                try:
                    doc = Document(full_path)
                    # Nie ma mozliwosci za bardzo zczytania ilosci stron z docx, bo kazdy program inaczej troche
                    # formatuje, tutaj jest aproksymacja ilosci stron <- rowiazanie z czata gpt
                    paragraphs = [p for p in doc.paragraphs if p.text.strip()]
                    page_count = len(paragraphs) // 20  # zakłada 20 paragrafów na stronę
                    records.append([file, full_path, page_count])
                except Exception as e:
                    print(f"Error :  {full_path}: {str(e)}")
                    
    df = pd.DataFrame(records, columns=['nazwaPliku', 'lokacjaPliku', 'ilośćStron'])
    print(df)


def kierownik():
    """
    Webscrap strony UŚ i wyszukanie słowa "kierownik" z wskazaniem adresu.
    """
    # url = 'https://ab.us.edu.pl/unit/6061'
    url = 'https://us.edu.pl'

    with requests.Session() as session:
        headers = {
            'Content-Type': 'text/html; charset=utf-8',
        }
        response = session.get(url, headers=headers, verify=False)

        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                sub_url = link['href']
                if sub_url.startswith('http://') or sub_url.startswith('https://'):
                    full_url = urljoin(url, sub_url)
                else:
                    continue

                sub_response = session.get(sub_url)
                if sub_response.ok:
                    sub_soup = BeautifulSoup(sub_response.text, 'html.parser')
                    
                    if 'kierownik' in sub_soup.text.lower():
                        print(f'Wyraz "kierownik" znaleziony na stronie: {sub_url}')
                
                        # print(sub_soup.prettify())
                    else:
                        print(f'nie')
        else:
            print(f'Nie udało się pobrać strony: {url}')

def webscrap():
    """
    printuje strukturę htmla strony
    """
    url = 'https://ab.us.edu.pl/unit/6061'
    page = requests.get(url, verify=False)
    print(page.text)



# ------------------- main -------------------


if __name__ == "__main__":
    # csv_uczelni()
    # csv_filie()
    # csv_uczelnie_niepubliczne()
    # scopus_csv()
    # listy_seryjne()
    # pdf_docx_counter()
    # kierownik()
    webscrap()



