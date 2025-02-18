import os
import time
import pandas as pd
from glob import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


SOURCE_URL = "https://www3.dmsc.moph.go.th/"


def main():

    # Options for Chrome WebDriver
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"

    op = Options()
    op.add_argument("--disable-notifications")
    op.add_experimental_option("prefs",{
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True 
    })

    with webdriver.Chrome(desired_capabilities=caps, options=op) as driver:

        # Setting Chrome to trust downloads
        driver.command_executor._commands["send_command"] = ("POST", "/session/$sessionId/chromium/send_command")
        params = {"cmd": "Page.setDownloadBehavior", "params": {"behavior": "allow", "downloadPath": "tmp"}}
        command_result = driver.execute("send_command", params)

        driver.get(SOURCE_URL)
        time.sleep(5)
        links = driver.find_elements_by_css_selector(".app-body .bg-white .container center a")
        for link in links:
            if "Raw Data" in link.text:
                nextcloud = link.get_attribute("href")
                break
        driver.get(nextcloud)
        time.sleep(5)
        driver.find_element_by_css_selector(".directDownload a").click()
        time.sleep(2)

    file = glob("tmp/Thailand*")[0]
    df = pd.read_excel(file)
    df.loc[:, "Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df[["Date", "Total"]].dropna()
    df = df[df["Total"] > 0]
    df = df.rename(columns={"Total": "Daily change in cumulative total"})

    df.loc[:, "Daily change in cumulative total"] = df["Daily change in cumulative total"].astype(int)
    df.loc[:, "Country"] = "Thailand"
    df.loc[:, "Source URL"] = SOURCE_URL
    df.loc[:, "Source label"] = "Ministry of Public Health"
    df.loc[:, "Units"] = "tests performed"
    df.loc[:, "Notes"] = pd.NA

    df.to_csv("automated_sheets/Thailand.csv", index=False)
    os.remove(file)


if __name__ == '__main__':
    main()
