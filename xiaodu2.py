from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import requests
from lxml import etree
import os
import re

def extract_video_url(html_content):
    tree = etree.HTML(html_content)
    video_url = tree.xpath('//video[@class="art-video"]/@src')
    title = tree.xpath('//h1/text()')
    view = tree.xpath('//div[@class="extrainfo-playnums"]/text()[1]')
    likes = tree.xpath('//div[@class="extrainfo-zan like-0"]/text()')
    print('标题：',title)
    print('播放量：',view)
    print('点赞数',likes)
    if video_url:
        return video_url[0]
    else:
        return None
def search_video_url(search_content):

    tree = etree.HTML(search_content)
    box = tree.xpath('//a[@class="video-title c-link"]/@href')
    print(box)
    return (box)


def download_video(video_url):
    response = requests.get(video_url, stream=True, verify=False)
    if response.status_code == 200:
        # 从URL中提取视频文件名
        video_filename = video_url.split('/')[-1].split('?')[0].split('?')[0]
        save_path = os.path.join('下载的视频（xiaodu）', video_filename)  # 创建一个下载目录
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

    if mode==1:

        video_id = input('请输入视频ID（例如：1990129003385853460）：')
        driver.get(f"https://haokan.baidu.com/v?vid={video_id}")



        html_content= driver.page_source
        video_src_url= extract_video_url(html_content)
        if video_src_url:
            download_video(video_src_url)
            print(video_src_url)
        else:
            print('无法找到视频链接')
    else:
        search_word = input('请输入搜索词：')
        driver.get(f'https://www.baidu.com/sf/vsearch?wd={search_word}&pd=video')
        wait = WebDriverWait(driver, 100)
        input()#停顿等页面加载，最好让selenium把页面往下滑，以防加载不出足够的URL
        search_content = driver.page_source
        box = search_video_url(search_content)
        for i in range (0,11):
            video_id = box[i]
            driver.get(video_id)

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





