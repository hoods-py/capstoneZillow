from bs4 import BeautifulSoup
import smtplib
import requests
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time

OPTIONS = webdriver.FirefoxOptions()
SERVICE = Service("/home/hoods/Documents/development/geckodriver")
dr = webdriver.Firefox(service=SERVICE, options=OPTIONS)

ZILLOW_URL = "https://www.zillow.com/homes/for_rent/1-_beds/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C" \
             "%22usersSearchTerm%22%3Anull%2C%22mapBounds%22%3A%7B%22west%22%3A-122.56276167822266%2C%22east%22%3A" \
             "-122.30389632177734%2C%22south%22%3A37.69261345230467%2C%22north%22%3A37.857877098316834%7D%2C" \
             "%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A" \
             "%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse" \
             "%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B" \
             "%22value%22%3Afalse%7D%2C%22pmf%22%3A%7B%22value%22%3Afalse%7D%2C%22pf%22%3A%7B%22value%22%3Afalse%7D" \
             "%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min" \
             "%22%3A1%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%7D"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSfyO_2IeFdlIZBu6gg1hPA_48RPE3FnRpSc2TEYVPkEOmQBmA/viewform?usp=sf_link"
dr.get(ZILLOW_URL)
time.sleep(4)

for _ in range(20):
    webdriver.ActionChains(dr).key_down(Keys.TAB).perform()
for _ in range(120):
    webdriver.ActionChains(dr).key_down(Keys.ARROW_DOWN).perform()

html_data = dr.page_source

# headers so i don't get kicked out of the webpage
headers = {
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

response = requests.get(url=ZILLOW_URL, headers=headers)
# create soup from the page
time.sleep(5)
soup = BeautifulSoup(html_data, "html.parser")
print(response)

# isolate the listings by tag and class
listings = soup.find_all("li", class_="ListItem-c11n-8-85-1__sc-10e22w8-0")
prices = []
addresses = []
urls = []
for listing in listings:
    try:
        # get price of each listing
        price_element = listing.find("div", class_="StyledPropertyCardDataWrapper-c11n-8-85-1__sc-1omp4c3-0 jVBMsP "
                                                   "property-card-data")
        price_span = price_element.find("span").text.strip()
        price = ''.join(x for x in price_span if x in ".1234567890")
        prices.append(price)
        print(price)
        # # get address of each listing
        address_element = listing.find("div", class_="StyledPropertyCardDataWrapper-c11n-8-85-1__sc-1omp4c3-0 jVBMsP property-card-data")
        address_ee = address_element.find("address").text
        addresses.append(address_ee)
        print(address_ee)
        # get url
        url = "https://www.zillow.com" + listing.find("a", class_="StyledPropertyCardDataArea-c11n-8-85-1__sc-yipmu-0 gdfTyO property-card-link")['href']
        print(url)
        urls.append(url)
    except:
        pass


time.sleep(5)

# Head over to the google form to fill in the data

dr.get(FORM_LINK)

# Combine the data from the lists into a dictionary
listings_dict = {}
listings_data = list(zip(addresses, prices, urls))
for address, price, url in listings_data:
    listings_dict[address] = {"price": price, "url": url}

# Get page elements of the form for data entry


time.sleep(3)
address_keys = list(listings_dict.keys())
for x in range(len(address_keys) - 1):
    time.sleep(2)
    address_entry = dr.find_element(By.XPATH,
                                    "/html/body/div/div[2]/form/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input")

    address_entry.send_keys(f"{address_keys[x]}")
    time.sleep(1)
    price_entry = dr.find_element(By.XPATH,
                                  "/html/body/div/div[2]/form/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input")

    price_entry.send_keys(f"{listings_dict[address_keys[x]]['price']}")
    time.sleep(1)
    link_entry = dr.find_element(By.XPATH,
                                 "/html/body/div/div[2]/form/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input")

    link_entry.send_keys(f"{listings_dict[address_keys[x]]['url']}")
    time.sleep(1)
    submit = dr.find_element(By.XPATH, "/html/body/div/div[2]/form/div[2]/div/div[3]/div[1]/div[1]/div/span/span")

    submit.click()
    time.sleep(5)
    submit_another_response = dr.find_element(By.LINK_TEXT, "Submit another response")
    submit_another_response.click()
    time.sleep(3)

dr.close()




