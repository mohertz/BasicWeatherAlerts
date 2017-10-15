import urllib.request, urllib.parse, urllib.error
import json
import smtplib
from email.mime.text import MIMEText
import configInfo


serviceurl = 'http://api.openweathermap.org/data/2.5/forecast?id='+configInfo.cityID+'&units=imperial&APPID='+configInfo.APIkey
forecastLows = {}
freezingDays = []


def checkForecast():
    uh = urllib.request.urlopen(serviceurl)
    data = uh.read().decode()

    try:
        js = json.loads(data)
    except:
        js = None

    for item in js['list']:
        forecastDayTime = item['dt_txt'].split()
        forecastDay = forecastDayTime[0]
        projLow = item['main']['temp_min']

        # find lows
        if forecastDay not in forecastLows or projLow < forecastLows[forecastDay]:
            forecastLows[forecastDay] = projLow
        else:
            continue

        # find projected lows that are near or below freezing
        if projLow < 33 and forecastDay not in freezingDays:
            freezingDays.append(forecastDay)

    for day in forecastLows:
        print(day + ':', forecastLows[day])


def sendEmail():
    subj = 'Projected Lows'

    # building email with forecast
    emailString = 'Projected lows for the next 5 days are:\r\n'
    for day in forecastLows:
        emailString += day + ': ' + str(forecastLows[day]) + '\r\n'
    if len(freezingDays) > 0:
        subj = 'FREEZING TEMPS UPCOMING'
        emailString += 'Projected lows near or below freezing for:\r\n'
        for day in freezingDays:
            emailString += day + '\r\n'

    # send email
    msg = MIMEText(emailString)
    msg['Subject'] = subj
    msg['From'] = configInfo.EMAIL_FROM
    msg['To'] = configInfo.EMAIL_TO
    debuglevel = True
    mail = smtplib.SMTP(configInfo.SMTP_SERVER, configInfo.SMTP_PORT)
    mail.set_debuglevel(debuglevel)
    mail.starttls()
    mail.login(configInfo.SMTP_USERNAME, configInfo.SMTP_PASSWORD)
    mail.sendmail(configInfo.EMAIL_FROM, configInfo.EMAIL_TO, msg.as_string())
    mail.quit()


checkForecast()
sendEmail()