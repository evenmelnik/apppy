from urllib import request
import json
import time
import sqlite3
from datetime import datetime, timedelta

key = ''
apiurl = ""



def datatim(datastart, dataend):  # 'https://api.e-autopay.com/v02/0b3bbfde-5c87-4c22-aa49-a2e580abd5db/orders/2018-03-01..2018-03-27?{"customer_api_key":"58fd6252-3dda-41fc-adcd-ccde6b3d7a1c"}' 
	k = '{"customer_api_key":"' + key + '"}'  #оборачивает ключ в http запрос
	api = apiurl.format(datastart, dataend, k) #форматируем строку запроса по датам
	try:
		jsonotvet = request.urlopen(api)
		jsonotvet = jsonotvet.read()
		json_read = json.loads(jsonotvet)
		return json_read["orders"]
	except:
		return False
	
def datainjson(result):
	
	datainApi = []
	for i in range(len(result)):
		status = result[i]['status']
		order_id = result[i]['order_id']
		amount = result[i]['credentials']['amount']
		created = result[i]['credentials']['created']
		if result[i]['credentials']['utm'] != []:
			try:
				utm_source = result[i]['credentials']['utm']['utm_source']
			except:
				utm_source = 'None'
			try:
				utm_medium = result[i]['credentials']['utm']['utm_medium']
			except:
				utm_medium = 'None'
			try:
				utm_campaign = result[i]['credentials']['utm']['utm_campaign']
			except:
				utm_campaign = 'None'
			try:
				utm_content = result[i]['credentials']['utm']['utm_content']
			except:
				utm_content = 'None'
			try:
				utm_term = result[i]['credentials']['utm']['utm_term']
			except:
				utm_term = 'None'
		else:
			utm_source = 'None'
			utm_medium = 'None'
			utm_campaign = 'None'
			utm_content = 'None'
			utm_term = 'None'
			
		order_res = (
		created, 
		order_id, 
		status, 
		amount, 
		utm_source, 
		utm_medium, 
		utm_campaign, 
		utm_content, 
		utm_term
		)
		
		
	
		anlitic(datainApi, order_res)
	
	return datainApi


def anlitic(listing, order_res):
	
	conn = sqlite3.connect("dataisapi.db", check_same_thread = False, timeout=30000) # или :memory: чтобы сохранить в RAM
	cursor = conn.cursor()
	try:
		cursor.execute("""CREATE TABLE bdorder (
		created text, 
		order_id text, 
		status text, 
		amount text, 
		utm_source text, 
		utm_medium text, 
		utm_campaign text, 
		utm_content text, 
		utm_term text
		)""")
		print('БД создана')
	except:
		print('БД ok')
	sql = "SELECT * FROM bdorder WHERE order_id=?"
	cursor.execute(sql, [(order_res[1])])
	otvet = cursor.fetchall()
	if otvet != []:
		
		if int(otvet[0][1]) == order_res[1]:
			#listing.append(order_res)
			print('Элемент есть в бд: {}'.format(order_res[1]))
			if otvet[0][2] != order_res[2]:
				sql = "UPDATE bdorder SET status = ? WHERE order_id = ?"
				cursor.execute(sql, [order_res[2], otvet[0][1]])
				print('Заказ {} обновлен на статус: {}'.format(order_res[1], order_res[2]))
				
				
	
	elif otvet == []:
		print(otvet)
		listing.append(order_res)
		print('Элемент не найден, делаю запись')
	
	conn.commit()

def bdappend(data):
	conn = sqlite3.connect("dataisapi.db", check_same_thread = False, timeout=30000) # или :memory: чтобы сохранить в RAM
	cursor = conn.cursor()
	try:
		cursor.execute("""CREATE TABLE bdorder (
		created text, 
		order_id text, 
		status text, 
		amount text, 
		utm_source text, 
		utm_medium text, 
		utm_campaign text, 
		utm_content text, 
		utm_term text
		)""")
		print('БД создана')
	except:
		pass
		
	

	sql = """INSERT INTO bdorder VALUES (?,?,?,?,?,?,?,?,?)"""
	cursor.executemany(sql, data)
	conn.commit()
	conn.close()
	return True

def bdwhat(string):
	conn = sqlite3.connect("dataisapi.db", check_same_thread = False, timeout=30000) # или :memory: чтобы сохранить в RAM
	cursor = conn.cursor()
	sql = "SELECT * FROM bdorder WHERE created LIKE ?"
	cursor.execute(sql, [('%' + string + '%')])
	what = cursor.fetchall() # or use fetchone()
	conn.close()
	return what


	

# ---- main ----
start_time = time.time()

start = datetime(2018, 2, 16) 
end = start + timedelta(days = 30)


data = True

while data:
	startstr = datetime.strftime(start, "%Y-%m-%d")
	endstr = datetime.strftime(end, "%Y-%m-%d")
	print('{}..{}'.format(startstr, endstr))
	
	result = datatim(startstr, endstr) #получаем данные за обьявленный период
	
	if end >= datetime.today():
		end = datetime.today()
		
	start = start + timedelta(days = 30)
	end = end + timedelta(days = 30)
	
	if result == False:
		continue
		
	h = datainjson(result)
	bdappend(h)
	if end >= datetime.today():
		break
	
	print('Количество полученных заказов от автопей: {}'.format(len(result)))
	print('Количество полученных заказов: ' + str(len(h)))
	print('Количество в БД: {}'.format(len(bdwhat('1'))))


print(len(bdwhat('0')))


	

	

print("--- %s seconds ---" % (time.time() - start_time))



