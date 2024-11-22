import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

class mailing:
    # receiver_email = "fardeenahmad853@gmail.com"
    # receiver_email = "mosako021@gmail.com"
    def __init__(self) -> None:
        self.sender_email = "dweb75260@gmail.com"
        self.password = "kxlogozjjwpxlvre"
        self.smtp_server = "smtp.google.com"
        self.smtp_port = 587
        self.subject = "Intrusion Alert"
        self.critical_subject = "Critical Security Breach Immediate Action Required"
        
    def compose_alert(self,name:str,receiver_email:str,img_path:str)->MIMEMultipart:
        body = f"""
Dear {name},
We have detected suspicious activity on your cameras. Please review the following details immediately
Alert the nearby police station if thats not you.
Your security is our priority,
VigiLENS.
[this is a computer generated mail please do not reply to this]
"""
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = receiver_email
        msg['Subject'] = self.subject
        msg.attach(MIMEText(body, 'plain'))
        try:
            with open(img_path, 'rb') as img_file:
                img = MIMEImage(img_file.read(), name="Alert Capture")
                msg.attach(img)
            return msg
        except Exception as e:
            print(f'Error:{e}')
            return msg
    def compose_warning(self,name:str,receiver_email:str,img_path:str)->MIMEMultipart:
        body = f"""
Dear {name},
We have detected multiple suspicious activity on your property. This can result serious risk
Alert the nearby police station if thats not you.
Your security is our priority,
VigiLENS.
[this is a computer generated mail please do not reply to this]
"""
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = receiver_email
        msg['Subject'] = self.critical_subject
        msg.attach(MIMEText(body, 'plain'))
        try:
            with open(img_path, 'rb') as img_file:
                img = MIMEImage(img_file.read(), name="Alert Capture")
                msg.attach(img)
            return msg
        except Exception as e:
            print(f'Error:{e}')
            return msg
    def send(self,msg)->bool:
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email,msg['To'], msg.as_string())
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
