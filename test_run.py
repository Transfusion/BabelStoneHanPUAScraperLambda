from pua_scraper.handler import pua_scrape
import json

data = pua_scrape()
print(json.dumps(data["data"][:50], ensure_ascii=False))
print(data["ts"])
