# Data Collection
To collect data, we are going to use Selenium to do web-scaping.

## Selenium
### Install and import
```py
pip install selenium
```
Once installed, it is ready for the imports:
```py
from selenium import webdriver
```
### Install and access web driver
A webdriver is a vital ingredient to this process. It is what will actually be automatically opening up your browser to access your website of choice. Selenium supports Chrome, Internet Explorer, Firefox, Safari, and Opera. We are going to use Chrome. It can be downloaded [here](https://chromedriver.chromium.org/downloads). For convenience, `chromedriver.exe` is included in this repository. 

### Access Website Via Python
```py
driver = webdriver.Chrome(service=Service("chromedriver.exe"))
driver.get("website-url")
```

## Enable Long Paths in Windows 10, Version 1607, and Later
To avoid erros when saving files with long names, `Computer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled (Type: REG_DWORD)` must exist and be set to 1.

## Parliament debates
Singapore parliament debates and speeches have been made available [here](https://sprs.parl.gov.sg/search/home). The reports date as far back as 1955. Our searching criteria are:
* 1st parliament to 14th parliament
* All categories except "Administrations of Oaths", "Attendance", and "Permission To Members To Be Absent"

A typical report can be found [here](https://sprs.parl.gov.sg/search/topic?reportid=010_19910729_S0006_T0031). It contains information about the report (its parliament, date, section, etc), a title and speeches.

For each report, we do the following:
1. Remove irrelevent texts and mark texts if they indicate speakers' names. This can be done by executing some javascript commands to that report directly in Chrome. Selenium allows us to do so via its interface `execute_script`. 
2. Save its title, date and speeches in a json format in `.\parliament`.
3. Record its date, title, url and path in a SQLite database, `.\parliament.db`.

### Usage
```py
python paliament.py -p <parliament number>
```
`-p`: the parliament that will be scraped. It is an integer from 1 to 14.

Using different values of `-p` for many parallel processes allows us to shorten the amount of time needed to scrape all reports.

## Nexis
Online database of international news and business reports. It allows users to search and download up to 500 articles at one time. We are interested in Singapore news published by The Straits Times and Channel News Asia. To scrape this database, it is good to use Exeter VPN to access. 

Note that Nexis allows us to download up to 30000 documents for any search result.

### Usage
```py
python nexis.py -s <start day> -e <end day> -n <starting article number>
```
`-s`: the start day on which Nexis starts searching
`-e`: the end day on which Nexis stops searching, inclusive
`-n`: the article number from which many batches of 500 articles are downloaded, default to 1

## The Independent
> The Independent Singapore brings independent perspective on news and current affairs in Singapore. It is a platform owned and operated by journalists. Started on the 9th of August 2013, the news website brings in-depth perspective and analysis on current affairs, economics and politics in Singapore. 

Fortunately, [articles](https://theindependent.sg/news/singapore-news/) are organized in such a way that it is convenient to scrape. 

### Enable Ad-block
The website contains many ads. To remove them, we need to enable the extension Ad-block. This is done by installing the extension and save it to a profile.

Perform the following steps:
1. Run this script to open a new Chrome window
```py
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument('user-data-dir=<path to profile folder>')

driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=chrome_options)
sleep(30) # to have time to install the plug-in
```
2. Install Ad-block in the Chrome

Similar to Parliament, for each report, we do the following:
1. Remove irrelevent texts. 
2. Save its title, date and speeches in a json format in `.\theindependent`.
3. Record its date, title, url and path in a SQLite database, `.\theindependent.db`.

### Usage
```py
python theindependent.py -f <start page> -t <end page>
```
`-f`: the page number that scraping starts

`-t`: the page number that scraping ends, inclusive.


## New Naratif
> New Naratif is an online journalism platform and independent media outlet that publishes content on Southeast Asian current affairs

We are interested in articles related to Singapore. They can be found [here](https://newnaratif.com/?s=Singapore). 

Many articles are podcasts. They are downloaded and transcribed by using `speech2text`.

### Usage
```py
python newnaratif.py -f <start page> -t <end page> -p <url>
```
`-f`: the page number that scraping starts.

`-t`: the page number that scraping ends, inclusive.

`-p`: the page url that is scraped. If this is specified, `-f` and `-t` are ignored.

Similar to Parliament, for each article, we do the following:
1. Remove irrelevent texts. 
2. Save its title, date and speeches in a json format in `.\newnaratif`.
3. Record its date, title, url and path in a SQLite database, `.\newnaratif.db`.

## TR Emeritus
> TR Emeritus (TRE, formerly Temasek Review Emeritus) is a socio-political blog and one of the alternative media that emerged in Singapore in the 2000s.

Articles are organized in categories: "Chinese", "Columnists", "Editorial", "Elections", "Letters", "Opinion", "Snippets", and "Sports". We are NOT interested in "Chinese" and "Sports".

Another thing to note is that the website limits access to articles that are 3 months and older for members only. The cost of membership is S$10/month.

### Usage
```py
python tremeritus.py -f <start page> -t <end page> -c <category>
```
`-f`: the page number that scraping starts.

`-t`: the page number that scraping ends, inclusive.

`-c`: the category that will be scraped.

Similar to Parliament, for each article, we do the following:
1. Remove irrelevent texts. 
2. Save its title, date and speeches in a json format in `.\tremeritus`.
3. Record its date, title, url and path in a SQLite database, `.\tremeritus.db`.

## TodayOnline
> TODAY is a Singapore English-language digital news provider under Mediacorp, Singapore's largest media broadcaster and provider and the only terrestrial television broadcaster in the country
Although TodayOnline has a search function, it only allows us to browse up to 67 pages of results which include articles of up to about 2 months old.
Therefore, we are going to use Google to search for articles' URLs. After that, we are going to scrape each URL. We are interested in 2 sections, "Commentary" and "Big Read" in 10 years, from 2012-02-01 to 2022-02-01.

Steps to use Google to search for articles:
1. Go to "News" when searching for "Singapore site:www.todayonline.com/commentary" or "Singapore site:www.todayonline.com/big-read"
2. Use "Tools" to set date range. Because Google only returns about 300 hits per search, we are going to divide 10-years period into many sub-periods of 7-days.
3. Save the urls of each hit.

Note that it is unavoidable that Google occasionally asks for Captcha, so it is necessary to monitor the process. Fortunately, it should not take too much time.

### Usage
```py
python todayonline.py -s <start url> -e <end url>
```
`-s`: the index in `todayonline_links.txt` that scraping starts.

`-e`: the index in `todayonline_links.txt` that scraping ends, inclusive.