from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import ollama
import os

EMBEDDING_MODEL_NAME = "nomic-embed-text"
INFERENCE_MODEL_NAME = "gemma3:4b-it-q4_K_M"

embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)
vectorDB = Chroma(persist_directory="vectordb", embedding_function=embeddings)
retriever = vectorDB.as_retriever(search_type="mmr", search_kwargs={"k": 5})

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