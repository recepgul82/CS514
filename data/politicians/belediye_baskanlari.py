import requests
import bs4
import selenium
import selenium.webdriver
import selenium.webdriver.chrome
from selenium.webdriver.common.by import By
import time

parti_map = {
    "chp": "cumhuriyet_halk_partisi",
    "ak parti": "adalet_ve_kalkınma_partisi",
    "mhp": "milliyetçi_hareket_partisi",

}

output_file = "belediye_baskanlari.txt"

url = "https://tr.wikipedia.org/wiki/T%C3%BCrkiye%27de_g%C3%B6revde_olan_il_belediye_ba%C5%9Fkanlar%C4%B1n%C4%B1n_listesi"

all_names = {"Lütfü_Savaş": "cumhuriyet_halk_partisi"}

driver = selenium.webdriver.Chrome()
driver.get(url)
time.sleep(1)
ppl_counter = 0

table = driver.find_element(By.CLASS_NAME, "wikitable")


table_body = table.find_element(By.TAG_NAME, "tbody")

for row in table_body.find_elements(By.TAG_NAME, "tr"):
    all_entries = row.find_elements(By.TAG_NAME, "td")

    if len(all_entries) == 0:
        continue

    baskan_link = all_entries[1].find_element(By.TAG_NAME, "a").get_attribute("title").strip()
    if "sayfa mevcut" not in baskan_link:
        baskan_name = all_entries[2].find_element(By.TAG_NAME, "a").text.strip().replace(" ", "_")
        baskan_party_text = all_entries[4].text.strip().lower()
        baskan_party =  parti_map[baskan_party_text] if baskan_party_text in parti_map else baskan_party_text
        all_names[baskan_name] = baskan_party

        ppl_counter += 1
    

driver.quit()
print(f"Total of {ppl_counter} persons.")

with open(output_file, "w", encoding="utf-8") as file:
    for name, party in all_names.items():

        name = name.replace(" ", "_")
        party = party.replace(" ", "_").lower()
        
        file.write(name + " " + party + "\n")