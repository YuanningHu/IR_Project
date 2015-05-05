__author__ = 'Michael'
#UI for dish search
#uses Tkinter package to create the UI, interacts with the search
from Tkinter import *
import search

#master frame
master = Tk()

#label prompt and entry box so that user can enter the query they are looking for
Label(master,text="Enter your query below:").grid(row=0)
entry_query = Entry(master)
entry_query.grid(row=1,column=0)

#button event - takes query and feeds it into the search class, and puts it into a messagebox under the query
def set_query_txt():
    search.q_mw(entry_query.get())
    Message(master,text=open('query_result.txt', 'r')).grid(row=2)

#button to confirm that the entry text should be queried
btn_search = Button(master, text="Enter",command=set_query_txt).grid(row=1,column=1)

#keep looping so that it's not just once instance of the program
mainloop()
