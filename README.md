# *PVP web scraping project*
This project's purpose is to scrape the pvp website (portale delle vendite pubbliche https://pvp.giustizia.it/pvp/) 

It is configured to run on docker, so you should have it downloaded on your computer. Then:

1. Run "docker-compose up extract_data" on the terminal 
2. Open on the browser: http://127.0.0.1:8000/docs
3. The defult outputs work just fine, but you can change them if you want. Then choose the input file, it *must* have the following structure:
        * tribunale= this column must have the name of the courthouse as it would have appeared on the website. Example: tribunale di aosta
        * procedura= this column must have the number of the procedure. Example: 18 
        * anno= this column must have the year of the procedure. Example: 2017   
4. You can click on Download file to download the output, or go search for it in the docker containter file's window. 
5. Be amazed 

## Small Code Explination
### Spiders:
In source/spiders there are two important files:
1. tribunals_dic.py = creates the tribunale_data.json file, that contains a dictionary with the id of the courthouse that the website uses, and its name. 
2. pvp_web_scraping.py = Contains the spider ProceduraSpider that takes tribunale(the id from before), procedura and anno as parameters. It downloads an HTML file 
using the tribunale(number), procedura and year as the name; it puts it into a folder with the name of the date (it creates it if it doesn't exist). 

### Source:
Important files inside source/ :
1. functions.py has the functions to be used across the project. They are explained in the same file.  
2. HTML_scraper.py reads the downloaded HTMLS and returns the general information and from details the Tipologia. 
3. Main.py reads the input file, does error handling on it and runs the ProceduraSpider on its lines. It then reads the downloaded HTML files, creates a dataframe with the scraped information, and finally it uses the function to create the output excel file.  


### Top folder
1. main.py contains the call to the API and the code to call the spiders when the file is inputed.
2. date_utils: contains the date to use today's date or a particular one in case it's neccesary

### Extra:
The notebook.ipynb contains some code I used for some particular cases. Each one is documented. 


