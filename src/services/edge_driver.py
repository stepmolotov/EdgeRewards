from injector import inject
from selenium import webdriver
from selenium.webdriver.edge.webdriver import WebDriver

@inject
class EdgeDriver(WebDriver):

    def __init__(self) -> None:
        self.super().__init__()
        self.__driver = webdriver.Edge(options=self.__options)