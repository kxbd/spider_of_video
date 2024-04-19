from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import requests
from lxml import etree
import os



def extract_video_url(html_content):
    tree = etree.HTML(html_content)
    video_url = tree.xpath('//video/@src')
    title = tree.xpath('//h2[@class="header_title__vP_8V"]/text()')
    likes = tree.xpath('//div[@class="praiseNum index_num__lvDnF"]/text()')
    introduction = tree.xpath('//p[@class="header_desc__OlmEB"]/text()')
    print('标题：',title)
    print('简介：',introduction)
    print('点赞数',likes)
    if video_url:
        return video_url[0]
    else:
        return None

def download_video(video_url):
    response = requests.get(video_url, stream=True, verify=False)
    if response.status_code == 200:
        # 从URL中提取视频文件名
        video_filename = video_url.split('/')[-1]
        save_path = os.path.join('下载的视频(the_paper)', video_filename)  # 创建一个下载目录
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

    wait = WebDriverWait(driver, 100)


    video_id = input('请输入视频ID（例如：27026484）：')
    driver.get(f"https://www.thepaper.cn/newsDetail_forward_{video_id}")
    #搜索100条不一定有一个视频
    wait = WebDriverWait(driver, 15)
    input()
    html_content= driver.page_source
    video_src_url= extract_video_url(html_content)
    if video_src_url:
        download_video(video_src_url)
        print(video_src_url)
    else:
        print('无法找到视频链接')

    # 关闭浏览器
    driver.quit()

if __name__ == '__main__':
    main()





