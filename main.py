#!/usr/bin/env python
#
import webapp2
import NepaliDateConverter
import jinja2
import os
import datetime

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

converter = NepaliDateConverter.NepaliDateConverter() 
def advalidation(date):
  year = date[0]
  month = date[1]
  day = date[2]
  if year % 4  == 0:
    calender = (31,29,31,30,31,30,31,31,30,31,30,31)
  else:
    calender = (31,28,31,30,31,30,31,31,30,31,30,31)
  if day > calender[month-1]:
    return False
  else:
    return True
def datetoday():
  now = datetime.datetime.now()
  return  (int(now.year),int(now.month), int(now.day))
def day(date):
   days = ("Monday","Tuesday","Wednesday","Thrusday","Friday","Saturday","Sunday")
   try:
     weekday = days[datetime.date(date[0],date[1],date[2]).weekday()]
     return weekday
   except:
     return None

class Handler(webapp2.RequestHandler):
  def write(self,*a,**kw):
    self.response.out.write(*a,**kw)
  def render_str(self,template,**params):
    t = jinja_env.get_template(template)
    return t.render(params)
  def render(self,template,**kw):
    self.write(self.render_str(template, **kw))

class MainHandler(Handler):
    def get(self):
        todayAD = (datetoday())
        todayBS = converter.ad2bs(todayAD)
        daytoday = day(todayAD)
        self.render("index.html",txtYear=todayBS[0],txtMonth=todayBS[1],txtDay=todayBS[2],adtxtYear=todayAD[0],adtxtMonth=todayAD[1],adtxtDay=todayAD[2],day=daytoday)
    
    def post(self):
        txtMonth = self.request.get("txtMonth")
        txtDay = self.request.get("txtDay")
        txtYear = self.request.get("txtYear")
        conversion = self.request.get("to")
        if conversion == "To Nepali":
            dateinAD =(int(txtYear),int(txtMonth),int(txtDay))
            if advalidation(dateinAD):
                dateinBS = converter.ad2bs(dateinAD)
                weekday = day(dateinAD)
                self.render("index.html",txtYear=dateinBS[0],txtMonth=dateinBS[1],txtDay=dateinBS[2],adtxtYear=dateinAD[0],adtxtMonth=dateinAD[1],adtxtDay=dateinAD[2],conversion=conversion,day=weekday,error="")
            else:
                dateinAD = (datetoday())
                dateinBS = converter.ad2bs(dateinAD)
                daytoday = day(dateinAD)
            
                self.render("index.html",txtYear=dateinBS[0],txtMonth=dateinBS[1],txtDay=dateinBS[2],adtxtYear=dateinAD[0],adtxtMonth=dateinAD[1],adtxtDay=dateinAD[2],conversion="",day="",error="We don't have that date in English Calender")
        if conversion == "To English":
            dateinBS =(int(txtYear),int(txtMonth),int(txtDay))
            dateexist = ( NepaliDateConverter.NepaliDateConverter.bs[int(txtYear)][int(txtMonth)-1] < dateinBS[2] ) #some date doesnot exits, need to dymanically create the dropdown menu and remove this
            if not dateexist:
                dateinAD = converter.bs2ad(dateinBS)
                weekday = day(dateinAD)
                self.render("index.html",txtYear=dateinBS[0],txtMonth=dateinBS[1],txtDay=dateinBS[2],adtxtYear=dateinAD[0],adtxtMonth=dateinAD[1],adtxtDay=dateinAD[2],conversion=conversion,day=weekday,error="")
            else:
                dateinAD = (datetoday())
                dateinBS = converter.ad2bs(dateinAD)
                daytoday = day(dateinAD)
                self.render("index.html",txtYear=dateinBS[0],txtMonth=dateinBS[1],txtDay=dateinBS[2],adtxtYear=dateinAD[0],adtxtMonth=dateinAD[1],adtxtDay=dateinAD[2],conversion="",day="",error="We don't have that date in Nepali Calender")
class APINepaliHandler(Handler):

    def get(self,date):
        year,month,daay = [int(i) for i in (str(date).split("-"))]
        try:
            converter = NepaliDateConverter.NepaliDateConverter() 
            weekday = day((year,month,daay)) 
            date = converter.ad2bs((year,month,daay))
            if not date:
              self.response.out.write("Out of Range")
            else:
              self.response.out.write({'weekday':weekday,'year':str(date[0]),'month':str(date[1]),'day':str(date[2])})
        except :  
          self.response.out.write("There was a error, is the url formatted correctly, /tonepali/yyyy-mm-dd <br>eg. /tonepali/1989-1-23")


class APIEnglishHandler(Handler):
    def get(self,date):
        year,month,daay = [int(i) for i in (str(date).split("-"))] 
        try:
            converter = NepaliDateConverter.NepaliDateConverter() 
            weekday = day((year,month,daay)) 
            date = converter.bs2ad((year,month,daay))
            if not date:
               self.response.out.write("Out of range")
            else:
               self.response.out.write({'weekday':weekday,'year':str(date[0]),'month':str(date[1]),'day':str(date[2])})
        except :  
          self.response.out.write("There was a error, is the url formatted correctly, /toenglish/yyyy-mm-dd <br>eg. /toenglish/2046-7-23")
app = webapp2.WSGIApplication([('/', MainHandler),('/toenglish/(.+)',APIEnglishHandler),('/tonepali/(.+)',APINepaliHandler)],debug=True)
