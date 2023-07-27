import smtplib
from email.mime.text import MIMEText
 
def send_mail(msg, subject):
    me = 'sanghun1210@gmail.com'
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(me, 'emkyudballjbrzdb')
 
    msg = MIMEText(msg)
    msg['Subject'] = subject
    smtp.sendmail(me, me, msg.as_string())
    smtp.quit()
