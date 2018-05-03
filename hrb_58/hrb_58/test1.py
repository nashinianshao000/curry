import cx_Oracle as oracle
conn = oracle.connect('gxd/gxd1528!1528@221.208.141.164:1528/xscj')
cursor = conn.cursor()

#声明变量
user = 'Nick' #plsql入参
msg = cursor.var(oracle.STRING) #plsql出参
#调用存储过程
cursor.callproc('t_esf_58_guocheng', [user, msg]) #['Nick', 'Nick, Good Morning!']
#打印返回值
print(msg) #<cx_Oracle.STRING with value 'Nick, Good Morning!'>
print(msg.getvalue()) #Nick, Good Morning!
#资源关闭
cursor.close()
conn.close()