import re
tm = '04-30'
s = re.findall('\d\d-\d\d',tm)[0]
print(s)
if tm == s:
    fbtime = '2018-' + tm + ' 00:00:00'
print(fbtime)