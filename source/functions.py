import pandas as pd
import sys
import os
import json 
import time
import random
import shutil

from scrapy.crawler import CrawlerProcess, CrawlerRunner
from source.spiders.tribunals_dic import TribunaleSpider
from source.spiders.pvp_web_scraping import ProceduraSpider
from source.HTML_scraper import ReadHTMLParser
from source.HTML_Details_scraper import ReadDetailHTMLParser
from twisted.internet import reactor, threads, defer
from scrapy.utils.project import get_project_settings


'''
FUNCTION TO EXPORT A DATAFRAME TO EXCEL 
pd.DataFrame(parsed_data).to_excel('scraped_data.xlsx', index=False) #saves the output normally, without column width adjusted
The function below creates the file scraped_data.xlsx adjusting the columns width to their content
'''
def dicToExcel(output_path, dics_df):
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        dics_df.to_excel(writer, sheet_name='RisultatiTribunali', index=False)
        worksheet = writer.sheets['RisultatiTribunali']
        # Get the maximum length of data in each column
        for i, col in enumerate(dics_df.columns):
            max_len = max(dics_df[col].astype(str).apply(len).max(), len(col) + 2)
            worksheet.set_column(i, i, max_len)  # Set the column width


'''
FUNCTION TO READ A FILE 
This function takes a file path (like 'input/input.xlsx'), reads it, and puts its columns names in lowercase. 
'''
def input_read(path):
    inputs = pd.read_excel(path)
    inputs.columns = [col.lower() for col in inputs.columns]
    return inputs


'''
FUNCTION TO READ A DF 
This function takes a dataframe, reads it, and puts its columns names in lowercase. 
'''
def df_input_clean(inputs):
    # Lowercase and strip column names
    inputs.columns = [col.lower().strip() for col in inputs.columns]
    inputs = inputs.applymap(lambda x: str(x).strip())

    return inputs


'''
FUNCTION TO MAP THE COURTHOUSES ID'S TO THEIR NAME
This function checks if the file already exists, and creates it if it doesn't, calling the spider that scrapes the website to get the info.
'''
def read_or_create_tribunales(file_path):
    if not os.path.exists(file_path):
        process = CrawlerProcess()
        process.crawl(TribunaleSpider,file_path)
        process.start()
    with open(file_path, 'r') as file:
        return json.load(file)

''' FUNCTION THAT CONSIDERS USER MISTAKES WHEN INPUTING'''
def common_mistakes(name):
    mapping = {
        'tribunale di ariano irpino': 'tribunale di benevento ex tribunale di ariano irpino',
        'tribunale di macerata ex camerino': 'tribunale di macerata ex tribunale di camerino',
        'tribunale di aquila': "tribunale di l'aquila",
        'tribunale di napoli nord-aversa': 'tribunale di napoli nord',
        'tribunale di reggio nell\'emilia': 'tribunale di reggio emilia',
        'tribunale di reggio di calabria': 'tribunale di reggio calabria',
        'tribunale di forlì': 'tribunale di forli',
        'tribunale di forli\'- cesena': 'tribunale di forli',
        'tribunale di monza brianza': 'tribunale di monza',
        'tribunale di barletta-andria-trani': 'tribunale di trani',
        "tribunale di sant'angelo dei lombardi": "tribunale di avellino ex tribunale di sant'angelo dei lombardi",
        "tribunale di melfi": "tribunale di potenza ex tribunale di melfi",
        "tribunale di sala consilina": "tribunale di lagonegro ex tribunale di sala consilina",
        "tribunale di mistretta": "tribunale di patti ex tribunale di mistretta",
        "tribunale di vigevano": "tribunale di pavia ex tribunale di vigevano"
        # Add more mappings as needed
    }

    # Use the mapping dictionary to replace common mistakes
    corrected_name = mapping.get(name.lower(), name)

    return corrected_name

'''
FUNCTION TO HANDLE THE POSSIBLE ERRORS IN THE INPUT 
This function prints a message indicating the error in case the way a request was inputed wouldn't allow the spider to scrape.
It takes a parameter:
1. inputs: The dataframe with the tribunale/procedura/anno structure 
2. loaded_dict: the dictionary with the mapping of the courthouses and their IDs on the pvp website
'''       
def inputErrorHandling(inputs, loaded_dict):
    errors = []

    for _, row in inputs.iterrows():  
        # Check year
        try:
            anno = int(row['anno'])
            if len(str(anno)) != 4:
                errors.append("L'anno deve avere 4 numeri.")
        except ValueError:
            errors.append("L'anno deve essere un numero intero (sono consentiti solo numeri).")
            
        # Check procedura
        try:
            int(row['procedura'])
        except ValueError:
            errors.append("Il numero di procedura deve essere un numero intero (sono consentiti solo numeri).")
            
        # Check tribunale
        tribunale = row['tribunale']
        n_tribunale = loaded_dict.get(tribunale.lower())
        if n_tribunale is None:
            tribunale = common_mistakes(tribunale)
            n_tribunale = loaded_dict.get(tribunale.lower())
            if n_tribunale is None:
                errors.append(f"Il tribunale {tribunale} non corrisponde a uno esistente.")
    
    inputs['tribunale'] = inputs['tribunale'].apply(lambda x: common_mistakes(x))

    if errors:
        #error_message = "\n".join(errors)
        raise ValueError(errors)



