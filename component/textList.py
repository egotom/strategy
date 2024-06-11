import customtkinter as ctk
import json

class TextList(ctk.CTkFrame):
    def __init__(self, master,r,c, v):
        super().__init__(master)
        self.master = master
        self.r = r
        self.c = c
        self.v = v

        self.textbox = ctk.CTkLabel(master, text=v, font=("Arial", 18), text_color="#00ff00")
        self.textbox.grid(row=r, column=c+1, padx=20, pady=20, sticky="we", columnspan=4)
 
    def setSate(self,s):
        pass

    def grid_forget(self):
        self.textbox.grid_forget()

    def grid(self):
        self.textbox.grid(row=self.r, column=self.c+1, padx=20, pady=20, sticky="we", columnspan=4)

    def get(self):
        tx = self.textbox.cget("text")
        if len(tx)<3:
            return []
        # print(tx,"=======", type(tx))
        return json.loads(tx)
    
    def setv(self, value):
        self.textbox.configure(text=value)
        self.grid()