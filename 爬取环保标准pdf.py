from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import json
import re
import requests
import os
import lxml
import urllib.request

# 确定root，从标准文本的首页开始工作。
root = 'http://kjs.mee.gov.cn/hjbhbz/bzwb/'
# 1 标定分类，确定每个分类的列表，例如水、气标准中的内容；
website = requests.get(root).text
soup = BeautifulSoup(website)
url_list = []
stop = 0
# 爬取网站中侧栏的标题，并且将标题中的内容贴到root的后面，形成新的网址；
for link in soup.find_all('a'):             
    ful_list = link.get("href")
    if ful_list is None or len(ful_list) > 12 or len(ful_list) < 5 or "../" in ful_list:
        pass
    else:
        url_list.append(ful_list)
lst_data =[]
finf = './(.*?)/'
for sample in url_list:
    u = re.compile(finf).findall(sample)
    lst_data.append(u[0])
# 列表lst_data中就是形成的标签；

# 2 爬去分类下各个页面下page中的url；
def find_url(soup,lst):
    for link in soup.find_all('a'):
        fullurl = link.get('href')
        if fullurl is None or len(fullurl) <=20 or 'http' in fullurl or 'https' in fullurl:
            pass
        else:
            lst.append(fullurl)
    return lst
# 定义函数，查找href的网址内容；
# 确定了每一个类别标签之后，可以进行页面url的重新组合，并且形成网址，打开之后逐页进行打开并读取网址中的地址，
url_final = []
for lst in lst_data:
    urls = []
    root_first_url = root + lst
    first_site = requests.get(root_first_url).text
    soup_first = BeautifulSoup(first_site)
    urls = find_url(soup_first,urls)
    for i in range(2,20):
        root_second_url = root_first_url + '/index_' + str(i) + '.shtml'   # 每个类别不超过20页，可以可以进行逐页的读取，逐页组成网址；
        root_second_site = requests.get(root_second_url).text
        root_second_soup = BeautifulSoup(root_second_site)
        if root_second_soup.find_all('Not Found') is True:
            pass
        else:
            urls = find_url(root_second_soup,urls)
    for samples in urls:
        if '../' in samples:
            x = samples.replace('../','')
            final = root_first_url + '/' + x
            url_final.append(final)
        elif './' in samples:
            y = samples.replace('./','')
            final = root_first_url + '/' + y
            url_final.append(final)
        else:
            pass 
# 形成网址链接的数据库，然后对每页中的pdf链接进行读取；

# 3 解析url 读取pdf链接，并将title 读取，并行组成以url 为key，标题为value的字典；
pdfs = {}
for pdf in url_final:
    second_site = requests.get(pdf).text
    soup_second = BeautifulSoup(second_site)
    for luck in soup_second.find_all('a'):
        fullurl_pdf = luck.get('href')
        if fullurl_pdf is None:
            pass
        elif fullurl_pdf.endswith('.pdf'):
            if "./" in fullurl_pdf:
                xx = fullurl_pdf.replace('./','')
                dd =  '(.*?)/t.'
                ddd = re.compile(dd).findall(pdf)
                dddd = ddd[0]
                final_pdf = dddd + '/' + xx
                z = '<p>(.*?)</p>'
                got_title = requests.get(pdf).content.decode("utf-8")
                title = re.compile(z).findall(got_title)[0]
                pdfs.setdefault(title,final_pdf)
# 形成pdf的链接的汇总；可以对列别中的内容进行逐页的下载；

# 4 将组成的pdf url逐个下载到本地文件夹，并用value进行命名；
def getpdf(folder_path, lists):
    if not os.path.exists(folder_path):
        print("Selected folder not exist, try to create it.")
        os.makedirs(folder_path)
    for title,url in lists.items():
        print("Try downloading file: {}".format(title))
        filename = title
        filepath = folder_path + '/' + filename + '.pdf'
        if os.path.exists(filepath):
            print("File have already exist. skip")
        else:
            try:
                urllib.request.urlretrieve(url, filename=filepath)
            except Exception as e:
                print("Error occurred when downloading file, error message:")
                print(e)

getpdf('F:\\1',pdfs)
# 后期可以修正为class的函数定义