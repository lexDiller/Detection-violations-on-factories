import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os


def send_mail_moroz(path :str, name :str):
    SUBJECT = 'Ежедневный отчет по Морозовке'
    FILENAME = name
    FILEPATH = path
    MY_EMAIL = 'reporting_operational@azotvzryv.ru'
    MY_PASSWORD = 'gbgm4Jdf9V'
    TO_EMAILS = (['a.li@avmining.ru', 'a.parshenkov@avmining.ru', 'al.fedorov@avmining.ru'])
                 # , 't.timina@avmining.ru',)
                 # 'a.vavilov@avmining.ru', 'e.myachikova@avmining.ru']
    SMTP_SERVER = 'av-vsr-exch-01.avgroup.com'
    SMTP_PORT = 2500
    TO_EMAILS_str = ', '.join(TO_EMAILS)
    body = ("")
    msg = MIMEMultipart()
    msg['From'] = MY_EMAIL
    msg['To'] = TO_EMAILS_str
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(body, 'plain'))
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(FILEPATH, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=FILENAME)
    msg.attach(part)
    smtpObj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(MY_EMAIL, MY_PASSWORD)
    smtpObj.sendmail(MY_EMAIL, TO_EMAILS_str.split(", "), msg.as_string())
    smtpObj.quit()


def clear_folder(folder_path: str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    clean_path = folder_path
    if not os.path.exists(clean_path):
        print(f"Folder '{clean_path}' none.")
        return
    file_list = os.listdir(clean_path)
    for file_name in file_list:
        file_path = os.path.join(clean_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
