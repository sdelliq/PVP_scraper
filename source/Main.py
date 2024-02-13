
import pandas as pd
import os
from date_utils import today as todayDate
from source.functions import dicToExcel, inputErrorHandling, read_or_create_tribunales, useProceduraSpider, scrapeDownloadedHTMLs, df_input_clean, scrapeDownloadedDetailsHTMLs #,input_read
from dotenv import load_dotenv 



def main_function(INPUT_PATH: pd.DataFrame, OUTPUT_EXCEL_FOLDER:str, OUTPUT_EXCEL_NAME: str): 
    load_dotenv()   
    today = todayDate

    TRIBUNALE_PATH = os.environ.get("TRIBUNALE_PATH")
    OUTPUT_EXCEL_PATH = f'{OUTPUT_EXCEL_FOLDER}/{OUTPUT_EXCEL_NAME}'
    OUTPUT_PATH = f'{OUTPUT_EXCEL_FOLDER}/{today}'
    
    loaded_dict = read_or_create_tribunales(TRIBUNALE_PATH)

    inputs = df_input_clean(INPUT_PATH)

    inputErrorHandling(inputs, loaded_dict)
    useProceduraSpider(inputs, loaded_dict, today)
    dictionaries = scrapeDownloadedHTMLs(today, loaded_dict)

    '''dictionaries_det = scrapeDownloadedDetailsHTMLs(today, loaded_dict)

    dictionaries = dictionaries.merge(dictionaries_det, on=['Data Vendita', 'id', "Prezzo base d'asta"])
    dictionaries = dictionaries.drop_duplicates()'''

    dicToExcel(OUTPUT_EXCEL_PATH, dictionaries)
    '''
    if len(dictionaries['id'].unique()) == len(os.listdir(OUTPUT_PATH)):
        dicToExcel(OUTPUT_EXCEL_PATH, dictionaries)
    else:
        main_function(pd.merge(INPUT_PATH, dictionaries, how='outer', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1), OUTPUT_EXCEL_FOLDER, OUTPUT_EXCEL_NAME)
'''
