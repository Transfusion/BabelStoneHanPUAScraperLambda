import boto3
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse

FIELDS = ["cp", "char", "ids", "note", "src", "src_refs", "enc_stat"]


def is_absolute(url):
    return bool(urlparse(url).netloc)


def scrape(event, context):
    data = pua_scrape()
    file_name = f"pua-{data['ts']}.json"
    save_file_to_s3("babelstone-han-pua-json", file_name, data)

    save_file_to_s3("babelstone-han-pua-json", "pua-latest.json", data)


def pua_scrape():
    page = requests.get("https://babelstone.co.uk/Fonts/PUA.html")
    res = {"data": [], "ts": None}
    content = BeautifulSoup(page.content, "html.parser")
    table = content.find_all("table")
    tbody = table[0].find("tbody")

    for row in tbody.find_all("tr"):
        obj = {}
        for idx, col in enumerate(row.find_all("td")):
            for a in col.find_all("a"):
                if not is_absolute(a["href"]):
                    a["href"] = urljoin("https://babelstone.co.uk/Fonts/", a["href"])

            if idx > 2:
                obj[FIELDS[idx]] = col.decode_contents()
            else:
                obj[FIELDS[idx]] = col.get_text()
        res["data"].append(obj)
    res["ts"] = datetime.now().isoformat()
    return res


def save_file_to_s3(bucket, file_name, data):
    s3 = boto3.resource("s3")
    obj = s3.Object(bucket, file_name)
    obj.put(Body=json.dumps(data, ensure_ascii=False))
