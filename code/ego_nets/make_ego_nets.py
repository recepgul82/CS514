import warnings
warnings.filterwarnings("ignore")
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from datetime import datetime
from matplotlib import pyplot as plt
from collections import Counter
import os
import re
import urllib.parse


def get_wikipedia_links(title):
    # Encode the title properly to handle special characters
    formatted_title = urllib.parse.quote(title.replace(' ', '_'))

    # Construct the URL to fetch the current version of the article
    url = f"https://tr.wikipedia.org/wiki/{formatted_title}"
    response = requests.get(url)
    soup = bs(response.content, 'html.parser')

    ### PARSING THE RELEVANT CONTENT ###

    # Find the main content div and extract links from paragraph and list elements
    content = soup.find('div', {'id': 'mw-content-text'})
    for tag in content.find_all("div",{"class":"reflist"}):
        tag.decompose()

    # Gather paragraphs and list items
    text_blocks = content.find_all(['p', 'li', "tr"])
    
    article_names = Counter()
    for block in text_blocks:
        links = block.find_all('a', href=True)
        # Filter links to keep only those that lead to other Wikipedia articles
        # and ignore links that are numeric
        for link in links:
            if link['href'].startswith('/wiki/') and not link['href'][6:].replace('_', ' ').isnumeric() and ":" not in link['href']:
                article_name = urllib.parse.unquote(link['href'][6:])
                article_names[article_name] += 1

    return article_names

def write_edges_to_file(query):
    edges = []
    for article, count in get_wikipedia_links(query).items():
        edges.append((query, article, count))
        new_links = get_wikipedia_links(article)
        for new_link, new_count in new_links.items():
            edges.append((article, new_link, new_count))
    with open(f"data/{query}_ego_net.txt", "w") as f:
        for edge in edges:
            f.write(f"{edge[0]}\t{edge[1]}\t{edge[2]}\n")


if __name__ == "__main__":
    files = [file[:file.index("_ego")] for file in os.listdir("data")]
    name_list= pd.read_csv("edit_history.csv")["name"].tolist()
    for i, name in enumerate(name_list[::-1], start=1):
        print(f"{i}\t",datetime.now().strftime("%H:%M"), end="\t\t")
        if name in files:
            print("Already processed: ", name)
            continue
        print("Processing: ", name)
        write_edges_to_file(name)
    