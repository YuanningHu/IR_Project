__author__ = 'Michael'
from Tkinter import *

master = Tk()

Label(master,text="Enter your query below:").grid(row=0)
query = Entry(master)
query.grid(row=1,column=0)


btn_search = Button(master, text="Enter",command=).grid(row=1,column=1)




msg = Message(master,text="Results will go here").grid(row=2)

mainloop()
x = StringVar()#use this to hold the final - make this the final result




#class simpleapp_tk(Tkinter.Tk):
 #   def __init__(self,parent):
  #      Tkinter.Tk.__init__(self,parent)
   #     self.parent = parent
    #    self.initialize()

    #def initialize(self):
       # self.grid()
        #self.entry = Tkinter.Entry(self)
        #self.entry.grid(column=0,row=0,sticky="EW")

        #label = Tkinter.Label(self,text ="Ranking goes here")
        #label.grid(column =0,row=1)

        #button = Tkinter.Button(self,text=u"TEST")
        #button.grid(column=1,row=0)

        #self.grid_columnconfigure(0,weight=1)
        #self.grid_rowconfigure(0,weight=1)






if __name__ == "__main__":
    app = simpleapp_tk(None)
    app.title('my application')
    app.mainloop()
