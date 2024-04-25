# US_skrypty
Skrypty pomocne do obsługi Elektronicznego Zarządzania Dokumentacją (EZD)

Krótka instrukcja jak zainstalować pythona i biblioteki oraz skorzystać i ztweakować skrypty.

Funkcje:

    # Funkcje czyszczącę pobrane poliki CSV z bazy danych "Polon"
    i przygotowujące plik CSV z danymi gotowy do importu do bazy
    danych przez system EZD.
    - csv_uczelni()
    - csv_filie()
    - csv_uczelnie_niepubliczne()


    # Prosta funkcja podmieniająca separator w CSV tak aby
    plik pobrany z Scopus mógłbyć zaimportowany do Excela.
    - scopus_csv()

    # Funkcja czyszcząca wyeksportowany plik CSV z Excela tak
    aby spełnić warunki importu do systemu EZD do wysyłki seryjnej korespondencji.
    - listy_seryjne()


    # Funkcja zliczająca pdfy i docx w foloderach, oraz ilość stron aby umożliwić
    weryfikację wysłanej poczty przez kancelarię z fakturą z Poczty Polskiej.
    - pdf_docx_counter()
    <img width="1317" alt="Zrzut ekranu 2024-04-25 o 13 25 02" src="https://github.com/dziadekGIT/US_skrypty/assets/53622677/696c716c-f022-4ce3-a84c-f7c317c74fe5">
    
    # Webscrapping i wyszukiwanie słowa "kierownik" na stronie www.
    Nie pamiętam po co taki cyrk, ale może się przydać jako podgląd webscrappingu 
    z biblioteką beautifull soup.
    - kierownik()
    - webscrap()


