from flask import Markup
from flask import Flask
from flask import render_template, request, url_for, redirect


from collections import defaultdict
import sqlite3
import pandas as pd
import json

def pandDB(h, res):
	cols = [column[0] for column in h.description]
	results= pd.DataFrame.from_records(data = res, columns = cols, index = 'order_id')
	return results

def ordWhat(start):
	conn = sqlite3.connect('dataisapi.db')
	#conn.row_factory = dict_factory
	cursor = conn.cursor()
	what = "SELECT * FROM bdorder WHERE created LIKE ?"  # utm_source=? AND
	h = cursor.execute(what, ([start + '%'])) 
	res = cursor.fetchall() 
	res = pandDB(h, res)
	conn.close()
	return res
	


def pandaJson(res):
	#res = ordWhat('2018-05-01', '2018-05-02')
	res['amount'] = res['amount'].apply(pd.to_numeric)
	res['zak'] = 1
	notgood = ["new", "specified", "delayed", "unconfirmed", "refused", "problem", "absence"]
	res.status.replace(notgood, [0 for i in range(len(notgood))], inplace=True)
	good = ["archive", "in_hands_paid", "in_hands_unpaid", "notice1", "notice2" , "pending" , "confirmed", "sent", "cancelled", "delivered_unpaid", "complectation", "ready_for_delivery", "wanted", "returned"]
	res.status.replace(good, [1 for i in range(len(good))], inplace=True)
	res.loc[res['status'] == 0, 'amount'] = 0
	
	grouped = res.groupby(['utm_source', 'utm_campaign', 'utm_content']).sum()
	
	results = defaultdict(lambda: defaultdict(dict))
	for index, goodzak, amout, zak in grouped.itertuples():
		for i, key in enumerate(index):
			if i == 0:
				nested = results[key]
				
				
			elif i == len(index) - 1:
				nested[key] = {
				'amout' :int(amout), 
				'zak': int(zak), 
				'goodzak': int(goodzak),
				}
			else:
				nested = nested[key]
				
	jsons = json.dumps(results, indent=4)
	return jsons
	
def obrab(res):
	res['amount'] = res['amount'].apply(pd.to_numeric)
	res['zak'] = 1
	notgood = ["new", "specified", "delayed", "unconfirmed", "refused", "problem", "absence"]
	res.status.replace(notgood, [0 for i in range(len(notgood))], inplace=True)
	good = ["archive", "in_hands_paid", "in_hands_unpaid", "notice1", "notice2" , "pending" , "confirmed", "sent", "cancelled", "delivered_unpaid", "complectation", "ready_for_delivery", "wanted", "returned"]
	res.status.replace(good, [1 for i in range(len(good))], inplace=True)
	res.loc[res['status'] == 0, 'amount'] = 0
	
	return res 	




#==== main =====                                                                   



app = Flask(__name__)



@app.route('/', methods = ['GET', 'POST'])
def dalta():
	if request.method == 'POST': 
		data = request.form['data']
		res = ordWhat(data)
		res = obrab(res)
		#res = res.loc[res['utm_source'] == 'mytarget_muslim22'] 
		grouped = res.groupby(['utm_campaign']).sum()
		datas = grouped.to_json(orient='table')
		
		return render_template('ind.html', data=datas)
	
	datas = 'nan'
	return render_template('ind.html', data=datas)
		
@app.route('/comp', methods = ['GET', 'POST'])
def dal():
	if request.method == 'POST': 
		data = request.form['data1']
		comp = request.form['comp']
		res = ordWhat(data)
		res = obrab(res)
		res = res.loc[res['utm_campaign'] == comp] 
		grouped = res.groupby(['utm_campaign']).sum()
		datas = grouped.to_json(orient='table')
		
		return render_template('ind.html', data=datas)
	
	datas = 'nan'
	return render_template('ind.html', data1=datas)

	
		

app.run(host= '192.168.0.100', port=80, debug=False)
