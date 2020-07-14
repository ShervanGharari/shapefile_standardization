#!/cvmfs/soft.computecanada.ca/easybuild/software/2017/Core/python/3.7.4/bin/python

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import requests
import re


# destination to saev files
des_loc = "/project/6008034/Model_Output/ClimateForcingData/MERIT_Hydro_basin_bugfixed/"
# page that the link to files are located
http_page = "XXX/XXXbugfix1/pfaf_level_02/" # replace XXX and should not be distributed publicly


# first get all the links in the page
req = Request(http_page)
html_page = urlopen(req)
soup = BeautifulSoup(html_page, "lxml")
links = []
for link in soup.findAll('a'):
    links.append(link.get('href'))
#print(links)

# specify the link to be downloaded
link_to_download = []
for link in links:
    if "cat_pfaf_" in link and "Basins" in link: # links that have cat_pfaf and Basins in them
        link_to_download.append(link)
        print(link)
#print(link_to_download)

# creat urls to download
urls =[]
for file_name in link_to_download:
    urls.append(http_page+file_name) # link of the page + file names
    print(http_page+file_name)
print(urls)
    
# loop to download the data
for url in urls:
    name = url.split('/')[-1] # get the name of the zip file at the end of the url to download
    r = requests.get(url) # download the URL
    # print the specification of the download 
    print(r.status_code, r.headers['content-type'], r.encoding)
    # if download successful the statuse code is 200 then save the file, else print what was not downloaded
    if r.status_code == 200:
        print('download was successful for '+url)
        with open(des_loc+name, 'wb') as f:
            f.write(r.content)
    else:
        print('download was not successful for '+url)
