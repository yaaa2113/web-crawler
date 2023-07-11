import os
from pyquery import PyQuery
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time
from tqdm import tqdm
import fire


def get_src():
    respone = requests.get("https://books.toscrape.com/")
    urls = []
    if respone.status_code == 200:
        ym = PyQuery(respone.text)
        items = [(i.attr("alt"), i.attr("src")) for i in ym("img.thumbnail").items()]
        for alt, src in items:
            urls.append((src, alt))
        return urls


def download_img(src, alt, dest_dir):
    respone = requests.get("https://books.toscrape.com/" + src, stream=True)
    total = int(respone.headers.get('content-length', 0))
    if respone.status_code == 200:
        filename = os.path.join(dest_dir, f"{alt}.jpg")
        with open(filename, "wb") as fp,tqdm(
                desc=filename,
                total=total,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
            for chunk in respone.iter_content(chunk_size=1024):
                size = fp.write(chunk)
                bar.update(size)


def main():
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=3) as pool:
        for alt, src in get_src():
            # download_img(alt, src, "downloads") 
            pool.submit(download_img,alt, src, 'downloads')
    end_time = time.time()
    print(end_time-start_time)

if __name__=='__main__':
    fire.Fire(main)
