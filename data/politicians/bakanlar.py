import requests
import bs4
import selenium
import selenium.webdriver
import selenium.webdriver.chrome
from selenium.webdriver.common.by import By
import time

period_range = "66-67"

output_file = "bakanlar.txt"

link1 = "https://tr.wikipedia.org/wiki/"
link2 = "._T%C3%BCrkiye_H%C3%BCk%C3%BBmeti"

period_range = period_range.split("-")
first_num = int(period_range[0])
second_num = int(period_range[1])

all_names = set()
for i in range(first_num, second_num+1):
    url = link1 + str(i) + link2
    
    driver = selenium.webdriver.Chrome()
    driver.get(url)
    time.sleep(1)

    table = driver.find_elements(By.CLASS_NAME, "wikitable")[-1]
    table_body = table.find_element(By.TAG_NAME, "tbody")

    decrease_col = False
    total_span = 0
    ppl_counter = 0
    for row in table_body.find_elements(By.TAG_NAME, "tr"):
        counter = 0
        span_decrement = 0
        if total_span > 0:
            span_decrement = 1
            total_span -= 1

        if len(row.find_elements(By.TAG_NAME, "td")) <= 2:
            continue

        for tdata in row.find_elements(By.TAG_NAME, "td"):
            counter += 1
            rowspan_attr = tdata.get_attribute("rowspan")
            if (row.find_elements(By.TAG_NAME, "td")[0] == tdata and rowspan_attr is not None):
                total_span = int(rowspan_attr) - 1
                decrease_col = True

            if counter == 3 - span_decrement:
                a_elem = tdata.find_element(By.TAG_NAME, "a")
                name = a_elem.text.strip().replace(" ", "_")
                all_names.add(name)
                print(name)
                ppl_counter += 1

                
    
    driver.quit()
    print(f"Retrieved all names from {i}th period. Total of {ppl_counter} persons.")

with open(output_file, "w", encoding="utf-8") as file:
    for name in all_names:
        file.write(name + "\n")