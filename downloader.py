import json
import os
import requests
import time

class INatGridDownloader:
    def __init__(self, timeout=1, target="cache"):
        if not os.path.exists(target):
            os.mkdir(target)
        self.s = requests.Session()
        self.last = 0
        self.target = target
        self.timeout = timeout
        self.url = "https://api.inaturalist.org/v1/observations/species_counts"

    def _get(self, params, desc):
        if time.time() < self.last + self.timeout:
            time.sleep(self.timeout - (time.time() - self.last))
        self.last = time.time()
        resp = self.s.get(self.url, params=params)
        if resp.status_code != 200:
            print(f"warning: {desc} returned status code {resp.status_code}")
        return resp.content

    def get(self, lat_start, lon_start, lat_end, lon_end, req_desc=None):
        # create a unique string to describe the request
        if not req_desc:
            req_desc = f"{lon_start}_{lat_start}_{lon_end}_{lat_end}"

        # prepare parameters and download first file, containing # results
        params = {
                "swlng": lon_start,
                "swlat": lat_start,
                "nelng": lon_end,
                "nelat": lat_end,
        }
        print(f"Downloading {req_desc}...")
        data = self._get(params, req_desc)
        
        # save to file
        page_number = 1
        with open(f"{self.target}/{req_desc}_{page_number:03}.json", "wb") as f:
            f.write(data)
        
        # check for and load additional pages
        j = json.loads(data)
        while j["per_page"] * page_number < j["total_results"]:
            page_number += 1
            params["page"] = page_number
            print(f"Downloading {req_desc} page {page_number}...")
            data = self._get(params, req_desc)
            with open(f"{self.target}/{req_desc}_{page_number:03}.json", "wb") as f:
                f.write(data)

