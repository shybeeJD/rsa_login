from .get_prime import get_prime
import random

#欧几里得除法
def exEuclid(a,b):
	x0=1
	y0=0
	x1=0
	y1=1
	r=a%b
	q=int((a-r)/b)
	while(r>0):
		x = x0 - q * x1
		y = y0 - q * y1
		x0 = x1
		y0 = y1
		x1 = x
		y1 = y
		a = b
		b = r
		r = a % b
		q = int(( a - r ) / b)
	return b,x,y

#求逆元
def inv(a,p):
	r,x,y=exEuclid(a,p)
	if r!=1:
		return 0
	x=x%p
	if x<0:
		x=x+p
	return x

#加解密函数
def modd(b,index,m):
	binary=bin(index).replace('0b','')
	b2=1
	a=1
	for i in range(0,len(binary)):
		a=pow(b,int(binary[i]))*b2
		a=a%m
		b2=a*a%m
	return a


#生成RSA公私钥
def get_rsa_pair(key_siez=1024):
	p=get_prime(key_siez)
	q=get_prime(key_siez)
	n=p*q
	fain=(p-1)*(q-1)
	while True:
		d = random.randrange(2, fain-1)
		r,x,y=exEuclid(d,fain)
		if r==1:
			break
	e=inv(d,fain)
	return n,e,d


#十六进制字符串转ASCII码，转码时使用
def hex2asc(a):
	a=hex(a).replace('0x','')
	s=''
	for i in range(0,len(a)-1,2):
		num=int(a[i],base=16)*16+int(a[i+1],base=16)
		s=s+chr(num)
	return s



