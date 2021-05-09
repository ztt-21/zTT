from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class FPSDriver:
	def __init__(self, driver_path):
		self.options=Options()
#		self.options.add_argument('--headless')
#		self.options.add_argument('--disable-gpu')
		self.options.add_argument('--no-sandbox')
		self.options.add_argument('--disable-dev-shm-usage')
#		self.options.add_argument('--remote-debugging-port=9222')

		self.driver_path = driver_path
		self.driver = webdriver.Chrome(self.driver_path, options=self.options)

	
	def open_page(self, url):
		self.driver.get(url)
	
	def get_fps(self):
		fps_box = self.driver.find_element(By.ID, "fps")
		return fps_box.text

