import asyncio
from contextlib import contextmanager

from requests_html import HTMLSession, AsyncHTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@contextmanager
def chromedriver():
    options = Options()
    options.headless = True
    # TODO: Improve this
    driver = webdriver.Chrome(executable_path="chromedriver.exe", chrome_options=options)
    yield driver
    driver.quit()


@contextmanager
def dynamic_requests_session(async_session: bool = False):
    session = AsyncHTMLSession() if async_session else HTMLSession()
    yield session
    if async_session:
        asyncio.run(session.close())
    else:
        session.close()

