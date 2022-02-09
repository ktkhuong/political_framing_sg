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

A report generally looks like this:
<iframe src="https://sprs.parl.gov.sg/search/topic?reportid=010_19910729_S0006_T0031"></iframe>

It contains information about the report (its parliament, date, section, etc), a title and speeches.

For each report, we do the following:
1. Remove irrelevent texts and mark texts if they indicates speakers' names. This can be done by executing some javascript commands to that report directly in Chrome. Selenium allows us to do so via its interface `execute_script`. 
2. Save its title, date and speeches in a json format in `.\parliament`.
3. Record its date, title, url and path in a SQLite database, `.\parliament.db`.

### Usage
```py
python paliament.py -p <parliament number>
```
`-p`: the parliament that will be scraped. It is an integer from 1 to 14.

Using different values of `-p` for many parallel processes allows us to shorten the amount of time needed to scrape all reports.

## The Independent
> The Independent Singapore brings independent perspective on news and current affairs in Singapore. It is a platform owned and operated by journalists. Started on the 9th of August 2013, the news website brings in-depth perspective and analysis on current affairs, economics and politics in Singapore.

Fortunately, [articles](https://theindependent.sg/news/singapore-news/) are organized in such a way that it is convenient to scrape. 

### Usage
```py
python theindependent.py -f <start page> -t <end page>
```
`-f`: the page number that scraping starts
`-t`: the page number that scraping ends, inclusive.

## New Naratif
> New Naratif is an online journalism platform and independent media outlet that publishes content on Southeast Asian current affairs

We are interested in articles related to Singapore. They can be found [here](https://newnaratif.com/?s=Singapore). 

Many articles are in the form of podcast. They are downloaded and transcribed by using `speech2text`.

### Usage
```py
python newnaratif.py -f <start page> -t <end page> -p <url>
```
`-f`: the page number that scraping starts.
`-t`: the page number that scraping ends, inclusive.
`-p`: the page url that is scraped. If this is specified, `-f` and `-t` are ignored.