from django.db import models

# Create your models here.


class User(models.Model):
    '''用户表'''

    gender = (
        ('male', '男'),
        ('female', '女'),
    )

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=32, choices=gender, default='男')
    c_time = models.DateTimeField(auto_now_add=True)
    types = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['c_time']
        verbose_name = '用户'
        verbose_name_plural = '用户'

class Course(models.Model):
    c_name=models.CharField(max_length=128)
    c_teacher=models.CharField(max_length=128)
    max_count=models.IntegerField(default=40)
    left_count=models.IntegerField(default=0)

    def __str__(self):
        return self.c_name

    class Meta:
        unique_together=(("c_name","c_teacher"),)
        ordering = ['c_name']
        verbose_name = '课程'
        verbose_name_plural = '课程'

class Inf(models.Model):
    name=models.CharField(max_length=128)
    course=models.ForeignKey(Course)
    time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['time']
        verbose_name = '选课记录'
        verbose_name_plural = '选课记录'

class Choice(models.Model):
    course=models.ForeignKey(Course)
    time = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    stu=models.CharField(max_length=128,default=' ')
    class Meta:
        ordering = ['time']
        verbose_name = '已选课'
        verbose_name_plural = '已选课'