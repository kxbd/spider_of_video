import requests
from lxml import etree
import os
import re
from selenium import webdriver
from selenium.webdriver.edge.service import Service


title = ' '
guid = re.compile(r'itemguid="(.*?)"', re.S)
m3u8 = re.compile(r'"hls_url":"(.*?)"', re.S)
ts = re.compile(r'/(.*?)450.m3u8', re.S)
front = re.compile(r'https:(.*?)/asp', re.S)

def extract_video_url(html_content):
    tree = etree.HTML(html_content)
    global title
    title = tree.xpath('//meta[@property="og:title"]/@content')
    likes = tree.xpath('//span[@class="like"]/text()')
    channel = tree.xpath('//*[@id="video"]/script[13]/text()')
    introduction = tree.xpath('//meta[@property="og:description"]/@content')
    print('标题：', title)
    print('频道：', channel)
    print('点赞数', likes)
    print('简介', introduction)

def search_video_url(search_content):
    tree = etree.HTML(search_content)
    box = [None] * 100
    for i in range(1,11):
        box[i] = tree.xpath(f'//*[@id="searchlist"]/li[{str(i)}]/div[2]/p/a/@href')
    return box



def download_video(video_url):
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        # 从URL中提取视频文件名
        video_filename = video_url.split('/')[-1]
        save_path = os.path.join('下载的视频(cctv)', video_filename)  # 创建一个下载目录
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    else:
        return

def merge_video_ts_files(output_filename, folder_path):
    output_path = os.path.join(folder_path, output_filename)
    with open(output_path, 'wb') as output_file:
        # 逐个打开每个ts文件并写入输出文件
        for i in range(36):  # 假设n是100
            ts_filename = os.path.join(folder_path, f'{i}.ts')
            try:
                with open(ts_filename, 'rb') as ts_file:
                    output_file.write(ts_file.read())
                # 删除已合并的ts文件
                os.remove(ts_filename)
            except FileNotFoundError:
                return

def main():
    service = Service(executable_path="msedgedriver.exe")
    driver = webdriver.Edge(service=service)
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76",

    }

    mode = int(input('输入id请按1，输入搜索词检索按0: '))
    if mode == 1:
        video_id = input('请输入视频ID（例如：VIDE7rA4vlEcTwrP3D2gkVd8240411）：')
        year = input('视频年份（查看ID后六位）：')
        month = input('视频月份（如果是1-9月则输入01-09）：')
        day = input('视频日期（如果是1-9月则输入01-09）：')
        url = f"https://v.cctv.com/{year}/{month}/{day}/{video_id}.shtml"
        driver.get(url)
        html_content = driver.page_source #动态网页的html，有点赞数
        resp = requests.get(url=url, headers=header)
        extract_video_url(html_content)
        guid_data = guid.findall(resp.text)[0]
        html_content = f"https://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid={guid_data}"
        resq = requests.get(url=html_content, headers=header)
        m3u8_data = m3u8.findall(resq.text)[0]
        resp = requests.get(url=m3u8_data, headers=header)
        re = resp.text
        f_data = front.findall(m3u8_data)[0]
        ts_data = ts.findall(re)[0]
        for i in range(0,35):
            video_url = 'https:' + str(f_data) + '/' + str(ts_data) + str(i) + '.ts'
            download_video(video_url)
        input_directory = '下载的视频(cctv)'
        filename = str(title) + '.mp4'
        merge_video_ts_files(filename,input_directory)
        print(title, '视频下载完成')
    else:
        search_word = input('请输入搜索词：')
        html_content = f'https://v.cctv.com/sousuo/index.shtml?title={search_word}'
        driver.get(html_content)
        input()#这里多等一会，央视的加载很慢
        search_content = driver.page_source
        box = search_video_url(search_content)
        for i in range (1,11):
            video_id = str(box[i])
            video_id = video_id.replace("[", "").replace("]", "").replace("'","")
            driver.get(video_id)
            html_content = driver.page_source  # 动态网页的html，有点赞数
            resp = requests.get(url=video_id, headers=header)
            extract_video_url(html_content)
            guid_data = guid.findall(resp.text)[0]
            html_content = f"https://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid={guid_data}"
            resq = requests.get(url=html_content, headers=header)
            m3u8_data = m3u8.findall(resq.text)[0]
            resp = requests.get(url=m3u8_data, headers=header)
            re = resp.text
            f_data = front.findall(m3u8_data)[0]
            ts_data = ts.findall(re)[0]
            for i in range(0, 35):
                video_url = 'https:' + str(f_data) + '/' + str(ts_data) + str(i) + '.ts'
                download_video(video_url)
            input_directory = '下载的视频(cctv)'
            filename = str(title) + '.mp4'
            merge_video_ts_files(filename, input_directory)
            print(title, '视频下载完成')
    # 关闭浏览器
    driver.quit()

if __name__ == '__main__':
    main()





