import mailbox
import csv
import os
from pathlib import Path
from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime
import shutil

# Create or reset the .data folder
data_dir = Path('.data')

def convert():
    # Delete .data folder if it exists
    if data_dir.exists() and data_dir.is_dir():
        shutil.rmtree(data_dir)

    # Recreate the base folder and subfolders
    pdf_dir = data_dir / 'attachments/pdf'
    img_dir = data_dir / 'attachments/images'
    pdf_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)

    # Set path for CSV output
    csv_file = data_dir / 'emails.csv'

    # Open mbox
    print("This is mainly made by chatGPT")
    print("Tell me the path of your mbox file:")
    path = input()
    os.system("clear")
    print("processing ...")
    mbox = mailbox.mbox(path)

    # Open CSV for writing
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['index', 'subject', 'from', 'to', 'date', 'body', 'pdf_attachments', 'image_attachments']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, message in enumerate(mbox):
            # Default values
            subject = message['subject']
            from_ = message['from']
            to = message['to']
            date = message['date']
            body = ""
            pdf_files = []
            image_files = []

            # Get email body
            if message.is_multipart():
                for part in message.walk():
                    content_type = part.get_content_type()
                    disposition = part.get("Content-Disposition", "")

                    # Body part
                    if content_type == 'text/plain' and 'attachment' not in disposition:
                        charset = part.get_content_charset() or 'utf-8'
                        body += part.get_payload(decode=True).decode(charset, errors='replace')
                    
                    # HTML body (fallback if plain not available)
                    elif content_type == 'text/html' and not body:
                        charset = part.get_content_charset() or 'utf-8'
                        html = part.get_payload(decode=True).decode(charset, errors='replace')
                        body += BeautifulSoup(html, 'html.parser').get_text()

                    # Attachments
                    elif 'attachment' in disposition:
                        filename = part.get_filename()
                        if filename and part.get_payload(decode=True):
                            file_data = part.get_payload(decode=True)
                            ext = filename.lower().split('.')[-1]
                            safe_filename = f"{i}_{filename.replace('/', '_')}"
                            
                            if ext == 'pdf':
                                pdf_path = pdf_dir / safe_filename
                                pdf_path.write_bytes(file_data)
                                pdf_files.append(str(pdf_path))
                            elif ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                                img_path = img_dir / safe_filename
                                img_path.write_bytes(file_data)
                                image_files.append(str(img_path))
            else:
                charset = message.get_content_charset() or 'utf-8'
                payload = message.get_payload(decode=True)
                if payload:
                    body = payload.decode(charset, errors='replace')

            # Write row to CSV
            writer.writerow({
                'index': i,
                'subject': subject,
                'from': from_,
                'to': to,
                'date': date,
                'body': body.strip(),
                'pdf_attachments': '; '.join(pdf_files),
                'image_attachments': '; '.join(image_files)
            })

    print("✅ All emails and attachments processed.")
