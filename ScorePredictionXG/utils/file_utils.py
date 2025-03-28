from bs4 import BeautifulSoup
import pandas as pd

def read_html_to_soup(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return BeautifulSoup(f, 'html.parser')

def parse_team_data(soup):
    rows = soup.find_all('tr')
    columns = [col.get_text().strip() for col in rows[0].find_all('th')]
    data = [[cell.get_text().strip() for cell in row.find_all('td')] for row in rows[1:]]
    return pd.DataFrame(data, columns=columns)
