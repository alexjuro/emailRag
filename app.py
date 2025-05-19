from mboxToCsv import convert
from createRag import create
from rag import rag

while True:
    print("Nenne deinen Input: (1. / 2.)")
    print("\t1. Emails Datei (mbox) entpacken und Email RAG installieren")
    print("\t2. Mit deinen Emails chatten?")
    inp = input(">> ")

    if inp == "1.":
        convert()
        create()
    elif inp == "2.":
        rag()
    else:
        print("Input falsch!")
