import datetime
import requests
from bs4 import BeautifulSoup
from date_utils import today as todayDate

today= todayDate

class ReadHTMLParser:
    def __init__(self, tribunale, procedura, anno):
        self.file_name = f"{tribunale}_{procedura}_{anno}.html"

    def read_html(self):
        with open(f'output/{today}/{self.file_name}', 'r', encoding='utf-8') as file:
            html_content = file.read()
        return html_content
    
    def download_detail_html(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Failed to download detail HTML from {url}: {e}")
            return None
        
    def parse(self):
        html_content = self.read_html()
        soup = BeautifulSoup(html_content, 'html.parser')

        details_list = []
        for lotto in soup.find_all(class_='col-md-6 col-lg-4 col-sm-6 col-xs-12 tile-dettaglio'):
            address = lotto.find('div', class_='anagrafica-risultato').get_text().strip()
            nLotto = lotto.find(class_='black').get_text()

            data_vendita = lotto.find(class_='margin-top-15').find(class_='font-green').get_text()

            offerta_elements = lotto.find_all(class_='inline font-blue')
            offerta_minima = offerta_elements[0].get_text() 
            rialzo_minimo = offerta_elements[1].get_text()
            n_procedura = lotto.find(class_='font-black inline').get_text()
            prezzo_base = lotto.find(class_='margin-bottom-15').find(class_='font-blue font18').get_text()
            tipologia = ''

            if nLotto and "Lotto nr." in nLotto:
                nLotto = nLotto.replace("\n                ", "")

            
            detail_link = lotto.find('a')['href']
            detail_url = f"https://pvp.giustizia.it{detail_link}"
            detail_html = self.download_detail_html(detail_url)


            if detail_html:
                detail_soup = BeautifulSoup(detail_html, 'html.parser')

                tipologia_element = detail_soup.find('div', text='Tipologia')

                if tipologia_element:
                    tipologia = tipologia_element.find_next('div', class_='anagrafica-risultato').get_text(strip=True)



            details_dict = {
                'Address': address,
                'Lotto': nLotto.strip() if nLotto else '',
                'Data Vendita': data_vendita.strip() if data_vendita else '',
                'Offerta minima': offerta_minima.strip() if offerta_minima else '',
                'Rialzo minimo': rialzo_minimo.strip() if rialzo_minimo else '',
                'N° Procedura': n_procedura.strip() if n_procedura else '',
                "Prezzo base d'asta": prezzo_base.strip() if prezzo_base else '',
                'Tipologia': tipologia.strip() if tipologia else ''
            }
            details_list.append(details_dict)

        return details_list