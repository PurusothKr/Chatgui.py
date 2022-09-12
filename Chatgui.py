import nltk
from nltk.stem import WordNetLemmatizer
lemmatize = WordNetLemmatizer()
import pickle
import numpy as np
from keras.models import load_model
model = load_model('chatbot_model.h5') # the actual model created by train_chatbot.py and used by chatgui.py
import json
import random

intents = json.loads(open('intents.json').read())
classes = pickle.load(open('classes.pkl','rb'))    # a list of different types of classes of responses
words = pickle.load(open('words.pkl','rb'))


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatize.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:

                bag[i] = 1 # assign 1 if current word is in the vocabulary position
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.10
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']  # Intent is a Python library for extracting semantic information from text
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i["tag"]== tag):
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res


#Creating GUI with tkinter
import tkinter
from tkinter import *
#3
def send():                                         # the relation between send button to the entry box
    msg = EntryBox.get("1.0",'end-1c').strip()      # read from one text box Entrybox
    EntryBox.delete("0.0",END)                      # Delete from position 0 till end

    if msg != '':
        ChatLog.config(state=NORMAL) # moves to the next line in a continuation manner

        ChatLog.insert(END, "You : " + msg + '\n\n')
        ChatLog.config(foreground="#a2d5c6", font=("Verdana", 12 ))
        res = chatbot_response(msg)
        ChatLog.insert(END, "JARVIS : " + res + '\n\n\n\n')
        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)
base = Tk()
base.title(" JARVIS ")
base.geometry("400x500")
base.resizable(width=TRUE, height=TRUE)

#Create Chat window
ChatLog = Text(base, bg="#077b8a", height="8", width="50", font="Arial",)
ChatLog.config(state=DISABLED)

#Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart") # to view in y-axis
ChatLog['yscrollcommand'] = scrollbar.set

#Create Button to send message #Create Button to send message
SendButton = Button(base, font=("Cosmic Sans MS",12), text="Send", width="16", height=5,
                    bd=0, bg="#5c3c92", command= send )
#Create the box to enter message
EntryBox = Text(base, bd=0, bg="#fffcec",width="29", height="10", font="Arial")
#EntryBox.bind("<Return>", send)
#Place all components on the screen
scrollbar.place(x=376,y=6, height=386)
ChatLog.place(x=6,y=6, height=386, width=370)
EntryBox.place(x=6, y=390, height=95, width=285)
SendButton.place(x=240, y=390, height=40)
base.mainloop()
