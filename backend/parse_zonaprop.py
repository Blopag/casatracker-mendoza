import os
from bs4 import BeautifulSoup
import json
import re

def parse_zonaprop_state():
    file_path = os.path.join(os.path.dirname(__file__), 'debug_zonaprop.html')
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    scripts = soup.find_all('script')
    
    for script in scripts:
        if script.string and 'window.__PRELOADED_STATE__' in script.string:
            content = script.string.strip()
            start_idx = content.find('{')
            if start_idx != -1:
                json_str = content[start_idx:]
                parts = re.split(r';\s*window\.', json_str)
                for part in parts:
                    try:
                        if part.endswith(';'):
                            part = part[:-1]
                        data = json.loads(part)
                        
                        if 'listStore' in data and 'listPostings' in data['listStore']:
                            postings = data['listStore']['listPostings']
                            if len(postings) > 0:
                                p = postings[0]
                                print("mainFeatures:", p.get('mainFeatures'))
                                print("generalFeatures:", p.get('generalFeatures'))
                                print("visiblePictures:", p.get('visiblePictures'))
                                print("postingLocation:", p.get('postingLocation'))
                        return
                    except Exception as e:
                        pass

if __name__ == "__main__":
    parse_zonaprop_state()
