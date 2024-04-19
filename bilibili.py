import requests
import json
import re
import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from lxml import etree

def get(url):
    url ='https:' + url

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.289 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
    }

    resp = requests.get(url=url, headers=header)

    html = re.compile(r'window.__playinfo__=(.*?)</script>', re.S)

    title = re.compile(r'<title data-vue-meta="true">(.*?)</title>', re.S)
    title = title.findall(resp.text)[0]
    print('标题：',title)

    keyword = re.compile(r'<meta data-vue-meta="true" itemprop="keywords" name="keywords" content=(.*?)<meta data-vue-meta="true" itemprop="description" ', re.S)
    keyword = keyword.findall(resp.text)[0]
    print('关键词：',keyword)

    introduction = re.compile(r'<meta data-vue-meta="true" itemprop="description" name="description" content="(.*?)<meta data-vue-meta="true" itemprop="author"', re.S)
    introduction = introduction.findall(resp.text)[0]
    print('简介：',introduction)

    html_data = html.findall(resp.text)[0]  # 从列表转换为字符串

    json_data = json.loads(html_data)

    videos = json_data['data']['dash']['video']  # 这里得到的是一个列表

    video_url = videos[0]['baseUrl']  # 视频地址

    audios = json_data['data']['dash']['audio']
    audio_url = audios[0]['baseUrl']

    download_folder = "下载的视频（b站）"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    video_filename = title + ".mp4"
    audio_filename = title + ".mp3"
    safevideo_filename = video_filename.replace('[', '').replace(']', '').replace('【', '').replace('】', '').replace('/', '')
    safeaudio_filename = audio_filename.replace('[', '').replace(']', '').replace('【', '').replace('】', '').replace('/', '')
    safename = title.replace('[', '').replace(']', '').replace('【', '').replace('】', '').replace('/', '')
    # 完整的文件路径
    video_filepath = os.path.join(download_folder, safevideo_filename)
    audio_filepath = os.path.join(download_folder, safeaudio_filename)

    # 确保下载文件夹存在
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # 发送HTTP GET请求并下载视频
    resp1 = requests.get(url=video_url, headers=header)
    # 确保请求成功
    if resp1.status_code == 200:
        with open(video_filepath, mode='wb') as f:
            f.write(resp1.content)
            print(f"视频文件 {video_filename} 下载成功。")
    else:
        print(f"视频文件下载失败，状态码：{resp1.status_code}")

    # 发送HTTP GET请求并下载音频
    resp2 = requests.get(url=audio_url, headers=header)
    # 确保请求成功
    if resp2.status_code == 200:
        with open(audio_filepath, mode='wb') as f:
            f.write(resp2.content)
            print(f"音频文件 {audio_filename} 下载成功。")
    else:
        print(f"音频文件下载失败，状态码：{resp2.status_code}")

    command = "ffmpeg -i " + safevideo_filename + " -i " + safeaudio_filename + " -acodec copy -vcodec copy " + title + "_out.mp4"
    #在合并的时候safevideo_filename后面.mp4后面会多一个.以至于识别不出，找不到什么原因QAQ


    os.system(command=command)
def main():
    service = Service(executable_path="msedgedriver.exe")
    driver = webdriver.Edge(service=service)

    mode = int(input('输入id请按1，输入搜索词检索按0: '))
    wait = WebDriverWait(driver, 100)

    if mode==1:
        video_id = input('请输入BV号：')
        url=f"//www.bilibili.com/video/{video_id}/"
        get(url)

    else:
        search_word = input('请输入搜索词：')
        driver.get(f'https://search.bilibili.com/all?keyword={search_word}')
        wait = WebDriverWait(driver, 100)
        search_content = driver.page_source
        tree = etree.HTML(search_content)
        video_url = tree.xpath('//a[@data-mod="search-card"]/@href')
        values = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27]#每个视频会出现3个别的id都一样的元素a，两个是视频网址，一个是作者网址，所以采用这种笨办法来提取前十个
        for i in values:
            print(video_url[i])
            get(video_url[i])
    # 关闭浏览器
    driver.quit()

if __name__ == '__main__':
    main()

