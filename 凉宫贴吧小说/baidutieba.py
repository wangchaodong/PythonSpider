#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
爬虫学习项目,在这个网站看到的教程(http://cuiqingcai.com/993.html) 
我将其中的一些正则修改,加入图片爬取功能.
爬取的内容是凉宫春日吧的一个小说帖子 http://tieba.baidu.com/p/3354416001
'''

__author__ = 'cd2want'

import urllib
import urllib2
import re
import os
import sys

#处理页面标签类
class Tool:
    #去除img标签,7位长空格
    removeImg = re.compile('<img.*?>| {7}|')
    #删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    #把换行的标签换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    #将表格制表<td>替换为\t
    replaceTD= re.compile('<td>')
    #把段落开头换为\n加空两格
    replacePara = re.compile('<p.*?>')
    #将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    #将其余标签剔除
    removeExtraTag = re.compile('<.*?>')
    def replace(self,x):
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeAddr,"",x)
        x = re.sub(self.replaceLine,"\n",x)
        x = re.sub(self.replaceTD,"\t",x)
        x = re.sub(self.replacePara,"\n    ",x)
        x = re.sub(self.replaceBR,"\n",x)
        x = re.sub(self.removeExtraTag,"",x)
        #strip()将前后多余内容删除
        return x.strip()

#百度贴吧爬虫类
class DBTB:

    def __init__(self,url,seeLZ):
        # 主要url
        self.url = url
        # 是否只看楼主
        self.seeLZ = '?see_lz=%s'%seeLZ
        # HTML表情剔除工具类
        self.tool = Tool()
        # 文件写入操作对象
        self.file = None
        self.default_title = u'Bai Du Tie Ba'
        # 图片
        self.images = []

    def getPage(self,pageNum):
        try:
            url = self.url+self.seeLZ + '&pn=%d' % pageNum

            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            # print(response.read())
            return response.read().decode('utf-8')
        except urllib2.URLError as e:
            if hasattr(e, 'reason'):
                print('百度贴吧连接失败, 错误原因', e.reason)
                return

    # 获取标题
    def getTitle(self,page):
        # page = self.getPage(1)
        pattern = re.compile('<h3 class="core_title_txt.*?>(.*?)</h3>',re.S)
        result = re.search(pattern, page)
        if result:
            print(result.group(1))
            return result.group(1).strip()
        else:
            return

    def setFileTitle(self,title):
         # 如果标题不是为None，即成功获取到标题
        if title is not None:
            # w+ 打开一个文件用于读写。如果该文件已存在则将其覆盖。如果该文件不存在，创建新文件。
            self.file = open(title + ".txt","w+")
        else:
            self.file = open(self.defaultTitle + ".txt","w+")

    # 获取 页数
    def getPageNum(self,page):
        # page = self.getPage(1)
        pattern = re.compile('<li class="l_reply_num.*?</span>.*?<span.*?>(.*?)</span>', re.S)
        result = re.search(pattern, page)
        if result:
            print(result.group(1))
            return result.group(1).strip()
        else:
            return

    # 获取 每个帖子里的内容
    def getContent(self,page):
        # page = self.getPage(1)
        # 匹配所有楼层内容
        pattern = re.compile('<div id="post_content_.*?>(.*?)</div>', re.S)
        items = re.findall(pattern, page)
        # for item in items:
        #     print(item)
        contents = []
        for item in items:
            # 去除html标签 加入换行符
            content = '\n'+self.tool.replace(item)+'\n'
            contents.append(content)
        return contents
        # print self.tool.replace(items[1])

    # 获取每个帖子里的图片
    def getimage(self,page):
        pattern = re.compile(r'<img.*?src="(.*?)" pic_ext="jpeg"')
        items = re.findall(pattern, page)
        for item in items:
            print(item.encode('utf-8'))
            self.images.append(item.encode('utf-8'))

    # 下载并保存图片
    def saveImage(self):
        #保存到一个文件夹中
        imgpath = os.getcwd()+'/凉宫春日'
        if os.path.exists(imgpath) is False:
            print("创建文件夹:",imgpath)
            os.mkdir(imgpath)

        for (key,imgUrl) in enumerate(self.images):
            # img = urllib.urlopen(imgUrl)
            # data = img.read()
            # f = open(str(key)+'.jpg','wb')
            # f.write(data)
            # f.close()
            path = imgpath + '/%d.jpg'%key
            print('正在保存第%d张图'%key)
            try:
                urllib.urlretrieve(urllib.urlopen(imgUrl).geturl(),path)
            except:
                print('该图片下载失败: %s'%imgUrl)

    # file write
    def fileWrite(self,contents):

        for item in contents:
            self.file.write(item.encode('utf-8'))

    def start(self):
        indexPage = self.getPage(1)
        pageNum = self.getPageNum(indexPage)
        title = self.getTitle(indexPage)
        self.setFileTitle(title)

        if pageNum == None:
            print("url 已失效 请重试")
            return
        try:
            print('这个帖子一共有'+str(pageNum)+' 页')
            for i in range(1,int(pageNum)+1):
                print('正在写入第%d页数据' % (i))
                page = self.getPage(i)
                self.getimage(page)
                contents = self.getContent(page)
                self.fileWrite(contents)
            self.saveImage()
        except IOError as e:
            print('IOError. reason:',e.message)
        finally:
            print('done')



if __name__=='__main__':

    url = 'http://tieba.baidu.com/p/3354416001'
    dbspider = DBTB(url,1)
    dbspider.start()
# # txt = db.getPage(1).encode('utf-8')
# # print(txt)
# # f = open('tb.txt','wb')
# # f.write(txt)
# # f.close()
# db.getTitle(1)
# db.getPageNum()
# db.getContent()