'''
FUNCTION TO EXECUTE THE ProceduraSpider SPIDER
This function calls the spider if it wasn't called already. It checks it doesn't exist in output/{today}/{n_tribunale}_{procedura}_{anno}.html bc that's how it gets created
It takes as parameters:
1. inputs: The dataframe with the tribunale/procedura/anno structure 
2. loaded_dict: the dictionary with the mapping of the courthouses and their IDs on the pvp website
3. today: today's date as "%d_%m_%Y"
'''
'''
#This worked before using the API
def useProceduraSpider(inputs, loaded_dict, today):
    process = CrawlerProcess()
    for _, row in inputs.iterrows():
        anno = int(row['anno'] )
        procedura = int(row['procedura'])
        tribunale = row['tribunale']
        n_tribunale = loaded_dict.get(tribunale.lower())
        
        if(not os.path.exists(f'output/{today}/{n_tribunale}_{procedura}_{anno}.html')):
            process.crawl(ProceduraSpider, n_tribunale, procedura, anno)
    process.start()
    '''

def useProceduraSpider(inputs, loaded_dict, today):
    settings = get_project_settings()
    runner = CrawlerRunner(settings)

    def stop_reactor():
        reactor.stop()

    crawler_deferreds = []

    def run_crawlers():
        for _, row in inputs.iterrows():
            anno = int(row['anno'])
            procedura = int(row['procedura'])
            tribunale = row['tribunale']
            n_tribunale = loaded_dict.get(tribunale.lower())

            if not os.path.exists(f'output/{today}/{n_tribunale}_{procedura}_{anno}.html'):
                spider_instance = ProceduraSpider
                d = runner.crawl(spider_instance, tribunale=n_tribunale, procedura=procedura, anno=anno)
                crawler_deferreds.append(d)

                time.sleep(random.uniform(1, 5))

        # When all crawlers are finished, stop the reactor
        defer.DeferredList(crawler_deferreds).addBoth(lambda _: stop_reactor())

    # Run the crawler in the main thread
    threads.deferToThread(run_crawlers)

    # Run the reactor outside the main thread
    reactor.run(installSignalHandlers=0)
    
'''
FUNCTION TO EXECUTE THE ReadHTMLParser on the downloaded HTMLs
Since the HTML files are downloaded as:  output/{today}/{n_tribunale}_{procedura}_{anno}.html it looks for them in that route
It takes as parameters:
1. inputs: The dataframe with the tribunale/procedura/anno structure 
2. loaded_dict: the dictionary with the mapping of the courthouses and their IDs on the pvp website
3. today: today's date as "%d_%m_%Y"
'''
def scrapeDownloadedHTMLs(today, loaded_dict):
    dictionaries = pd.DataFrame()
    directory_path = f'output/{today}'
    empty_directory_path = f'{directory_path}/empty'
    made_directory_path = f'{directory_path}/made'
    os.makedirs(empty_directory_path, exist_ok=True)
    os.makedirs(made_directory_path, exist_ok=True)
    files_in_directory = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    
    for file in files_in_directory:
        tribunale_len, procedura, anno = map(str, file.rstrip('.html').split('_'))
        tribunale_len = len(tribunale_len)
        n_tribunale, procedura, anno = map(int, file.rstrip('.html').split('_'))
        n_tribunale = f'{n_tribunale:0{tribunale_len}d}'  # I put back the 0s it might have taken from the start in the conversion
        tribunale = list(loaded_dict.keys())[list(loaded_dict.values()).index(n_tribunale)]

        parser = ReadHTMLParser(n_tribunale, procedura, anno)
        parsed_data = parser.parse()
        
        # Create one dataframe with the information parsed, adding the ID of the search for better identification later. Then, concat it to a general DF 
        parsed_data=pd.DataFrame(parsed_data)
        if parsed_data.empty:
            shutil.move(f'{directory_path}/{n_tribunale}_{procedura}_{anno}.html', empty_directory_path)
        else:
            parsed_data['id'] = f'{tribunale}_{procedura}_{anno}'
            dictionaries = pd.concat([dictionaries, parsed_data])
            shutil.move(f'{directory_path}/{n_tribunale}_{procedura}_{anno}.html', made_directory_path)
            dictionaries.to_excel('prev.xlsx', index=False, header=False)
    
    return dictionaries


def scrapeDownloadedDetailsHTMLs(today, loaded_dict):
    dictionaries = pd.DataFrame()
    directory_path = f'output/{today}'
    for file in os.listdir(directory_path):
        n_tribunale, procedura, anno = map(int, file.rstrip('.html').split('_'))
        n_tribunale = f'{n_tribunale:010d}' #I put back the 0s it might have taken from the start in the conversion
        tribunale = list(loaded_dict.keys()) [list(loaded_dict.values()).index(n_tribunale)] #get the name to put into the excel later 

        parser = ReadDetailHTMLParser(n_tribunale, procedura, anno)
        parsed_data = parser.parse()
        
        # Create one dataframe with the information parsed, adding the ID of the search for better identification later. Then, concat it to a general DF 
        parsed_data=pd.DataFrame(parsed_data)
        parsed_data['id'] = f'{tribunale}_{procedura}_{anno}'
        dictionaries = pd.concat([dictionaries, parsed_data])
    
    return dictionaries