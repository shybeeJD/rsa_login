
from __future__ import unicode_literals
from django.shortcuts import render, redirect,HttpResponse
from .forms import UserForm, RegisterForm
from login import models
import time
from django.db import transaction
import hashlib
import base64
import time
from .RSA import get_rsa_pair,modd,hex2asc
import json

# Create your views here.
def login(request):
    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']#获得用户名
            password = login_form.cleaned_data['password']#获得密文
            #使用base64解码并使用（n，d）对解码后的密文进行解密
            password=modd(int(base64.b64decode(password).decode()),int(request.session['d']),int(request.session['n']))
            #获得解密后口令哈希值的十六进制字符串
            password=hex(password).replace('0x','')
            print('口令哈希值：',end='')
            print(password)
            #password=hex2asc(password)
            try:
                user = models.User.objects.get(name=username)
                if request.session.get('is_login', None):
                    r = redirect('/index/')
                    r.set_cookie('username', username, max_age=1000)
                    return r
                if user.password == password:

                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    r=redirect('/index/')
                    r.set_cookie('username', username, max_age=1000)
                    return r
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"

        login_form = UserForm()
        n, e, d = get_rsa_pair(256)  # 生成公私钥对（n,e）（n,d）。p，q为512位，n为1024位
        request.session['n'] = n
        request.session['d'] = d
        mod = base64.b64encode(str(n).encode('utf-8')).decode()  # base64编码n
        exp = base64.b64encode(str(e).encode('utf-8')).decode()  # base64编码e
        return render(request, 'page/login.html', {'message':message,"login_form": login_form, "moddd": [mod], "exppp": [exp]})



    login_form = UserForm()
    n,e,d=get_rsa_pair(1024)#生成公私钥对（n,e）（n,d）。p，q为512位，n为1024位
    request.session['n'] = n
    request.session['d'] = d
    mod=base64.b64encode(str(n).encode('utf-8')).decode()#base64编码n
    exp=base64.b64encode(str(e).encode('utf-8')).decode()#base64编码e
    return render(request, 'page/login.html', {"login_form":login_form,"moddd":[mod],"exppp":[exp]})
    pass



def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")

    request.session.flush()
    r=redirect("/login/")
    r.delete_cookie('username')
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return r


def index(request):

    username = request.COOKIES.get('username')
    del_cou=request.GET.get('del_cou')
    course = request.GET.get('course')
    if not username:
        return redirect("/login/")

    user= models.User.objects.get(name=username)
    if user.types==1:
        message = ' '
        new_c = request.GET.get('new')
        max_count=request.GET.get('max_count')
        if new_c:
            course =models.Course.objects.filter(c_teacher=username,c_name=new_c)
            if not course:
                try:
                    with transaction.atomic():
                        new_course = models.Course.objects.create()
                        new_course.c_name = new_c
                        new_course.c_teacher =username
                        new_course.left_count=max_count
                        new_course.max_count=max_count
                        if new_course.c_name and new_course.c_teacher:
                            new_course.save()
                except Exception as e:
                    return HttpResponse("出现错误<%s>" % str(e))
        if course and del_cou == '1':

            c = models.Course.objects.get(c_teacher=username, c_name=course)
            exi = models.Choice.objects.filter(course_id=c.id)
            if exi:
                message = '存在学生无法删除'
            else:
                c = models.Course.objects.get(c_name=course, c_teacher=username)
                c.delete()
        course = models.Course.objects.filter(c_teacher=username)
        return render(request, 'page/index.html',{"course":course,"message":message})
    else:
        course=request.GET.get('course')
        teacher=request.GET.get('teacher')
        exi=models.Course.objects.all()
        if course and teacher:
            c=models.Course.objects.get(c_name=course,c_teacher=teacher)#加锁
            exi=models.Choice.objects.filter(stu=username,course_id=c.id)
            if not exi:
                try:
                    with transaction.atomic():
                        c = models.Course.objects.select_for_update().get(c_name=course, c_teacher=teacher)  # 加锁
                        c.left_count=c.left_count-1
                        choice=models.Choice(course_id=c.id,stu=username)
                        choice.save()
                        c.save()
                except Exception as e:
                    return HttpResponse("出现错误<%s>" % str(e))
            else:
                return redirect("/inf/?course="+course+"&teacher="+teacher)

        #choice.
        c=models.Course.objects.all()
        my_c=models.Choice.objects.filter(stu=username)
        score=[]
        type=[]
        for i in c:
            flag=0
            temp=0
            for j in my_c:
                if i.id==j.course_id:
                    flag=1
                    temp=j.score
                    break
            if flag:
                score.append(temp)
                type.append(0)
            else:
                score.append(-1)
                type.append(1)

        inf = models.Inf.objects.filter(name=username)
        history=[]
        for item in inf:
            q=models.Course.objects.get(id=item.course_id)
            history.append(q)
        print(inf,history)
        return render(request, 'page/index1.html',{"course":zip(c,type,score),"info":zip(inf,history)})

        pass
        pass


def register(request):
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            role=register_form.cleaned_data['role']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'page/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'page/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'page/register.html', locals())

                # 当一切都OK的情况下，创建新用户
                a = hashlib.md5()  # 实例化
                a.update(password1.encode('utf8'))  # 开始加密
                password1 = a.hexdigest()  # 获得加密之后的文本
                new_user = models.User.objects.create()
                new_user.name = username
                new_user.password = password1
                new_user.email = email
                new_user.sex = sex
                if role=='teacher':
                    new_user.types=True
                new_user.save()
                return redirect('/login/')  # 自动跳转到登录页面
    register_form = RegisterForm()
    return render(request, 'page/register.html', locals())



def inf(request):
    username = request.COOKIES.get('username')
    if not username:
        return redirect("/login/")
    course=request.GET.get('course')
    stu = request.GET.get('stu')
    score = request.GET.get('score')
    delete=request.GET.get('delete')
    print(type(delete))
    print([score,stu])
    message=' '
    c = models.Course.objects.get(c_teacher=username, c_name=course)
    if stu and score:
        fix=models.Choice.objects.get(course_id=c.id,stu=stu)
        fix.score=score
        fix.save()
    if stu and delete=='1':
        try:
            with transaction.atomic():
                c = models.Course.objects.select_for_update().get(c_teacher=username, c_name=course)
                fix=models.Choice.objects.get(course_id=c.id,stu=stu)
                c.left_count=c.left_count+1
                c.save()
                fix.delete()
        except Exception as e:
            return HttpResponse("出现错误<%s>" % str(e))

    choice=models.Choice.objects.filter(course_id=c.id)
    return render(request,"page/inf.html",{"choice":choice,"course":course})
    pass