import customtkinter as ctk

class LabelMenu(ctk.CTkFrame):
    def __init__(self, master, title,r,c, v, s):
        super().__init__(master)
        self.master = master
        self.title = title
        self.label = None
        self.r = r
        self.c = c
        self.v = v
        self.s = s
        if title!="":
            self.label = ctk.CTkLabel(master, text=title)
            self.label.grid(row=r, column=c, padx=20, pady=20, sticky="w")
        self.cbOpen = ctk.CTkOptionMenu(master, values=["Buy", "Sell"])
        self.cbOpen.grid(row=r, column=c+1, padx=20, pady=20, sticky="w")

        if s=="disabled":
            self.cbOpen.configure(state="disabled")  

    def setSate(self,s):
        self.cbOpen.configure(state=s)

    def grid_forget(self):
        self.label.grid_forget()
        self.cbOpen.grid_forget()

    def grid(self):
        if self.label:
            self.label.grid(row=self.r, column=self.c, padx=20, pady=20, sticky="w")
        self.cbOpen.grid(row=self.r, column=self.c+1, padx=20, pady=20, sticky="w")  

    def get(self):
        return self.cbOpen.get()
    
    def setv(self,value):
        self.cbOpen.set(value)
        self.grid()