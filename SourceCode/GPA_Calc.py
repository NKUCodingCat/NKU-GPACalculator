#! /usr/bin/env python
#coding:utf8

import httplib
import re
import wx
import sys
import os
import platform

#---------------------------------------------------------
Ver = 'NKU GPA Calculator'


HEADERS = {
'Accept':' application/x-ms-application, image/jpeg, application/xaml+xml, image/gif, image/pjpeg, application/x-ms-xbap, */*',
'Referer':' http://222.30.32.10/xsxk/swichAction.do',
'Accept-Language':' zh-CN',
'Content-Type':' application/x-www-form-urlencoded',
'Accept-Encoding':' gzip, deflate',
'User-Agent':' Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; InfoPath.3)',
'Host':' 222.30.32.10',
'Pragma':' no-cache',
'Cookie':''
}
Login = False
Preset = ['ABC', 'BCD', 'FC,FD', u'全部', u'自定义']
ScoreList = {
'A':[], 'B':[], 'C':[], 'D':[], 'E':[], 'FC':[], 'FD':[]
}
LoginPanelWidget = []
if getattr(sys, 'frozen', False):
	LocPath = os.path.dirname(sys.executable)+"/"
elif __file__:
	LocPath = os.path.dirname(__file__)+"/"
else:
	print "Find Path Error"
isWindows = (platform.platform().upper()[:7]=="WINDOWS")
isOSX = (platform.system().upper()=="Darwin")
#---------------------------------------------------------
def INIT():
	global Login
	Login = False
	if CheckSystemStatus():
		try:
			conn=httplib.HTTPConnection("222.30.32.10",timeout=20)
			conn.request("GET","/")
			res=conn.getresponse()
			cookie=res.getheader("Set-Cookie")
			conn.close()
		except:
			return False
		HEADERS['Cookie'] = cookie
		try:
			conn=httplib.HTTPConnection("222.30.32.10",timeout=20)
			conn.request("GET","http://222.30.32.10/ValidateCode","",HEADERS)
			res=conn.getresponse()
			f=open(LocPath+"ValidateCode.jpg","w+b")
			f.write(res.read())
			f.close()
			conn.close()
		except:
			return False
		return True
	return False

def CheckSystemStatus():
	try:
		conn=httplib.HTTPConnection("222.30.32.10",timeout=10)
		conn.request("GET","ttp://222.30.32.10/xsxk/studiedAction.do")
		conn.getresponse()
		conn.close()
	except:
		return False
	return True

#---------------------------------------------------------
class AppFrame(wx.Frame):
	def __init__(self, calc = False):
		wx.Frame.__init__(self, parent = None, title = Ver, size = (360, 265))
		self.fSizer = wx.BoxSizer(wx.VERTICAL)
		self.panel = AppPanel(self, calc)
		self.Bind(wx.EVT_CLOSE, self.OnClose, self)
		self.Show()

	def OnClose(self, event):
		self.Destroy()
		sys.exit(0)


