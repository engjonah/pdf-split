import subprocess
from imbox import Imbox
import traceback
import os
import time
import datetime
import yagmail
import glob

def email(who, attachment, msg):
  address = 'SENDER_EMAIL'
  password = 'PASSWORD'
  yag = yagmail.SMTP(address, password)
  yag.send(
    to=who,
    bcc=['ADRESSEE_EMAIL'],
    subject = "Your Split Files",
    contents='Please see attached.\n' + msg,
    attachments=attachment
  )

def download():
  host = "imap.gmail.com"
  username = "GMAIL_USERNAME"
  password = 'PASSWORD'
  download_folder = "/home/pi/Documents/pdf_split"
  
  if not os.path.isdir(download_folder):
    os.makedirs(download_folder, exist_ok=True)
  
  mail = Imbox(host, username=username, password=password, ssl=True, ssl_context=None, starttls=False)
  messages = mail.messages(unread=True, subject='Split', label='Split') #Messages that are unread and have Split in them
  for (uid, message) in messages:
    mail.mark_seen(uid) # optional, mark message as read
    sender = message.sent_from[0]['email']
    time = message.date
    for idx, attachment in enumerate(message.attachments):
      try:
        att_fn = attachment.get('filename')
        download_path = f"{download_folder}/{att_fn}"
        with open(download_path, "wb") as fp:
          fp.write(attachment.get('content').read())
      except:
        pass
        print(traceback.print_exc())
    mail.logout()
    return [sender, time]

def main(): 
  while True: 
    #download all attachments from email
    sender_info = download()
    if sender_info is not None:
      print ('received email!')
      #turn all pdf files into the list 
      emails = glob.glob('/home/pi/Documents/pdf_split/*.pdf')
      for x in range(len(emails)):
        emails[x] = os.path.basename(emails[x])
      #process each attachment seperately
      for attachment in emails: 
        subprocess.run(['./split.sh', attachment])
      #find all split pdfs
      final_attachments = glob.glob('/home/pi/Documents/pdf_split/*_split.pdf')
      for x in range(len(final_attachments)):
        final_attachments[x] = os.path.basename(final_attachments[x])
      now = time.strftime("%H:%M:%S", time.localtime())
      print(now)
      now = str(now).split(":")
      now = now[0]*60*60 + now[1]*60 + now[2]
      sent = sender_info[1].split(' ')[4]
      print (sent)
      sent = sent.split(":")
      sent = sent[0]*60*60 + sent[1]*60 + sent[2]
      #time_spent = now-sent
      mins = int(time_spent/60)
      secs = int(time_spent%60)
      message = ("finished in: " + mins+ ":" +secs)
      print(message)
      email(sender_info[0], final_attachments, message)
      subprocess.run(['./rm.sh']) #delete all pdfs after emailing them back to user
      
    else: 
      print ('waiting for email')
      time.sleep(60)
if __name__ == "__main__":
  main()
