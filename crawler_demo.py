from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# from bs4 import BeautifulSoup as bs 
from pathlib import Path 
from PIL import Image 
from io import BytesIO

import requests
import sys
import time
# import pandas as pd, numpy as np 
import os

class CrawlerBot():
	def __init__(self):
		# manger = ChromeDriverManager().install()
		# self.driver = webdriver.Chrome(manger)

		self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())		
		self.link = 'https://xembao.vn'
		self.home_page_path = str(Path.home())
		self.driver.get(self.link)

	# get all papers links
	def get_all_links(self):
		list_products = self.driver.find_element_by_id("ctl00_dListProducts")
		paper_href_elements = list_products.find_elements_by_tag_name("a")
		# Test only
		# links = [href_element.get_attribute("href")for href_element in paper_href_elements[:1]]
		
		links = [href_element.get_attribute("href") for href_element in paper_href_elements]
		dict_paper_link = dict()
		# for href_element in paper_href_elements[:1]:
		for href_element in paper_href_elements:
			paper_title = href_element.get_attribute('innerHTML').split("<br>")[-1].strip().replace(' ','_').replace('/','-') 
			paper_link = href_element.get_attribute("href")
			dict_paper_link[paper_title] = paper_link

		return dict_paper_link

	# each paper, we scroll down to get publications
	def load_all_publications(self, link_paper='https://vietnam.xembao.vn'):
		self.driver.get(link_paper)

		script_load_all = '''
		window.scrollTo(0, document.body.scrollHeight);
	 	$("#btnContinue").click();
		'''

		# Test only
		script_load_all = '''
		window.scrollTo(0, document.body.scrollHeight);
		'''

		last_height = self.driver.execute_script("return document.body.scrollHeight")
		while True:
			self.driver.execute_script(script_load_all)
			time.sleep(0.5)
			new_height = self.driver.execute_script("return document.body.scrollHeight")

			if new_height == last_height:
				break
			last_height = new_height

	# get publication links
	def get_all_publications(self):
		list_content = self.driver.find_element_by_id("listContent")
		list_href = list_content.find_elements_by_tag_name("a")
		list_publications = list_content.find_elements_by_class_name("blockTitle")

		links = [href.get_attribute("href") for href in list_href]
		publications = [publication.get_attribute("innerHTML").strip().replace(' ','_').replace('/','-') for publication in list_publications]
		# Test
		# links = [href.get_attribute("href") for href in list_href[:1]]
		publications_dict = dict()
		publications_dict = {key: value for key, value in zip(publications, links)}
		
		return publications_dict

	def save_publication_source(self, publication_folder, img_links, publication):
		imgs_list = []
		for img_url in img_links[:10]:
			response = requests.get(img_url)
			img = Image.open(BytesIO(response.content))
			imgs_list.append(img)

			img_name = img_url.split('/')[-1]
			img_path = os.path.join(publication_folder, 'input-pages', img_name)
			img.save(img_path)
		# Save all to 1 pdf file
		pdf_filename_path = os.path.join(publication_folder, f'{publication}.pdf')
		print(f'Saving pdf files with {len(imgs_list)} pages. This may take a while')
		imgs_list[0].save(pdf_filename_path, "PDF", resolution=100.0, save_all=True, append_images=imgs_list[1:])

	def crawl(self):
		self.links_paper = self.get_all_links()
		Path(self.home_page_path + '/data').mkdir(parents=True, exist_ok=True)

		# Handle each paper
		for title, link in self.links_paper.items():
			title_folder = f'{self.home_page_path}/data/{title}'
			print(f'Save {title_folder}')
			Path(title_folder).mkdir(parents=True, exist_ok=True)
			# Go to that paper link, get all publications
			self.load_all_publications(link_paper=link)

			self.publications_data = []
			publications_dict = self.get_all_publications()
			self.publications_data.append(publications_dict)
			# Handle each publication of that
			for publication, publication_link in publications_dict.items():
				publication_folder = f'{self.home_page_path}/data/{title}/{publication}'
				Path(publication_folder).mkdir(parents=True, exist_ok=True)
				Path(publication_folder + '/input-pages').mkdir(parents=True, exist_ok=True)
				Path(publication_folder + '/output-texts').mkdir(parents=True, exist_ok=True)

				print(f'Save {publication_folder}')

				self.driver.get(publication_link)
				time.sleep(5)
				
				# Find images
				list_imgs = self.driver.find_element_by_xpath("/html/body/div[21]/div[2]/div/ul")
				list_imgs_href = list_imgs.find_elements_by_tag_name("img")
				img_links = [link.get_attribute("src").replace('thumbs', 'large') for link in list_imgs_href]

				# Save all
				self.save_publication_source(publication_folder, img_links, publication)
				break
			print('-------------')
			break
		return img_links

bot = CrawlerBot()
img_links = bot.crawl()
# bot.driver.get(img_links[0])

# browser.quit()
# sys.exit()
	