# Import libraries
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.timeshighereducation.com/world-university-rankings/2024/world-ranking#"
# Function to scrape
def scrape_page(driver, data):
    # Parse the content of the specified URL.
    soup = BeautifulSoup(driver.page_source, 'html.parser')
     # Find all 'tr' (in this case) inside the link provided.
    universities = soup.find_all('tr')
    
    for university in universities:
        name_elem = university.find('a', class_='ranking-institution-title')
        name = name_elem.text.strip() if name_elem else "N/A"

        name_rank = university.find('td', class_='rank sorting_1 sorting_2')
        rank = name_rank.text.strip() if name_rank else "N/A"

        name_locat = university.find('div', class_='location')
        locat = name_locat.text.strip() if name_locat else "N/A"

        if locat == 'United States':
            data.append({
                "Name ": name,
                "Rank ": rank,
                "Location ": locat
            })

        if locat == 'United States':
            print(f"Name: {name} \r\n Rank: {rank} \r\n Location: {locat}")
            print("--------------------------------")
            


def scrape_first_page(url):
    driver = webdriver.Chrome()
    data = []
    try:
        driver.get(url)
        scrape_page(driver,data)
    finally:
        driver.quit()

    df = pd.DataFrame(data)
    df.to_excel("universities_ranking_first_page.xlsx", index=False)
    print("Data saved to 'universities_ranking_first_page.xlsx'")
    print("Scraping finished.")

scrape_first_page(url)