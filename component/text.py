import customtkinter as ctk

class TextFrame(ctk.CTkFrame):
    def __init__(self, master, title,r,c, v, s):
        super().__init__(master)
        self.master = master
        self.title = title
        self.label = None
        self.r = r
        self.c = c
        self.v = v
        self.s = s

        self.textbox = ctk.CTkEntry(master)
        self.textbox.delete(0, ctk.END)
        self.textbox.insert(0, v) 
        self.textbox.grid(row=r, column=c+1, padx=20, pady=20, sticky="we", columnspan=4)
        if title !="":
            self.label = ctk.CTkLabel(master, text=title, fg_color="transparent")
            self.label.grid(row=r, column=c, padx=20, pady=20, sticky="w")
            self.textbox.grid(row=r, column=c+1, padx=20, pady=20, sticky="w")
        # textbox.insert("0.0", v)  # insert at line 0 character 0
        if s=="disabled":
            self.textbox.configure(state="disabled")  
        # print(self.textbox.get(),"++++++++++++++++",self.title)

    def setSate(self,s):
        self.textbox.configure(state=s)

    def grid_forget(self):
        self.label.grid_forget()
        self.textbox.grid_forget()

    def grid(self):
        if self.label :
            self.label.grid(row=self.r, column=self.c, padx=20, pady=20, sticky="w")

        if self.title != "":
            self.textbox.grid(row=self.r, column=self.c+1, padx=20, pady=20, sticky="w")
        else:
            self.textbox.grid(row=self.r, column=self.c+1, padx=20, pady=20, sticky="we", columnspan=4)

    def get(self):
        # print(self.textbox.get(),"++++++++++++++++",self.title)
        return self.textbox.get()
    
    def setv(self,value):
        self.textbox.delete(0, ctk.END)
        self.textbox.insert(0, value)  # = ctk.CTkEntry(self.master, placeholder_text=value)
        self.grid()