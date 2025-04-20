import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication   # good enough for .ics


def create_send_email(request):
    # ------------------------------------------------------------------
    # 1) CONFIGURE THESE FOUR LINES ONLY --------------------------------
    SENDER   = "veganman2018@gmail.com"
    APP_PWD  = "ckwvrboupappkpdc"               # 16‑chars, no spaces
    RECIPIENTS = [
        "Vinal.Jain@UTDallas.edu",
        "vxj230003@UTDallas.edu",
        "virat-kumar@outlook.com",
        "vk001716@gmail.com"
    ]
    ICS_PATH = "event.ics"
    # ------------------------------------------------------------------

    # -- Build the message ------------------------------------------------
    msg               = MIMEMultipart("mixed")
    msg["From"]       = SENDER
    msg["To"]         = ", ".join(RECIPIENTS)
    msg["Subject"]    = "Add your event " + request["event_name"]

    # 1️⃣  Body (plain text helps spam filters)
    body_text = (
        "Hi ,\n\n"
        "Kindly find the calendar invite attached. "
        "Open it to add the event to your calendar.\n\n"
        "Regards,\nVinal\n"
    )
    msg.attach(MIMEText(body_text, "plain"))

    # 2️⃣  Attachment (.ics)
    basename = os.path.basename(ICS_PATH)
    with open(ICS_PATH, "rb") as f:
        part = MIMEApplication(f.read(), Name=basename)
        part['Content-Disposition'] = f'attachment; filename="{basename}"'
        part['Content-Type']       = 'text/calendar; method=REQUEST; name="{}"'.format(basename)
        msg.attach(part)

    # -- Send -------------------------------------------------------------
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER, APP_PWD)
        result = smtp.sendmail(SENDER, RECIPIENTS, msg.as_string())

    print("Gmail response dict (empty means accepted):", result)
    return True
