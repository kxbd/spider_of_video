from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import requests
from lxml import etree
import os
import re


def extract_video_url(html_content):
    tree = etree.HTML(html_content)
    video_url = tree.xpath('//meta[@name="og:img_video"]/@content')
    title = tree.xpath('//meta[@property="og:title"]/@content')
    view = tree.xpath('//span[@class="index_playNum_Tn7xu"]/text()')
    likes = tree.xpath('//*[@id="js_supportCount"]/text()')
    channel = tree.xpath('//div[@index="1"]/text()')
    print('标题：',title)
    print('频道：',channel)
    print('播放量：',view)
    print('点赞数',likes)
    if video_url:
        return video_url[0]
    else:
        return None
def search_video_url(search_content):

    pattern = r'"id":"([^"]+)"'

    # 使用re.findall()查找所有匹配的id字段
    ids = re.findall(pattern, search_content)
    return ids

def download_video(video_url):
    response = requests.get(video_url, stream=True, verify=False)
    if response.status_code == 200:
        # 从URL中提取视频文件名
        video_filename = video_url.split('/')[-1]
        save_path = os.path.join('下载的视频(phx)', video_filename)  # 创建一个下载目录
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f'视频下载完成: {save_path}')
    else:
        print(f'无法获取视频链接，状态码：{response.status_code}')

def main():
    service = Service(executable_path="msedgedriver.exe")
    driver = webdriver.Edge(service=service)

    mode = int(input('输入id请按1，输入搜索词检索按0: '))
    wait = WebDriverWait(driver, 100)
    if mode==1:

        video_id = input('请输入视频ID（例如：8V8ZaWDukBx）：')
        driver.get(f"https://v.ifeng.com/c/{video_id}")

        wait = WebDriverWait(driver, 15)

        html_content= driver.page_source
        video_src_url= extract_video_url(html_content)
        if video_src_url:
            download_video(video_src_url)
            print(video_src_url)
        else:
            print('无法找到视频链接')
    else:
        search_word = input('请输入搜索词：')
        driver.get(f'https://shankapi.ifeng.com/api/getSoFengData/video/{search_word}/1/getSoFengDataCallback?callback=getSoFengDataCallback')
        wait = WebDriverWait(driver, 100)
        search_content = driver.page_source
        box = search_video_url(search_content)
        for i in range (0,11):
            video_id = box[i]
            driver.get(f"https://v.ifeng.com/c/{video_id}__")

            wait = WebDriverWait(driver, 15)

            html_content = driver.page_source
            video_src_url = extract_video_url(html_content)
            if video_src_url:
                download_video(video_src_url)
                print(video_src_url)
            else:
                print('无法找到视频链接')
    # 关闭浏览器
    driver.quit()

if __name__ == '__main__':
    main()





