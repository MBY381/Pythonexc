from tkinter import*
import csv
import os
import urllib.request
from bs4 import BeautifulSoup
import pygal
import cityinfo
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
from PIL import Image,ImageTk




def getinfo():
    
    #将输入的中文城市名转换为ciyinfo对应的标准数字代码，目标网站以此代码作为不同城市的标记
    cityname = entry1.get()
    if cityname in cityinfo.city:
        citycode = cityinfo.city[cityname]
    else:
        sys.exit()

    url = 'http://www.weather.com.cn/weather/' + str(citycode) + '.shtml'#合成目标url
    header = ("User-Agent",
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36")  # 设置Headers
    http_handler = urllib.request.HTTPHandler()
    opener = urllib.request.build_opener(http_handler)
    opener.addheaders = [header]
    request = urllib.request.Request(url) 
    response = opener.open(request)  
    html = response.read()  
    html = html.decode('utf-8')  

    
    final = []  
    bs = BeautifulSoup(html, "html.parser")  
    body = bs.body
    data = body.find('div', {'id': '7d'})
    print(type(data))
    ul = data.find('ul')
    li = ul.find_all('li')

    # 爬取天气数据
    i = 0  # 控制爬取的天数
    lows = []  # 保存低温
    highs = []  # 保存高温
    daytimes = []  # 保存日期
    weathers = []  # 保存天气
    for day in li:  
        if i < 7:
            temp = []  
            date = day.find('h1').string  
            
            temp.append(date)
            daytimes.append(date)
            inf = day.find_all('p')  

            
            temp.append(inf[0].string)
            weathers.append(inf[0].string)
            temlow = inf[1].find('i').string  
            if inf[1].find('span') is None:  
                temhigh = None
                temperate = temlow
            else:
                temhigh = inf[1].find('span').string  
                temhigh = temhigh.replace('℃', '')
                temperate = temhigh + '/' + temlow
            
            #转换温度为绘图整数
            lowStr = ""
            lowStr = lowStr.join(temlow.string)
            lows.append(int(lowStr[:-1]))  
            if temhigh is None:
                highs.append(int(lowStr[:-1]))
            else:
                highStr = ""
                highStr = highStr.join(temhigh)
                highs.append(int(highStr))  
            temp.append(temperate)
            final.append(temp)
            i = i + 1

    # 清除上一次写入的天气数据csv文件
    os.remove("weatherinfo.csv")

    # 将最终的获取的天气写入csv文件
    with open('weatherinfo.csv', 'a', errors='ignore', newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerows([cityname])
        f_csv.writerows(final)

    # 绘图
    bar = pygal.Line()  
    bar.add('lowest temperature', lows)
    bar.add('highest temperature', highs)

    bar.x_labels = daytimes
    bar.x_labels_major = daytimes[::30]
    bar.x_label_rotation = 45

    bar.title = cityname + 'Temperature of the next seven days'
    bar.x_title = 'Date'
    bar.y_title = 'Temperature (Celsius)'

    bar.legend_at_bottom = True

    bar.show_x_guides = False
    bar.show_y_guides = True

    bar.render_to_file('tempdraw.svg')
    
    drawing = svg2rlg("tempdraw.svg")
    renderPM.drawToFile(drawing, "tempdraw.jpg", fmt='JPG')



myWindow = Tk()

#定义全局变量解决了后续show函数显示空图的问题
photo=None
img=None
myWindow.geometry("1100x700")
myWindow.title('天气查询系统')#设置标题

Label(myWindow, text="请输入城市名",bg="pink").grid(row=0,column=0)
Label(myWindow,text=" ").grid(row=0,column=1)
#输入城市名
entry1=Entry(myWindow)
entry1.grid(row=0, column=2)

#定义了show函数用于显示查询绘图操作完成之后的结果图
def show():
    global img
    global photo
    img = Image.open('tempdraw.jpg')  # 打开图片
    photo = ImageTk.PhotoImage(img)  # 用PIL模块的PhotoImage打开
    Label(myWindow, image=photo).grid(row=2, column=4)
    
'''
   调用getinfo查询天气并写入csv文件，绘图并转为jpg文件供GUI显示
   GUI不能直接显示绘图的svg格式文件，在转为gif，或者jpg,png等格式后才能被调用
   此处文件转换出现了中文乱码的问题，与目标格式无关，尝试过其他多种方法无果
'''
run = Button(myWindow, text='查询天气', command=getinfo,bg="orange", fg="white")
run.grid(row=1, column=0, sticky=W, padx=5, pady=5)

#退出按钮
quit = Button(myWindow, text='退出', command=myWindow.quit,bg="lightblue", fg="black")
quit.grid(row=1, column=1, sticky=W, padx=5, pady=5)

#显示查询绘图操作完成之后的结果图
getimg = Button(myWindow, text='显示曲线图',command=show,bg='lightgreen',fg='white')
getimg.grid(row=1, column=2, sticky=W, padx=5, pady=5)



#进入消息循环
myWindow.mainloop()
