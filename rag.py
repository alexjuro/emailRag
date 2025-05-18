from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import ollama
import os
import csv
from pathlib import Path
from pypdf.errors import FileNotDecryptedError

csv.field_size_limit(10 * 1024 * 1024)

EMBEDDING_MODEL_NAME = "nomic-embed-text"
INFERENCE_MODEL_NAME = "gemma3:4b-it-q4_K_M"

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

        # Add to splits
        print(email_text.strip())
        splits.append(email_text.strip())

embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)
vectorDB = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory="vectordb")
retriever = vectorDB.as_retriever(search_type="mmr")

os.system("clear")

while True:
    print("\nNenne deine Frage:")    
    prompt = input()

    retrieved_docs = retriever.invoke(prompt)
    contextFromDB = "\n".join(doc.page_content for doc in retrieved_docs)
    # print("\n\n **************Context For Query*************")
    # print(contextFromDB)
    # print("***********************\n\n")

    response = ollama.chat(model = INFERENCE_MODEL_NAME, messages=[{
        "role": "user",
        "content": f'Du bist mein digitaler Assistent und hast Zugriff auf meine bisherigen E-Mails. Nutze den Inhalt der abgerufenen E-Mails, um meine Frage vollständig und präzise zu beantworten.\nBeziehe dich nur auf E-Mails, wenn sie relevant sind. Gib, wenn möglich, den Absender, den Betreff und das Datum der betreffenden E-Mail an.\nHier ist meine Frage:\n{prompt}\nUnd hier ist der Kontext:\n{contextFromDB}'
    }])
    answer = response["message"]["content"]
    print(f"\n\nAntwort:\n{answer}")