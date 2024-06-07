import requests
import bs4
import selenium
import selenium.webdriver
import selenium.webdriver.chrome
from selenium.webdriver.common.by import By
import time

period_range = "27-28"

output_file = "milletvekilleri.txt"

link1 = "https://tr.wikipedia.org/wiki/TBMM_"
link2 = "._d%C3%B6nem_milletvekilleri_listesi"

period_range = period_range.split("-")
first_num = int(period_range[0])
second_num = int(period_range[1])

all_names = dict()
for i in range(first_num, second_num+1):
    url = link1 + str(i) + link2
    
    driver = selenium.webdriver.Chrome()
    driver.get(url)
    time.sleep(1)
    ppl_counter = 0

    table = driver.find_elements(By.CLASS_NAME, "jquery-tablesorter")[-1]

    table_sorter_button = driver.find_elements(By.CLASS_NAME, "headerSort")[1]

    # Click twice to open up the list where there will not be any rowspanned entries
    table_sorter_button.click()
    time.sleep(0.1)
    table_sorter_button.click()
    time.sleep(0.1)

    table_body = table.find_element(By.TAG_NAME, "tbody")

    for row in table_body.find_elements(By.TAG_NAME, "tr"):
        all_entries = row.find_elements(By.TAG_NAME, "td")
        if len(all_entries) < 2:
            break
        
        name = all_entries[1].text.strip()
        initial_party = all_entries[3].text.strip()
        changed_party = all_entries[5]
        try:
            changed_party = changed_party.find_element(By.TAG_NAME, "a").text.lower().strip()
            if changed_party != "bağımsız" and "parti" not in changed_party.lower():
                changed_party = ""
        except:
            changed_party = changed_party.text.lower().strip()
            if "milletvek" in changed_party or "ölüm" in changed_party:
                changed_party = ""
        if changed_party == "":
            all_names[name] = initial_party
        else:
            all_names[name] = changed_party
        ppl_counter += 1
        
    
    driver.quit()
    print(f"Retrieved all names from {i}th period. Total of {ppl_counter} persons.")

with open(output_file, "w", encoding="utf-8") as file:
    for name, party in all_names.items():

        name = name.replace(" ", "_")
        party = party.replace(" ", "_").lower()
        
        file.write(name + " " + party + "\n")