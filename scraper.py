import csv, datetime
from time import sleep, time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as E
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from pathlib import Path

# chrome driver

options = webdriver.ChromeOptions()                                     # this is for removing
options.add_experimental_option('excludeSwitches', ['enable-logging'])  # the windows10 error
driver = webdriver.Chrome(options=options)

# variables & initialisation

startTime = time() # starting time of the scraping
currentPageNum = 1 # current page number
baseDir = Path(__file__).resolve(strict=True).parent # path to the base directory where the output will be saved

# naming the output file

outputTimestamp = datetime.datetime.now().strftime("%Y%m%d%H%M") # year/month/date/hour/minute 
outputFilename = f"output_{outputTimestamp}.csv"

# connecting to the website

def connectWebsite(driver, pageNumber):
    if pageNumber == 1:
        pageNumber = ""
    site_url = f"https://www.gadgetsnow.com/latest-news/{pageNumber}"
    attempts = 0
    while attempts < 3:
        try:
            driver.get(site_url)

            WebDriverWait(driver, 3).until(
                E.presence_of_element_located((By.CLASS_NAME, "w_tle"))
            )
            return True
        except Exception as e:
            print(e)
            attempts += 1
            print(f"Error connecting to {site_url}.")
            print(f"Attempt {attempts}.")
    return False

# parsing data from html page

def parse_html(html):
    # create soup object
    soup = BeautifulSoup(html, "html.parser")
    outputList = []
    # parse soup object to get article id, rank, score, and title
    spanBlocks = soup.find_all("span", class_="w_tle")
    article = 0
    for span in spanBlocks:
        articleText = span.find("a")["title"]
        articleUrl = span.find("a")["href"]
        words = ['apple', 'Apple', 'APPLE']

        # check if article is an apple article
        if any(x in articleText for x in words) :
            articleUrl = f"https://gadgetsnow.com/{articleUrl}"

            articleInfo = {
                "heading": articleText,
                "url": articleUrl,
            }

            # appends article_info to output_list
            outputList.append(articleInfo)
        else:
            article += 1
    return outputList

# writing to the output file

def writeFile(outputList, filename):
    for row in outputList:
        with open(Path(baseDir).joinpath(filename), "a") as csvfile:
            fieldnames = ["heading", "url"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(row)

# main process

def runProcess(pageNumber, filename, driver):

    if connectWebsite(driver, pageNumber):
        sleep(2)
        html = driver.page_source
        outputList = parse_html(html)

        writeFile(outputList, filename)
    else:
        print("Error connecting to gadgets now!")

# scraping

while currentPageNum <= 10:

    print(f"---Currently Scraping Page {currentPageNum}---")
    runProcess(currentPageNum, outputFilename, driver)
    currentPageNum += 1

# end

driver.quit()
endTime = time()
elapsedTime = round((endTime - startTime), 2) # round off upto 2 decimal digits
print(f"Total time elapsed: {elapsedTime} seconds")
