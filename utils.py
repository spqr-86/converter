import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET


def kzt_course():
    url = "https://onlymir.ru/?ysclid=ld5juogtia19615737"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    needed_block = soup.find(text="Казахстанский тенге").find_parent().find_parent().find_parent()
    course = float(needed_block.find("div", class_="btn-content").text)
    return course


def usd_course():
    url = "https://cbr.ru/scripts/XML_daily.asp/"
    now = datetime.now()
    current_date = now.strftime("%d/%m/%Y")
    params = {
        "date_req": current_date,
    }
    r = requests.get(url, params=params).text
    root = ET.fromstring(r)
    usd = root.find(".//Valute[CharCode='USD']")
    if usd is not None:
        return float(usd.find('Value').text.replace(",", "."))
    else:
        return "Valute with CharCode 'USD' not found."
