import os
from dotenv import load_dotenv
import requests
import json
import csv

# get api key from .env file
load_dotenv()
API_KEY = os.getenv("NASDAQ_API_KEY")
#print(API_KEY)

# import relevant API modules (Carl Zeiss Meditec AFX_X, from Frankfurt Stock Exchange FSE)
# "https://data.nasdaq.com/api/v3/datasets/{database_code}/{dataset_code}/data.{return_format}?api_key=" + API_KEY
api_url = "https://data.nasdaq.com/api/v3/datasets/FSE/AFX_X/data.json?api_key=" + API_KEY

database = "FSE"
dataset = "AFX_X"
return_format = "json"
start_date = "2017-01-01"   # YYYY-MM_DD
end_date = "2017-12-31"

test_url = "https://data.nasdaq.com/api/v3/datasets/"+("%s/"%database)+("%s/"%dataset)+("data.%s?"%return_format)
test_url += "start_date="+start_date + "&end_date="+end_date + "&api_key="+API_KEY
#print(test_url)
#print(api_url)

def getStockData(search_params={'database_code':'FSE', 'dataset_code':'AFX_X'}):
    # inspect the base json structure
    base_url = "https://data.nasdaq.com/api/v3/datasets"

    # myResponse = requests.get(api_url)
    myResponse = requests.get(test_url)
    #print(type(myResponse)) # requests.models.Response
    #print(myResponse.json())
    
    if(myResponse.ok):
        # loading the response data into a dict variable data
        dataset = json.loads(myResponse.content.decode('utf-8'))
        column_names = dataset['dataset_data']['column_names']
        #print(column_names)
        #   0       1       2       3       4       5           6       
        # ['Date', 'Open', 'High', 'Low', 'Close', 'Change', 'Traded Volume', 
        # 'Turnover', 'Last Price of the Day', 'Daily Traded Units', 'Daily Turnover']
        #   7           8                       9                       10
        
        # 2d list
        data = dataset['dataset_data']['data']  # ordered columns: newest to oldest 
        numDays = len(data)
        #print(data[0:3])

        # Compute: 
        openMax = 0     # highest Opening prices in this period
        openMin = float('inf')     # lowest Opening prices in this period
        rangeMax = 0    # largest change in any one day (based on High and Low price)
        diffMax = 0     # largest change between ANY 2 (CONSECUTIVE?) days (based on Closing price)
        closeMax = 0
        closeMin = float('inf')
        avgVol = 0      # average daily Trading Volume during this year
        medianVol = 0   # (optional) median trading volume during this year
        
        # some Opening values are missing (day 169,179,180) (May1,Apr17,Apr14)
        # i = 0
        # for day in data:          
            # if(day[1]==None):   
                # print(i)
                # print(day[0])
            # i += 1
        
        # Compute Output & Write database data to csv file
        file_name = "api_data.csv"
        with open(file_name,'w',encoding='utf-8',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(column_names)
       
            for day in data:
                writer.writerow(day)
                if(day[1]!=None):           # some Opening data is missing
                    if(day[1]>openMax):     
                        openMax = day[1]
                    if(day[1]<openMin):
                        openMin = day[1]
                if(day[2]-day[3] > rangeMax):
                    rangeMax = day[2]-day[3]
                if(day[4]>closeMax):
                    closeMax = day[4]
                if(day[4]<closeMin):
                    closeMin = day[4]
                avgVol += day[6]
        f.close()
        diffMax = closeMax-closeMin
        avgVol /= numDays
        
        output = ("Open Max: %0.2f"%openMax) + "\n"
        output += ("Open Min: %0.2f"%openMin) + "\n"
        output += ("Range Max: %0.2f"%rangeMax) + "\n"
        output += ("Diff Max: %0.2f"%diffMax) + "\n"
        output += ("Avg Volume: %0.1f"%avgVol)
        print(output)
        
        # write output to text file
        file_name = "api_output.txt"
        with open(file_name,'w') as f:
            f.write(output)
        f.close()
        

if __name__ == '__main__':
    getStockData()

    
# {'id': 10095370, 'dataset_code': 'AFX_X', 'database_code': 'FSE', 'name': 'Carl Zeiss Meditec (AFX_X)', 'description': 'Stock Prices for Carl Zeiss Meditec (2020-11-02) from the Frankfurt Stock Exchange.<br><br>Trading System: Xetra<br><br>ISIN: DE0005313704', 'refreshed_at': '2020-12-01T14:48:09.907Z', 'newest_available_date': '2020-12-01', 'oldest_available_date': '2000-06-07', 'column_names': ['Date', 'Open', 'High', 'Low', 'Close', 'Change', 'Traded Volume', 'Turnover', 'Last Price of the Day', 'Daily Traded Units', 'Daily Turnover'], 'frequency': 'daily', 'type': 'Time Series', 'premium': False, 'database_id': 6129}    