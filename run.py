import os
import requests
from bs4 import BeautifulSoup
import re
from time import sleep
import json

class Tool_backup():
	if not os.path.exists('OUTPUT'): os.mkdir('OUTPUT')
	if not os.path.exists('JSON'): os.mkdir('JSON')
	def __init__(self):
		self.ses = requests.session()
		self.path_file_image = None
		self.path_file_output = None
		self.cout_all = None

	def save_file_json(self, path_input, data):
		f = open(path_input, 'w', encoding='utf8')
		json.dump(data, f, ensure_ascii=False, indent=4)
		f.close()

	def load_file_json(self, path_input):
		f = open(path_input, 'r', encoding='utf8')
		data = json.load(f)
		f.close()
		return data

	def get_headers(self, cookie):
		headers_fb = {
			'authority': 'mbasic.facebook.com',
			'upgrade-insecure-requests': '1',
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'sec-fetch-site': 'same-origin',
			'sec-fetch-mode': 'navigate',
			'accept-language': 'en-US,en;q=0.9',
			'user_agent': 'Mozilla/5.0 (Linux; Android) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36',
			'cookie': cookie
		}
		return headers_fb

	def get_token(self, cookie):
		headers = self.get_headers(cookie)
		url = 'https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed'
		res = self.ses.get(url, headers=headers)
		token = re.findall(r'accessToken\\":\\"(.*?)\\', res.text)
		if token != []: token = token[0]
		else: token = ''
		return token

	def get_list_friends(self, token):
		params = {'access_token': token}
		url = 'https://graph.facebook.com/me?fields=friends'
		res = self.ses.get(url, params=params)
		data = res.json()
		list_friends = data['friends']['data']
		return list_friends

	def get_list_id_albums(self, token, fbid):
		list_id_albums = []
		params = {'access_token': token}
		url = f'https://graph.facebook.com/{fbid}?fields=albums'
		res = requests.get(url, params=params)
		data = res.json()
		data = data['albums']['data']
		for album in data:
			list_id_albums.append(album['id'])
		return list_id_albums

	def get_list_url_images(self, token, name, list_id_albums):
		images = {}
		try:
			images[name] = []
			params = {'access_token': token}
			for id_album in list_id_albums:
				url = f'https://graph.facebook.com/{id_album}/photos'
				res = requests.get(url, params=params)
				data = res.json()
				data = data['data']
				for i in data:
					images[name].append(i['source'])
		except:
			images = {}
		if images != {}:
			list_images = self.load_file_json(self.path_file_image)
			list_images.append(images)
			self.save_file_json(self.path_file_image, list_images)
			

	def backup(self):
		open(self.path_file_output, 'w').close()
		list_images = self.load_file_json(self.path_file_image)
		for images in list_images:
			for name in images:
				with open(self.path_file_output, 'a', encoding='utf8') as f:
					f.write(f'<h1>{name}</h1>')
					for url in images[name]:
						f.write(f'<img src="{url}"/>')
					f.close()

	def run(self):
		cookie = input('Cookie: ')
		token = self.get_token(cookie)
		if token=="":
			print("Cookie die!!!")
			return 0
		list_friends = self.get_list_friends(token)
		sl = len(list_friends)
		print(f"Friends: {sl}")

		st = int(input("from: "))
		en = int(input("to: "))
		self.path_file_image = f'JSON/image_{st}_{en}.json'
		self.path_file_output = f'OUTPUT/finish_{st}_{en}.html'
		self.cout_all = st - 1
		print("START")
		open(self.path_file_image, 'w').write('[]')
		for x in range(st-1,en):
			name = list_friends[x]['name']
			fbid = list_friends[x]['id']
			list_id_albums = self.get_list_id_albums(token, fbid)
			self.get_list_url_images(token, name, list_id_albums)
			self.cout_all += 1
			print(f"{self.cout_all}|{name}")
		print('XONG!!!')

if __name__ == '__main__':
	tool = Tool_backup()
	tool.run()
	tool.backup()