from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os 
import pathlib
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import gspread

options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--ignore-ssl-errors')

os.environ["WDM_LOG_LEVEL"] = "0"
        
script_directory = pathlib.Path().absolute()
options.add_argument(f"user-data-dir={script_directory}\\Selenium")

service = Service(r"C:\Users\cste_sd\Downloads\chromedriver_win32\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://seller.indiamart.com/messagecentre/")
input()
Name=[]
GSTNumber=[]
PhoneNumber=[]
Location=[]
Email=[]
LeadDate=[]

sa=gspread.service_account(filename="GoogleAccessKey.json")
WorkBook=sa.open_by_url("https://docs.google.com/spreadsheets/d/1EZt-4PDuZfMrtKhIgnHyANruLkUOAi3iproHt12uxH0/edit#gid=1984851733")
WorkSheet=WorkBook.get_worksheet(5)
NameCheck=WorkSheet.get("A2")[0][0]
for i in range(0,2000):

    element=driver.find_element(By.XPATH,f"/html/body/div[5]/div[3]/div[2]/div[2]/div[7]/div[15]/div[3]/div[2]/div/div[1]/ul/li[{i+1}]")
    element.click()
    name=driver.find_element(By.XPATH,"/html/body/div[5]/div[3]/div[2]/div[2]/div[27]/div[7]/div/div[1]/div[1]/div[1]").text
    gst=driver.find_element(By.XPATH,"/html/body/div[5]/div[3]/div[2]/div[2]/div[27]/div[7]/div/div[3]/span[2]/span[2]/span").text
    phone=driver.find_element(By.XPATH,"/html/body/div[5]/div[3]/div[2]/div[2]/div[27]/div[7]/div/div[2]/div/span[2]/span").text
    location=driver.find_element(By.XPATH,"/html/body/div[5]/div[3]/div[2]/div[2]/div[27]/div[7]/div/div[3]/span[1]").text
    email=driver.find_element(By.XPATH,"/html/body/div[5]/div[3]/div[2]/div[2]/div[27]/div[7]/div/div[2]/div/span[3]/span").text
    leaddate=driver.find_element(By.XPATH,f"/html/body/div[5]/div[3]/div[2]/div[2]/div[7]/div[15]/div[3]/div[2]/div/div[1]/ul/li[{i+1}]/div[3]/p").text
    if(NameCheck==name):
        break
    Name.append(name)
    GSTNumber.append(gst)
    PhoneNumber.append(phone)
    Location.append(location)
    Email.append(email)
    LeadDate.append(leaddate)
UpdateValue=[]
for i in range(len(Name)):
    UpdateValue.append([Name[i],Location[i],PhoneNumber[i],Email[i],GSTNumber[i],LeadDate[i]])

WorkSheet.insert_rows(UpdateValue,row=2)

    


input()