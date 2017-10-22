import urllib.request, urllib.parse, urllib.error
import json
import smtplib
from email.mime.text import MIMEText
import configInfo


serviceurl = 'http://api.openweathermap.org/data/2.5/forecast?id='+configInfo.cityID+'&units=imperial&APPID='+configInfo.APIkey
forecastRain = {}
forecastRainDays = []


def checkForecast():
    uh = urllib.request.urlopen(serviceurl)
    data = uh.read().decode()

    try:
        js = json.loads(data)
    except:
        js = None

    # print(json.dumps(js, indent=4))

    for item in js['list']:
        forecastDayTime = item['dt_txt']
        forecastDay = forecastDayTime.split()[0]
        projCond = item['weather'][0]['main']
        projCondDesc = item['weather'][0]['description']

        # find rainy days
        if projCond.lower() == 'rain':
            forecastRain[forecastDayTime] = projCondDesc
            if forecastDay not in forecastRainDays:
                forecastRainDays.append(forecastDay)
            else:
                continue
        else:
            continue


def sendEmail():
    subj = 'Rain Detected'
    EMAIL_TO = configInfo.EMAIL_TO['Rain']

    # building email with forecast
    emailString = 'Expected Rain:\r\n'
    for day in forecastRain:
        emailString += day + ': ' + str(forecastRain[day]) + '\r\n'

    # send email
    msg = MIMEText(emailString)
    msg['Subject'] = subj
    msg['From'] = configInfo.EMAIL_FROM
    msg['To'] = EMAIL_TO
    debuglevel = True
    mail = smtplib.SMTP(configInfo.SMTP_SERVER, configInfo.SMTP_PORT)
    mail.set_debuglevel(debuglevel)
    mail.starttls()
    mail.login(configInfo.SMTP_USERNAME, configInfo.SMTP_PASSWORD)
    mail.sendmail(configInfo.EMAIL_FROM, EMAIL_TO, msg.as_string())
    mail.quit()


checkForecast()
if len(forecastRainDays) > 0:
    sendEmail()