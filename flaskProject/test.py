import re
s = "hello, wo.rld. this, is yufeng chen he is  a fucking genious"
print(re.findall(r'\w+', s))