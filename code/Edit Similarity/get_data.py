import requests
import json
import asyncio
import aiohttp
from aiohttp import ClientTimeout
from bs4 import BeautifulSoup
import nest_asyncio
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Allow nested use of asyncio.run()
nest_asyncio.apply()

def get_revisions(page_title, start_date, end_date):
    url = f"https://tr.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&titles={page_title}&rvstart={end_date}&rvend={start_date}&rvlimit=max&rvprop=ids|timestamp|comment"
    
    # Configure retries
    retries = Retry(total=5, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    
    response = http.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    page_id = list(data['query']['pages'].keys())[0]
    if 'revisions' in data['query']['pages'][page_id]:
        revisions = data['query']['pages'][page_id]['revisions']
        return revisions
    else:
        return []

async def get_diff(session, oldid, newid):
    url = f"https://tr.wikipedia.org/w/api.php?action=compare&format=json&fromrev={oldid}&torev={newid}"
    async with session.get(url) as response:
        data = await response.json()
        if 'compare' in data and '*' in data['compare']:
            return data['compare']['*']
        else:
            return ''

def extract_changes(diff_html):
    soup = BeautifulSoup(diff_html, 'html.parser')
    ins_tags = soup.find_all('ins', class_='diffchange diffchange-inline')
    del_tags = soup.find_all('del', class_='diffchange diffchange-inline')
    changes = {
        'added': [tag.text for tag in ins_tags],
        'removed': [tag.text for tag in del_tags]
    }
    return changes

async def process_page(session, page_title, start_date, end_date):
    revisions = get_revisions(page_title, start_date, end_date)
    changes = []

    tasks = []
    for i in range(len(revisions) - 1):
        oldid = revisions[i+1]['revid']
        newid = revisions[i]['revid']
        tasks.append(get_diff(session, oldid, newid))

    diffs = await asyncio.gather(*tasks)

    for diff_html in diffs:
        if diff_html:  # Check if diff_html is not empty
            changes.append(extract_changes(diff_html))
    
    result = {page_title: changes}
    return result

async def process_intervals(intervals):
    timeout = ClientTimeout(total=60)
    all_changes = {f"{start_date}_{end_date}": {} for start_date, end_date, _ in intervals}

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for start_date, end_date, page_titles in intervals:
            tasks = []
            for page_title in page_titles:
                tasks.append(process_page(session, page_title, start_date, end_date))

            results = await asyncio.gather(*tasks)

            for changes in results:
                page_title = list(changes.keys())[0]
                interval_key = f"{start_date}_{end_date}"
                if page_title not in all_changes[interval_key]:
                    all_changes[interval_key][page_title] = []
                all_changes[interval_key][page_title].extend(changes[page_title])
    
    return all_changes

def save_changes_to_json(all_changes, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_changes, f, ensure_ascii=False, indent=4)

intervals = [
    ("2016-05-01T00:00:00Z", "2016-08-31T23:59:59Z", ["Recep_Tayyip_Erdoğan","Devlet_Bahçeli","Binali_Yıldırım","Ahmet_Davutoğlu","Mehmet_Şimşek","Meral_Akşener","Fatma_Betül_Sayan_Kaya"]),
    # Add more intervals with different people here
]

all_changes = asyncio.run(process_intervals(intervals))

save_changes_to_json(all_changes, "all_changes.json")

print("Changes saved to all_changes.json")
