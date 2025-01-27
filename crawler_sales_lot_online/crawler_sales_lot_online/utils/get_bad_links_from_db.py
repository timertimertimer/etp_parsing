# import mysql.connector
# from icecream import ic
#
# # data for collaborate with database
# connect_db = {
#     'host': 'localhost',
#     'user':
#     'passwd':
#     'database':
#     'lots_lot_online': 'lots_lot_online'}
#
# TABLE = connect_db['lots_lot_online']
# DATABASE = connect_db['database']
#
# host = connect_db['host']
# user = connect_db['user']
# passwd = connect_db['passwd']
#
# mydb = mysql.connector.connect(
#     host=host,
#     user=user,
#     passwd=passwd,
#     database=DATABASE)
#
# mycursor = mydb.cursor()
# mycursor.execute(
#     "select trading_link from lots_lot_online where status='ended' or status='pending' and created_at > '2021-01-01 14:20:00' order by created_at desc")
# myresult = mycursor.fetchall()
# main_list = list()
#
# for l in myresult:
#     with open('links.txt', 'a+') as f:
#         f.write(str(l[0]))
#         f.write('\n')
#
# with open('links.txt', 'r') as f:
#     result = f.readlines()
#     for r in result:
#         main_list.append(r.rstrip('\n'))
# ic(len(myresult))
# ic(main_list)
