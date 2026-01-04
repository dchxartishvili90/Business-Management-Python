import requests
from bs4 import BeautifulSoup
try:
    pasuxi = requests.get("https://www.google.com")
    if pasuxi.status_code == 200:
        print("warmatebit Damyarebulia kavsh saiti is on ")
        soup = BeautifulSoup(pasuxi.text, 'html.parser')
        print(f" SAITIS SATAURIA :{soup.title.string}")
    else:
        print("saitma pasuxi ar daabruna")
except Exception as e :
    print(f" SHECDOMA {e}")
