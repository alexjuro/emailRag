from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import os
import csv
from pathlib import Path
from pypdf.errors import FileNotDecryptedError
from langchain.schema import Document
from itertools import islice

csv.field_size_limit(10 * 1024 * 1024)

EMBEDDING_MODEL_NAME = "nomic-embed-text"

os.system("clear")
os.system("rm -rf ./vectordb")
print("Lade E-Mails ...")

pdf_dir = Path("./.data/attachments/pdf/")
pages = []

for pdf_file in pdf_dir.glob("*.pdf"):
    try:
        loader = PyPDFLoader(str(pdf_file))
        loaded_pages = loader.load()
        pages.extend(loaded_pages)
    except FileNotDecryptedError:
        print(f"🔐 PDF verschlüsselt, wird übersprungen: {pdf_file.name}")
    except Exception as e:
        print(f"⚠️ Fehler beim Verarbeiten von {pdf_file.name}: {e}")

# Text aufteilen
text_splitter = RecursiveCharacterTextSplitter(chunk_size=7000, chunk_overlap=1000)
splits = text_splitter.split_documents(pages)

# CSV-Datei später verarbeiten
csv_file = Path('.data/emails.csv')
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    # for row in islice(reader, 10):
    for row in reader:
        # Format each email into a single string
        email_text = f"""
From: {row['from']}
To: {row['to']}
Date: {row['date']}
Subject: {row['subject']}

{row['body']}
"""
        # Optionally include attachments info:
        # if row['pdf_attachments']:
        #     email_text += f"\n[PDF Attachments: {row['pdf_attachments']}]"
        # if row['image_attachments']:
        #     email_text += f"\n[Image Attachments: {row['image_attachments']}]"

        if len(email_text) <= 7000:
            # print(email_text.strip())
            splits.append(Document(page_content=email_text.strip()))
        else:
            print(f"Email von {row['from']} übersprungen, Länge: {len(email_text)}")

os.system("clear")
print(f"Emails und Datein geladen (insgesamt {len(splits)} Splits) - erstelle Datenbank ...")
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)
vectorDB = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory="vectordb")
print("done!")