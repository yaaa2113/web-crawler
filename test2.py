import os
from pyquery import PyQuery
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time
from tqdm import tqdm
import fire
import jieba
from imageio import imread
import wordcloud


# 得到标题与图片的网址
def get_src():
    respone = requests.get("https://books.toscrape.com/")
    urls = []
    if respone.status_code == 200:
        ym = PyQuery(respone.text)
        items = [(i.attr("alt"), i.attr("src")) for i in ym("img.thumbnail").items()]
        for alt, src in items:
            urls.append((src, alt))
        return urls


# 从得到的网址下载图片到本地并命名
def download_img(src, alt, dest_dir):
    respone = requests.get("https://books.toscrape.com/" + src, stream=True)
    total = int(respone.headers.get("content-length", 0))
    if respone.status_code == 200:
        filename = os.path.join(dest_dir, f"{alt}.jpg")
        with open(filename, "wb") as fp, tqdm(
            desc=filename,
            total=total,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in respone.iter_content(chunk_size=1024):
                size = fp.write(chunk)
                bar.update(size)


# 统计词数并写入txt文本
def countfile():
    with open("tittle.txt", "r", encoding="utf-8") as file:
        text = file.read()

    # 使用jieba分词获取英文单词
    words = jieba.lcut(text)
    english_letters = [word for word in words if word.isalpha()]

    # 统计英文字母个数
    letter_counts = {}
    for letter in english_letters:
        letter_counts[letter] = letter_counts.get(letter, 0) + 1

    # 降序排序
    sorted_counts = sorted(letter_counts.items(), key=lambda x: x[1], reverse=True)

    with open("tittlecount.txt", "w", encoding="utf-8") as file:
        for letter, count in sorted_counts:
            file.write("{:<8} {:>2}\n".format(letter, count))


# 创建词云图
def wordsclound_img():
    txt = open(
        r"C:/Users/yaaa/PycharmProjects/project/tittlecount.txt", "r", encoding="utf-8"
    ).read()
    w = wordcloud.WordCloud(
        background_color="white",
        width=1000,
        height=800,
        font_path="C:/Windows/Fonts/STCAIYUN.TTF",
        mask=imread(r"C:/Users/yaaa/PycharmProjects/project/1.png"),
    )
    w.generate(txt)
    w.to_file("C:/Users/yaaa/PycharmProjects/project/tittle.png")


def main():
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=3) as pool:
        for alt, src in get_src():
            # download_img(alt, src, "downloads")
            pool.submit(download_img,alt, src, 'downloads')
            with open("tittle.txt", "a", encoding="utf-8") as fp:
                fp.write(src + "\n")
    countfile()
    wordsclound_img()
    end_time = time.time()
    print(end_time - start_time)


if __name__ == "__main__":
    fire.Fire(main)
