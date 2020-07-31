from django.shortcuts import redirect
from django.shortcuts import render
from .models import Products
import datetime
import requests
import hashlib
import telebot
import sqlite3
import json

# Create your views here.

bot = telebot.TeleBot('1180532717:AAHWoW2YBILbypSelntjDOzLX2ph3NRNRMQ')

def main_page(request):

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

	if x_forwarded_for:

		ip = x_forwarded_for.split(',')[-1].strip()

	else:

		ip = request.META.get('REMOTE_ADDR')

	conn = sqlite3.connect("mydb.sqlite3")

	cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

	if len(cursor.fetchall()) == 0:

		new_user = [('{}'.format(ip), ',', ',', ',', 0, False, False, 0, 0, None, None)]

		cursor.executemany("INSERT INTO Users VALUES (?,?,?,?,?,?,?,?,?,?,?)", new_user)

		conn.commit()
		conn.close()

	conn = sqlite3.connect("mydb.sqlite3")

	cursor = conn.cursor()

	cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

	user = cursor.fetchall()

	user = user[0]

	order_price = user[4]
	delivery = user[5]

	if len(user[7]) > 10:

		url = 'https://securepay.tinkoff.ru/v2/GetState'

		data = {
			"TerminalKey":'1595793366396DEMO',
			"PaymentId":user[6],
			"Token":user[7],
		}


		responce = requests.post(url, json = data)

		data = json.loads(responce.content.decode('utf-8'))

		if str(data['Status']) == "CONFIRMED":

			sql = """
			UPDATE Users
			SET delivery = '{}'
			WHERE ip_user = '{}'
			""".format(True, ip)

			cursor.execute(sql)
			conn.commit()

			new_line = ','

			sql = """
			UPDATE Users
			SET user_order = '{}'
			WHERE ip_user = '{}'
			""".format(new_line, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET count_product = '{}'
			WHERE ip_user = '{}'
			""".format(new_line, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET price = '{}'
			WHERE ip_user = '{}'
			""".format(new_line, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET order_price = '{}'
			WHERE ip_user = '{}'
			""".format('0', ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET paymentid = '{}'
			WHERE ip_user = '{}'
			""".format(False, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET token = '{}'
			WHERE ip_user = '{}'
			""".format('0', ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET created_order = '{}'
			WHERE ip_user = '{}'
			""".format('0', ip)

			cursor.execute(sql)
			conn.commit()


			now_time = datetime.datetime.now()

			start_day = now_time.day
			start_hour = now_time.hour
			start_minute = now_time.minute

			start_time = str(start_hour) + ':' + str(start_minute)

			end_day = 0
			end_hour = 0
			end_minute = 0

			if int(now_time.minute) + 40 >= 60:

				if start_hour + 1 != 25:
					
					end_day = start_day
					end_hour = start_hour + 1
					end_minute = int(now_time.minute) + 40 - 60

				elif start_hour + 1 == 24:
					
					end_day = start_day + 1
					end_hour = 0
					end_minute = int(now_time.minute) + 40 - 60

			else:

				end_day = start_day
				end_hour = start_hour
				end_minute = int(now_time.minute) + 40

			create_time = '{}:{}:{}'.format(start_day, start_hour, start_minute)
			end_time = '{}:{}:{}'.format(end_day, end_hour, end_minute)


			sql = """
			UPDATE Users
			SET create_time = '{}'
			WHERE ip_user = '{}'
			""".format(create_time, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET end_time = '{}'
			WHERE ip_user = '{}'
			""".format(end_time, ip)

			cursor.execute(sql)
			conn.commit()


			bot.send_message(
				921930444,
				user[8],
				parse_mode='html'
			)

			conn.close()

	conn = sqlite3.connect("mydb.sqlite3")

	cursor = conn.cursor()

	cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

	user = cursor.fetchall()

	user = user[0]

	timeout = 0

	if user[5] == 'True':

		time_now = datetime.datetime.now()

		day_now = time_now.day
		hour_now = time_now.hour
		minute_now = time_now.minute

		end_time = user[10].split(':')

		day_end = end_time[0]
		hour_end = end_time[1]
		minute_end = end_time[2]

		if int(day_now) == int(day_end):

			if int(hour_now) == int(hour_end):

				timeout = int(minute_end) - int(minute_now)

			else:

				timeout = int(minute_end) - int(minute_now) + 60

		else:

			timeout = 60 - int(minute_now) + int(minute_end)

		if timeout <= 0:

			conn = sqlite3.connect("mydb.sqlite3")

			cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

			cursor = conn.cursor()

			user = cursor.fetchall()

			sql = """
			UPDATE Users
			SET delivery = '{}'
			WHERE ip_user = '{}'
			""".format(False, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET create_time = '{}'
			WHERE ip_user = '{}'
			""".format(0, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET end_time = '{}'
			WHERE ip_user = '{}'
			""".format(0, ip)

			cursor.execute(sql)
			conn.commit()

			conn.close()

	return render(request, 'shop/main_page.html', {'order_price':order_price, 'delivery':delivery, 'timeout':timeout})

def menu(request):

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

	if x_forwarded_for:

		ip = x_forwarded_for.split(',')[-1].strip()

	else:

		ip = request.META.get('REMOTE_ADDR')

	conn = sqlite3.connect("mydb.sqlite3")

	cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

	user = cursor.fetchall()

	user = user[0]

	product_list = user[1].split(',')
	len_product_list = len(product_list) - 1
	count_product = user[2].split(',')
	prices = user[3].split(',')
	order_price = user[4]


	class Product():

		def __init__(self, name, count, price):

			self.name = name
			self.count = count
			self.price = price

	products_list = []

	for i in range(len_product_list):

		a = Product(product_list[i], count_product[i], prices[i])

		products_list.append(a)

	product_list = Products.objects.all()


	indicator = [True]

	def check():

		if indicator[0] == False:

			del indicator[0]
			indicator.append(True)

			return True

		elif indicator[0] == True:

			del indicator[0]
			indicator.append(False)

			return False
			

	return render(request, 'shop/menu.html', {'product_list':product_list, 'products_list':products_list, 'order_price':order_price, 'indicator':indicator, 'check':check})

def send(request):

	response = request.GET

	date = response['time']
	address = response['address']
	office = response['extra-flat']
	intercom = response['extra-domofon']
	entrance = response['extra-pod']
	floor = response['extra-floor']
	comment = response['comment']

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

	if x_forwarded_for:

		ip = x_forwarded_for.split(',')[-1].strip()

	else:

		ip = request.META.get('REMOTE_ADDR')

	conn = sqlite3.connect("mydb.sqlite3")

	cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

	user = cursor.fetchall()

	user = user[0]

	order_price = user[4]

	product_list = user[1].split(',')

	if '' in product_list:

		product_list.remove('')

	count_product_list = user[2].split(',')

	if '' in count_product_list:

		count_product_list.remove('')

	order = ''

	for i in range(len(product_list)):

		order += f'{product_list[i]} - {count_product_list[i]}\n'

	

	created_order = f'Заказ:\n{order}\nИнформация о заказе:\nВремя доставки - {date}\nАдрес доставки - {address}\nКв/Офис - {office}\nДомофон - {intercom}\nПодъезд - {entrance}\nЭтаж - {floor}\nКоментарий - {comment}'

	print(created_order)

	sql = """
	UPDATE Users
	SET created_order = '{}'
	WHERE ip_user = '{}'
	""".format(created_order, ip)

	cursor.execute(sql)
	conn.commit()

	url = 'https://securepay.tinkoff.ru/v2/Init'


	conn_2 = sqlite3.connect("mydb.sqlite3")

	cursor_2 = conn_2.cursor()
	
	cursor_2.execute("SELECT * FROM Configs WHERE call_me=?", (1,))

	user = cursor_2.fetchall()

	user = user[0]


	data = {
		"TerminalKey": "1595793366396DEMO",
		"Amount": "{}".format(order_price * 100),
		"OrderId": "{}".format(user[0]),
		"Description": "Заказ еды",
		"DATA": {
			"Phone": "+71234567890",
			"Email": "a@test.com"
		},
		"Receipt": {
			"Email": "a@test.ru",
			"Phone": "+79031234567",
			"Taxation": "osn",
			"Items": [
				{
					"Name": "Еда",
					"Price": order_price * 100,
					"Quantity": 1.00,
					"Amount": order_price * 100,
					"Tax": "vat0",
					"Ean13": "0123456789"
				}
			]
		}
	}

	sql = """
	UPDATE Configs
	SET order_id = '{}'
	WHERE call_me = '{}'
	""".format(user[0] + 1, 1)

	cursor_2.execute(sql)
	conn_2.commit()

	conn_2.close()


	responce = requests.post(url, json = data)
	responce = responce.content

	dict_responce = json.loads(responce.decode('utf-8'))

	sql = """
	UPDATE Users
	SET paymentid = '{}'
	WHERE ip_user = '{}'
	""".format(dict_responce["PaymentId"], ip)

	cursor.execute(sql)
	conn.commit()

	text = 'eej2noa87wqmh0uv' + str(dict_responce['PaymentId']) + str(dict_responce['TerminalKey'])

	hashvalue=hashlib.sha256(text.encode('utf-8'))
	token = hashvalue.hexdigest()

	sql = """
	UPDATE Users
	SET token = '{}'
	WHERE ip_user = '{}'
	""".format(token, ip)

	cursor.execute(sql)
	conn.commit()

	redirect_url = dict_responce['PaymentURL']

	return redirect(redirect_url)

def basket_del(request, name):

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

	if x_forwarded_for:

		ip = x_forwarded_for.split(',')[-1].strip()

	else:

		ip = request.META.get('REMOTE_ADDR')

	products_list = Products.objects.all()

	product_name = None
	product_price = None

	for product in products_list:

		if product.name == name:

			product_name = product.name
			product_price = product.price

	conn = sqlite3.connect("mydb.sqlite3")

	cursor = conn.cursor()

	cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

	user = cursor.fetchall()

	user = user[0] 

	product_list = user[1].split(',')
	count_product = user[2].split(',')
	prices = user[3].split(',')
	order_price = user[4]

	count = 0
	for i in range(len(product_list)):
		if product_list[i] == name:
			count = i
			break

	product_list.remove(product_name)
	del product_list[-1]

	new_product_list = ','.join(product_list)
	new_product_list += ','

	count_del_product = int(count_product[count])

	del count_product[count]
	del count_product[-1]

	new_count_product = ','.join(count_product)
	new_count_product += ','

	order_price = order_price - (product_price * count_del_product)

	del prices[-1]
	del prices[count]

	new_prices = ','.join(prices)
	new_prices += ','

	sql = """
	UPDATE Users
	SET price = '{}'
	WHERE ip_user = '{}'
	""".format(new_prices, ip)

	cursor.execute(sql)
	conn.commit()

	sql = """
	UPDATE Users
	SET order_price = '{}'
	WHERE ip_user = '{}'
	""".format(order_price, ip)

	cursor.execute(sql)
	conn.commit()


	sql = """
	UPDATE Users
	SET count_product = '{}'
	WHERE ip_user = '{}'
	""".format(new_count_product, ip)

	cursor.execute(sql)
	conn.commit()


	sql = """
	UPDATE Users
	SET user_order = '{}'
	WHERE ip_user = '{}'
	""".format(new_product_list, ip)

	cursor.execute(sql)
	conn.commit()

	conn.close()

	return redirect('/basket/')

def basket(request):

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

	if x_forwarded_for:

		ip = x_forwarded_for.split(',')[-1].strip()

	else:

		ip = request.META.get('REMOTE_ADDR')

	conn = sqlite3.connect("mydb.sqlite3")

	cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

	user = cursor.fetchall()

	user = user[0]

	product_list = user[1].split(',')
	len_product_list = len(product_list) - 1
	count_product = user[2].split(',')
	prices = user[3].split(',')
	order_price = user[4]


	class Product():

		def __init__(self, name, count, price):

			self.name = name
			self.count = count
			self.price = price

	products_list = []

	for i in range(len_product_list):

		a = Product(product_list[i], count_product[i], prices[i])

		products_list.append(a)
	
	produc_list = Products.objects.all()

	indicator = False

	for product in produc_list:

		if product.name in product_list:

			indicator = True
			break



	return render(request, 'shop/basket.html', {'products_list':products_list, 'order_price':order_price, 'indicator':indicator})

def mapp(request):

	a = request.GET
	b = request.POST

	print('\n\n\n\n\nAAAAAA - ', a, '\n\n\n\n\n')
	print('\n\n\n\n\nBBBBBB - ', b, '\n\n\n\n\n')



	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

	if x_forwarded_for:

		ip = x_forwarded_for.split(',')[-1].strip()

	else:

		ip = request.META.get('REMOTE_ADDR')

	url = 'https://geocode-maps.yandex.ru/1.x/?apikey=4406b995-547e-479c-b157-f0afdc59b812&geocode=Тула+Белкина+6&format=json'

	a = requests.get(url)


	text = a.content.decode('utf-8')

	html = json.loads(text)

	positions = html['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']

	positions_list = positions.split()

	latitude = positions_list[1]
	longitude = positions_list[0]

	return render(request, 'shop/map.html', {'latitude':latitude, 'longitude':longitude})

def beverages(request):

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

	if x_forwarded_for:

		ip = x_forwarded_for.split(',')[-1].strip()

	else:

		ip = request.META.get('REMOTE_ADDR')

	conn = sqlite3.connect("mydb.sqlite3")

	cursor = conn.cursor()

	cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

	user = cursor.fetchall()

	user = user[0]

	product_list = user[1].split(',')
	len_product_list = len(product_list) - 1
	count_product = user[2].split(',')
	prices = user[3].split(',')
	order_price = user[4]

	class Product():

		def __init__(self, name, count, price):

			self.name = name
			self.count = count
			self.price = price

	products_list = []

	for i in range(len_product_list):

		a = Product(product_list[i], count_product[i], prices[i])

		products_list.append(a)

	product_list = Products.objects.all()


	indicator = [True]

	def check():

		if indicator[0] == False:

			del indicator[0]
			indicator.append(True)

			return True

		elif indicator[0] == True:

			del indicator[0]
			indicator.append(False)

			return False

	return render(request, 'shop/beverages.html', {'product_list':product_list, 'products_list':products_list, 'order_price':order_price, 'indicator':indicator, 'check':check})

def fruits(request):

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

	if x_forwarded_for:

		ip = x_forwarded_for.split(',')[-1].strip()

	else:

		ip = request.META.get('REMOTE_ADDR')

	conn = sqlite3.connect("mydb.sqlite3")

	cursor = conn.cursor()

	cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

	user = cursor.fetchall()

	user = user[0]

	product_list = user[1].split(',')
	len_product_list = len(product_list) - 1
	count_product = user[2].split(',')
	prices = user[3].split(',')
	order_price = user[4]

	class Product():

		def __init__(self, name, count, price):

			self.name = name
			self.count = count
			self.price = price

	products_list = []

	for i in range(len_product_list):

		a = Product(product_list[i], count_product[i], prices[i])

		products_list.append(a)

	product_list = Products.objects.all()


	indicator = [True]

	def check():

		if indicator[0] == False:

			del indicator[0]
			indicator.append(True)

			return True

		elif indicator[0] == True:

			del indicator[0]
			indicator.append(False)

			return False

	return render(request,  'shop/fruits.html', {'product_list':product_list, 'products_list':products_list, 'order_price':order_price, 'indicator':indicator, 'check':check})

def minus(request, name):

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

	if x_forwarded_for:

		ip = x_forwarded_for.split(',')[-1].strip()

	else:

		ip = request.META.get('REMOTE_ADDR')

	products_list = Products.objects.all()

	product_name = None
	product_price = None

	for product in products_list:

		if product.name == name:

			product_name = product.name
			product_price = product.price

	conn = sqlite3.connect("mydb.sqlite3")

	cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

	user = cursor.fetchall()

	user = user[0] 

	product_list = user[1].split(',')
	count_product = user[2].split(',')
	prices = user[3].split(',')
	order_price = user[4]

	if product_name in product_list:
		count = 0
		for i in range(len(product_list)):
			if product_list[i] == name:
				count = i
				break

		if int(count_product[count]) == 1:

			product_list.remove(product_name)
			del prices[count]
			del prices[-1]
			del product_list[-1]
			del count_product[count]
			del count_product[-1]

			new_product_list = ','.join(product_list)
			new_product_list += ','

			new_count_product = ','.join(count_product)
			new_count_product += ','

			order_price = int(order_price) - int(product_price)

			new_prices = ','.join(prices)
			new_prices += ','

			sql = """
			UPDATE Users
			SET user_order = '{}'
			WHERE ip_user = '{}'
			""".format(new_product_list, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET count_product = '{}'
			WHERE ip_user = '{}'
			""".format(new_count_product, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET order_price = '{}'
			WHERE ip_user = '{}'
			""".format(order_price, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET price = '{}'
			WHERE ip_user = '{}'
			""".format(new_prices, ip)

			cursor.execute(sql)
			conn.commit()

			conn.close()

		elif int(count_product[count]) > 1:

			del count_product[-1]

			count_product[count] = str(int(count_product[count]) - 1)

			new_count_product = ','.join(count_product)
			new_count_product += ','

			order_price = int(order_price) - int(product_price)

			sql = """
			UPDATE Users
			SET count_product = '{}'
			WHERE ip_user = '{}'
			""".format(new_count_product, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET order_price = '{}'
			WHERE ip_user = '{}'
			""".format(order_price, ip)

			cursor.execute(sql)
			conn.commit()

			conn.close()


	return redirect('/menu/')

def plus(request, name):

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

	if x_forwarded_for:

		ip = x_forwarded_for.split(',')[-1].strip()

	else:

		ip = request.META.get('REMOTE_ADDR')

	products_list = Products.objects.all()

	product_name = None
	product_price = None

	for product in products_list:

		if product.name == name:

			product_name = product.name
			product_price = product.price

	conn = sqlite3.connect("mydb.sqlite3")

	cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

	user = cursor.fetchall()

	user = user[0] 

	product_list = user[1].split(',')
	count_product = user[2].split(',')
	prices = user[3].split(',')
	order_price = user[4]

	if name not in product_list:

		del prices[-1]

		if '' in product_list:

			product_list.remove('')

		if '' in count_product:

			count_product.remove('')

		if '' in prices:

			prices.remove('')

		prices.append(str(product_price))

		new_prices = ','.join(prices)
		new_prices += ','

		sql = """
		UPDATE Users
		SET price = '{}'
		WHERE ip_user = '{}'
		""".format(new_prices, ip)

		cursor.execute(sql)
		conn.commit()

		product_list.append(product_name)

		if '' in product_list:

			product_list.remove('')

		new_product_list = ','.join(product_list)
		new_product_list += ','

		sql = """
		UPDATE Users
		SET user_order = '{}'
		WHERE ip_user = '{}'
		""".format(new_product_list, ip)

		print(sql)

		cursor.execute(sql)
		conn.commit()

		order_price = int(order_price) + int(product_price)

		sql = """
		UPDATE Users
		SET order_price = '{}'
		WHERE ip_user = '{}'
		""".format(order_price, ip)

		cursor.execute(sql)
		conn.commit()

		count_product.append('1')

		if '' in count_product:

			count_product.remove('')

		new_count_product = ','.join(count_product)
		new_count_product += ','

		sql = """
		UPDATE Users
		SET count_product = '{}'
		WHERE ip_user = '{}'
		""".format(new_count_product, ip)

		cursor.execute(sql)
		conn.commit()

		conn.close()

	elif name in product_list:

		del count_product[-1]

		count = 0
		for i in range(len(product_list)):
			if product_list[i] == name:
				count = i
				break

		print('\n\n\n\n', count_product, '\n\n\n\n')

		count_product[count] = str(int(count_product[count]) + 1)

		print('\n\n\n\n', count_product, '\n\n\n\n')

		new_count_product = ','.join(count_product)
		new_count_product += ','

		sql = """
		UPDATE Users
		SET count_product = '{}'
		WHERE ip_user = '{}'
		""".format(new_count_product, ip)

		cursor.execute(sql)
		conn.commit()


		order_price = int(order_price) + int(product_price)

		sql = """
		UPDATE Users
		SET order_price = '{}'
		WHERE ip_user = '{}'
		""".format(order_price, ip)

		cursor.execute(sql)
		conn.commit()


		conn.close()

	return redirect('/menu/')

def fruits_minus(request, name):

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

	if x_forwarded_for:

		ip = x_forwarded_for.split(',')[-1].strip()

	else:

		ip = request.META.get('REMOTE_ADDR')

	products_list = Products.objects.all()

	product_name = None
	product_price = None

	for product in products_list:

		if product.name == name:

			product_name = product.name
			product_price = product.price

	conn = sqlite3.connect("mydb.sqlite3")

	cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

	user = cursor.fetchall()

	user = user[0] 

	product_list = user[1].split(',')
	count_product = user[2].split(',')
	prices = user[3].split(',')
	order_price = user[4]

	if product_name in product_list:
		count = 0
		for i in range(len(product_list)):
			if product_list[i] == name:
				count = i
				break

		if int(count_product[count]) == 1:

			product_list.remove(product_name)
			del prices[-1]
			del prices[count]
			del product_list[-1]
			del count_product[-1]
			del count_product[count]

			new_product_list = ','.join(product_list)
			new_product_list += ','

			new_count_product = ','.join(count_product)
			new_count_product += ','

			order_price = int(order_price) - int(product_price)

			new_prices = ','.join(prices)
			new_prices += ','

			sql = """
			UPDATE Users
			SET user_order = '{}'
			WHERE ip_user = '{}'
			""".format(new_product_list, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET count_product = '{}'
			WHERE ip_user = '{}'
			""".format(new_count_product, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET order_price = '{}'
			WHERE ip_user = '{}'
			""".format(order_price, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET price = '{}'
			WHERE ip_user = '{}'
			""".format(new_prices, ip)

			cursor.execute(sql)
			conn.commit()

			conn.close()

		elif int(count_product[count]) > 1:

			del count_product[-1]

			count_product[count] = str(int(count_product[count]) - 1)

			new_count_product = ','.join(count_product)
			new_count_product += ','

			order_price = int(order_price) - int(product_price)

			sql = """
			UPDATE Users
			SET count_product = '{}'
			WHERE ip_user = '{}'
			""".format(new_count_product, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET order_price = '{}'
			WHERE ip_user = '{}'
			""".format(order_price, ip)

			cursor.execute(sql)
			conn.commit()

			conn.close()


	return redirect('/fruits/')

def fruits_plus(request, name):

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

	if x_forwarded_for:

		ip = x_forwarded_for.split(',')[-1].strip()

	else:

		ip = request.META.get('REMOTE_ADDR')

	products_list = Products.objects.all()

	product_name = None
	product_price = None

	for product in products_list:

		if product.name == name:

			product_name = product.name
			product_price = product.price

	conn = sqlite3.connect("mydb.sqlite3")

	cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

	user = cursor.fetchall()

	user = user[0] 

	product_list = user[1].split(',')
	count_product = user[2].split(',')
	prices = user[3].split(',')
	order_price = user[4]

	if name not in product_list:

		if '' in product_list:

			product_list.remove('')

		if '' in count_product:

			count_product.remove('')

		if '' in prices:

			prices.remove('')

		prices.append(str(product_price))

		new_prices = ','.join(prices)
		new_prices += ','

		sql = """
		UPDATE Users
		SET price = '{}'
		WHERE ip_user = '{}'
		""".format(new_prices, ip)

		cursor.execute(sql)
		conn.commit()

		product_list.append(product_name)

		new_product_list = ','.join(product_list)
		new_product_list += ','

		sql = """
		UPDATE Users
		SET user_order = '{}'
		WHERE ip_user = '{}'
		""".format(new_product_list, ip)

		print(sql)

		cursor.execute(sql)
		conn.commit()

		order_price = int(order_price) + int(product_price)

		sql = """
		UPDATE Users
		SET order_price = '{}'
		WHERE ip_user = '{}'
		""".format(order_price, ip)

		cursor.execute(sql)
		conn.commit()

		count_product.append('1')

		new_count_product = ','.join(count_product)
		new_count_product += ','

		sql = """
		UPDATE Users
		SET count_product = '{}'
		WHERE ip_user = '{}'
		""".format(new_count_product, ip)

		cursor.execute(sql)
		conn.commit()

		conn.close()

	elif name in product_list:

		del count_product[-1]

		count = 0
		for i in range(len(product_list)):
			if product_list[i] == name:
				count = i
				break

		print('\n\n\n\n', count_product, '\n\n\n\n')

		count_product[count] = str(int(count_product[count]) + 1)

		print('\n\n\n\n', count_product, '\n\n\n\n')

		new_count_product = ','.join(count_product)
		new_count_product += ','

		sql = """
		UPDATE Users
		SET count_product = '{}'
		WHERE ip_user = '{}'
		""".format(new_count_product, ip)

		cursor.execute(sql)
		conn.commit()


		order_price = int(order_price) + int(product_price)

		sql = """
		UPDATE Users
		SET order_price = '{}'
		WHERE ip_user = '{}'
		""".format(order_price, ip)

		cursor.execute(sql)
		conn.commit()


		conn.close()

	return redirect('/fruits/')

def beverages_minus(request, name):

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

	if x_forwarded_for:

		ip = x_forwarded_for.split(',')[-1].strip()

	else:

		ip = request.META.get('REMOTE_ADDR')

	products_list = Products.objects.all()

	product_name = None
	product_price = None

	for product in products_list:

		if product.name == name:

			product_name = product.name
			product_price = product.price

	conn = sqlite3.connect("mydb.sqlite3")

	cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

	user = cursor.fetchall()

	user = user[0] 

	product_list = user[1].split(',')
	count_product = user[2].split(',')
	prices = user[3].split(',')
	order_price = user[4]

	if product_name in product_list:
		count = 0
		for i in range(len(product_list)):
			if product_list[i] == name:
				count = i
				break

		if int(count_product[count]) == 1:

			product_list.remove(product_name)
			del prices[-1]
			del prices[count]
			del product_list[-1]
			del count_product[-1]
			del count_product[count]

			new_product_list = ','.join(product_list)
			new_product_list += ','

			new_count_product = ','.join(count_product)
			new_count_product += ','

			order_price = int(order_price) - int(product_price)

			new_prices = ','.join(prices)
			new_prices += ','

			sql = """
			UPDATE Users
			SET user_order = '{}'
			WHERE ip_user = '{}'
			""".format(new_product_list, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET count_product = '{}'
			WHERE ip_user = '{}'
			""".format(new_count_product, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET order_price = '{}'
			WHERE ip_user = '{}'
			""".format(order_price, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET price = '{}'
			WHERE ip_user = '{}'
			""".format(new_prices, ip)

			cursor.execute(sql)
			conn.commit()

			conn.close()

		elif int(count_product[count]) > 1:

			del count_product[-1]

			count_product[count] = str(int(count_product[count]) - 1)

			new_count_product = ','.join(count_product)
			new_count_product += ','

			order_price = int(order_price) - int(product_price)

			sql = """
			UPDATE Users
			SET count_product = '{}'
			WHERE ip_user = '{}'
			""".format(new_count_product, ip)

			cursor.execute(sql)
			conn.commit()

			sql = """
			UPDATE Users
			SET order_price = '{}'
			WHERE ip_user = '{}'
			""".format(order_price, ip)

			cursor.execute(sql)
			conn.commit()

			conn.close()


	return redirect('/beverages/')

def beverages_plus(request, name):

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

	if x_forwarded_for:

		ip = x_forwarded_for.split(',')[-1].strip()

	else:

		ip = request.META.get('REMOTE_ADDR')

	products_list = Products.objects.all()

	product_name = None
	product_price = None

	for product in products_list:

		if product.name == name:

			product_name = product.name
			product_price = product.price

	conn = sqlite3.connect("mydb.sqlite3")

	cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM Users WHERE ip_user=?", (ip,))

	user = cursor.fetchall()

	user = user[0] 

	product_list = user[1].split(',')
	count_product = user[2].split(',')
	prices = user[3].split(',')
	order_price = user[4]

	if name not in product_list:

		if '' in product_list:

			product_list.remove('')

		if '' in count_product:

			count_product.remove('')

		if '' in prices:

			prices.remove('')

		prices.append(str(product_price))

		new_prices = ','.join(prices)
		new_prices += ','

		sql = """
		UPDATE Users
		SET price = '{}'
		WHERE ip_user = '{}'
		""".format(new_prices, ip)

		cursor.execute(sql)
		conn.commit()

		product_list.append(product_name)

		new_product_list = ','.join(product_list)
		new_product_list += ','

		sql = """
		UPDATE Users
		SET user_order = '{}'
		WHERE ip_user = '{}'
		""".format(new_product_list, ip)

		print(sql)

		cursor.execute(sql)
		conn.commit()

		order_price = int(order_price) + int(product_price)

		sql = """
		UPDATE Users
		SET order_price = '{}'
		WHERE ip_user = '{}'
		""".format(order_price, ip)

		cursor.execute(sql)
		conn.commit()

		count_product.append('1')

		new_count_product = ','.join(count_product)
		new_count_product += ','

		sql = """
		UPDATE Users
		SET count_product = '{}'
		WHERE ip_user = '{}'
		""".format(new_count_product, ip)

		cursor.execute(sql)
		conn.commit()

		conn.close()

	elif name in product_list:

		del count_product[-1]

		count = 0
		for i in range(len(product_list)):
			if product_list[i] == name:
				count = i
				break

		print('\n\n\n\n', count_product, '\n\n\n\n')

		count_product[count] = str(int(count_product[count]) + 1)

		print('\n\n\n\n', count_product, '\n\n\n\n')

		new_count_product = ','.join(count_product)
		new_count_product += ','

		sql = """
		UPDATE Users
		SET count_product = '{}'
		WHERE ip_user = '{}'
		""".format(new_count_product, ip)

		cursor.execute(sql)
		conn.commit()


		order_price = int(order_price) + int(product_price)

		sql = """
		UPDATE Users
		SET order_price = '{}'
		WHERE ip_user = '{}'
		""".format(order_price, ip)

		cursor.execute(sql)
		conn.commit()


		conn.close()

	return redirect('/beverages/')

def redirect_whatsapp(request):

	return redirect('https://wa.me/79992181876?text=Здравствуйте!%20У%20меня%20возник%20вопрос%20по%20поводу%20сайта.')