#---------------------------------------------------------
class AppPanel(wx.Panel):
	def __init__(self, parent, calc):
		wx.Panel.__init__(self, parent)
		self.frame = parent
		if calc:
			self.CalcPanel()
		else:
			self.LoginPanel()

	def LoginPanel(self):
		self.label_id = wx.StaticText(self, 1, u"学号:")
		self.label_id.SetPosition(wx.Point(85, 15))
		self.label_psw = wx.StaticText(self, 2, u"密码:")
		self.label_psw.SetPosition(wx.Point(85, 50))
		self.label_val = wx.StaticText(self, 3, u"验证码:")
		self.label_val.SetPosition(wx.Point(85, 115))

		self.text_id = wx.TextCtrl(self, 4)
		self.text_id.SetPosition(wx.Point(140, 15))

		self.text_psw = wx.TextCtrl(self, 5, style = wx.TE_PASSWORD)
		self.text_psw.SetPosition(wx.Point(140, 50))

		self.text_val = wx.TextCtrl(self, 6, style = wx.TE_PROCESS_ENTER )
		self.text_val.SetPosition(wx.Point(140, 115))
		self.Bind(wx.EVT_TEXT_ENTER, self.Login, self.text_val)

		self.confirm = wx.Button(self, 7, label = u"登录")
		self.confirm.SetPosition(wx.Point(150, 145))
		self.Bind(wx.EVT_BUTTON, self.Login)

		self.error_text = wx.StaticText(self, 8, "", style= wx.ALIGN_CENTER)
		self.error_text.SetPosition(wx.Point(95, 175))

		self.image = wx.Image(LocPath+"ValidateCode.jpg", wx.BITMAP_TYPE_JPEG)
		self.val = wx.StaticBitmap(self, 9, bitmap = self.image.ConvertToBitmap())
		self.val.SetPosition(wx.Point(89, 80))

		self.version = wx.StaticText(self, 0, "@version 0.0.3", pos = (255, 205))

	def OutPut(self, event):
		global LocPath
		if not OSX:
			LocPath = re.sub('[^/]+?/Contents/MacOS/', '', LocPath)
		f = open(LocPath + "Your_Score.txt","w")
		for i in sorted(ScoreList.keys()):
			for j in ScoreList[i]:
				f.writelines(("%s\t"*3)%(j['name'],j['credit'],j['score'])+"\n")
		f.close()
		if isWindows:
			#print unicode(LocPath.decode("GBK"))
			#print u"成绩清单已被导出到\n"+LocPath + u"Your_Score.txt"+u"\n是否打开？"
			dlg = wx.MessageBox( u"成绩清单已被导出到\n"+unicode(LocPath.decode("GBK")) + u"Your_Score.txt"+u"\n是否打开？",u'导出完成', wx.YES_NO |wx.ICON_INFORMATION | wx.STAY_ON_TOP)
			if dlg == wx.YES:
				os.startfile(LocPath + "Your_Score.txt")
			else:
				pass
		else:
			dlg = wx.MessageBox( u"成绩清单已被导出到\n"+unicode(LocPath) + u"Your_Score.txt",u'导出完成', wx.ICON_INFORMATION | wx.STAY_ON_TOP)

	def CalcPanel(self):
		self.preset = wx.RadioBox(self, 20, label = "", pos = (15,110),
			choices = Preset, majorDimension = 2)
		self.Bind(wx.EVT_RADIOBOX, self.OnRadio, self.preset)

		self.A = wx.CheckBox(self, 11, label = u"A类", pos = (185,120))
		self.B = wx.CheckBox(self, 12, label = u"B类", pos = (185,145))
		self.C = wx.CheckBox(self, 13, label = u"C类", pos = (185,170))
		self.D = wx.CheckBox(self, 14, label = u"D类", pos = (235,120))
		self.E = wx.CheckBox(self, 15, label = u"E类", pos = (235,145))
		self.FC = wx.CheckBox(self, 16, label = "FC", pos = (285,120))
		self.FD = wx.CheckBox(self, 17, label = "FD", pos = (285,145))
		#=====================
		self.confirm = wx.Button(self, 15, label = u"导出")
		self.confirm.SetPosition(wx.Point(240, 175))
		self.Bind(wx.EVT_BUTTON, self.OutPut)
		#=====================
		self.CourseType = [self.A, self.B, self.C, self.D, self.E, self.FC, self.FD]
		self.EnableCourseType(False)

		for ctype in self.CourseType:
			self.Bind(wx.EVT_CHECKBOX, self.OnRadio, ctype)

		self.infoText = wx.StaticText(self, 18, label = '=, =', pos = (25,15))
		self.infoText.SetFont(wx.Font(17, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))

		self.GPAText = wx.StaticText(self, 19, label = '12.345678', pos = (90,55))
		self.GPAText.SetFont(wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))

		self.OnRadio(wx.EVT_RADIOBOX)

	def calculate(self, typeList):
		GPA = 0
		total_credit = 0
		for ctype in typeList:
			for course in ScoreList[ctype]:
				GPA += course['score']*course['credit']
				total_credit += course['credit']
		if GPA == 0:
			return 'N.A.'
		return GPA/total_credit

	def getSelected(self):
		selected = []
		choice = self.preset.GetSelection()
		if choice == 0:
			selected = ['A', 'B', 'C']
		if choice == 1:
			selected = ['B', 'C', 'D']
		if choice == 2:
			selected = ['FC', 'FD']
		if choice == 3:
			selected = ['A', 'B', 'C', 'D', 'E', 'FC', 'FD']
		if choice == 4:
			index_arr = ['A', 'B', 'C', 'D', 'E', 'FC', 'FD']
			index = 0
			for ctype in self.CourseType:
				if ctype.IsChecked():
					selected.append(index_arr[index])
				index += 1
		return selected

	def ShowResult(self, result, typeList):
		info = ''
		for typename in typeList:
			info += typename+' '
		info += u'平均成绩：'
		self.infoText.SetLabel(unicode(info))
		self.GPAText.SetLabel(str(result))

	def getScore(self):
		conn = httplib.HTTPConnection('222.30.32.10')
		conn.request('GET', 'http://222.30.32.10/xsxk/studiedAction.do', '', HEADERS)
		content = conn.getresponse().read().decode('GBK')
		conn.close()
		number_of_pages = re.findall('共 ([0-9]+) 页', content.encode('utf8'))
		number_of_pages = int(number_of_pages[0])

		requestURL = 'http://222.30.32.10/xsxk/studiedPageAction.do'
		postdata = 'index='
		for index in range(1, number_of_pages+1):	#每一页
			conn = httplib.HTTPConnection('222.30.32.10')
			conn.request('POST', requestURL, 'index='+str(index), HEADERS)
			content = conn.getresponse().read().decode('GBK').encode('utf8')
			conn.close()
			content = re.sub('[\\t\\r\\n\\ ]+','',content)
			re_course = re.compile('<trbgcolor="#FFFFFF">([\s\S]+?)</tr>')
			course = re_course.findall(content)
			course = course[:len(course)-1]

			pass_list = []
			for detail in course:	#每门课程的情况
				re_detail = re.compile('<tdalign="center"class="NavText">([\s\S]*?)</td>')
				cc = re_detail.findall(detail)	#每门课的情况排成一个列表
												#下标0-7依次：序号 课程代码 名称 类型 成绩 学分 重修成绩 重修情况
				if cc[4] == '通过':
					#ScoreList[cc[3]].append({'score':80,'credit':1})
					pass_list.append({'score':0, 'credit':float(cc[5]), 'type':cc[3], 'name':cc[2]})
					continue
				c = {'score':0,'credit':0}
				if cc[6] == '':	#无重修 cc[6] : 重修成绩
					c['score'] = float(cc[4])
				else:
					c['score'] = float(cc[6])
				c['credit'] = float(cc[5])
				c['name'] = cc[2]
				ScoreList[cc[3]].append(c)	#cc[3] 课程类型
			if len(pass_list) == 1 and pass_list[0]['type'] == 'C':
				pass_list = pass_list[0]
				ABCScore = re.findall('ABC类课学分绩:([0-9\.]+?)\(成绩合格课程\)', content)[0]
				ABCScore = float(ABCScore)
				ABCCredit = 0
				for ctype in ['A', 'B', 'C']:
					for course in ScoreList[ctype]:
						ABCCredit += course['credit']
				pass_list['score'] = (( ABCScore*(ABCCredit+pass_list['credit'])
									-self.calculate(['A','B','C'])*ABCCredit )
									/pass_list['credit'])
				#print pass_list
				ScoreList[pass_list['type']].append(pass_list)

	def OnRadio(self, event):
		choice = self.preset.GetSelection()
		if choice == 4:
			self.EnableCourseType()
		else:
			self.EnableCourseType(False)
		selected = self.getSelected()
		self.ShowResult(self.calculate(selected), selected)

	def EnableCourseType(self, flag = True):
		if flag:
			for type in self.CourseType:
				type.Enable()
		else:
			for type in self.CourseType:
				type.Disable()

	def Login(self, event):
		global Login
		global HEADERS

		ID = self.text_id.GetValue()
		passwd = self.text_psw.GetValue()
		v_code = self.text_val.GetValue()

		try:
			logindata="operation=&usercode_text="+ID+"&userpwd_text="+passwd+"&checkcode_text="+v_code+"&submittype=%C8%B7+%C8%CF"
			conn=httplib.HTTPConnection("222.30.32.10",timeout=10)
			conn.request("POST","http://222.30.32.10/stdloginAction.do",logindata,HEADERS)
			res=conn.getresponse()
			response=res.read()
			content=response.decode("gb2312")
			conn.close()
		except:
			self.error_text.SetLabel(u"网络连接错误，无法连接到选课系统。请检查网络连接！")
			return

		self.err_code = u"未知错误"

		if content.find("stdtop") != -1:
			Login = True

		if Login == False and (content.find(unicode("请输入正确的验证码","utf8")) != -1):
			self.err_code = u"验证码错误！"
			self.text_val.SetValue('')
			if INIT():
				self.image.Destroy()
				self.val.Destroy()
				self.image = wx.Image(LocPath+"ValidateCode.jpg", wx.BITMAP_TYPE_JPEG)
				self.val = wx.StaticBitmap(self, 9, bitmap = self.image.ConvertToBitmap())
				self.val.SetPosition(wx.Point(89, 80))
			else:
				self.error_text.SetLabel(u"网络连接错误，无法连接到选课系统。请检查网络连接！")

		if Login == False and (content.find(u"用户不存在或密码错误") != -1):
			self.err_code = u"用户不存在或密码错误！"
			self.text_id.SetValue('')
			self.text_psw.SetValue('')

		if Login == False and (content.find(u"忙") != -1 or content.find(u"负载") != -1):
			self.err_code = u"系统忙，请稍后再试！"

		if not Login:
			self.error_text.SetLabel(unicode(self.err_code))
			return

		self.error_text.SetLabel(u'正在获取成绩...')
		self.getScore()
		self.GatherLoginWidget()
		self.Switch2CalcPanel()

	def GatherLoginWidget(self):
		LoginPanelWidget.append(self.label_id)
		LoginPanelWidget.append(self.label_psw)
		LoginPanelWidget.append(self.label_val)
		LoginPanelWidget.append(self.text_id)
		LoginPanelWidget.append(self.text_psw)
		LoginPanelWidget.append(self.text_val)
		LoginPanelWidget.append(self.confirm)
		LoginPanelWidget.append(self.error_text)
		LoginPanelWidget.append(self.val)
		LoginPanelWidget.append(self.version)

	def Switch2CalcPanel(self):
		for widget in LoginPanelWidget:
			widget.Hide()
		self.CalcPanel()

#---------------------------------------------------------
if __name__ == "__main__":
	INIT()
	app = wx.App()
	frame = AppFrame()
	app.MainLoop()

#---------------------------------------------------------
