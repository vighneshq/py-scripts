import os, bs4, requests, sys 

if __name__ == "__main__":

	url = "https://www.smbc-comics.com/"

	#Create a separate folder for all the images, if one does not exist already.
	if os.path.isdir(os.path.join(os.getcwd(),"smbc")) == False: 
		os.mkdir("smbc")	
	
	os.chdir("smbc")
	print(os.getcwd())
	
	while(True):

		while(True):
			try:
				res = requests.get(url)
				res.raise_for_status()
				break
			except KeyboardInterrupt:
				sys.exit(0)
			except:
				pass
				
		#Get the source for the comic using Beautiful Soup
		soup = bs4.BeautifulSoup(res.text, "html.parser")
		image = soup.select('img[id="cc-comic"]')[0]
		comic = image.get('src')
		
		try:
			res = requests.get("https://www.smbc-comics.com"+comic)
			res.raise_for_status()
			file = open(comic[9:], "wb")
			print("Downloading comic... " + comic)
			for chunk in res.iter_content(100000):
				file.write(chunk)		
			file.close()
		except KeyboardInterrupt:
			sys.exit(0)
		except:
			pass
	
		prev = soup.select('a[class="prev"]')	
		if prev == []:
			print("Done printing.")
			sys.exit(0)
		url = prev[0].get('href')