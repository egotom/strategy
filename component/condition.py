import customtkinter as ctk

class ConditionFrame(ctk.CTkFrame):
    def __init__(self, master, title,r,c):
        super().__init__(master)
        self.r=r 
        self.c=c
        self.cbPeriod=None
        label = ctk.CTkLabel(master, text=title)
        label.grid(row=r, column=c, padx=20, pady=20, sticky="w")

        self.cbOpt = ctk.CTkOptionMenu(master, values=["and", "or", "not"])
        self.cbOpt.grid(row=r, column=c+2, padx=20, pady=20, sticky="w")

        self.cbOpt2 = ctk.CTkOptionMenu(master, values=["=", ">", "<", "+", "-"], command=self.addCBPeriod)
        self.cbOpt2.grid(row=r, column=c+3, padx=20, pady=20, sticky="w")

        self.ttQty = ctk.CTkEntry(master)
        self.ttQty.grid(row=r, column=c+4, padx=20, pady=20, sticky="w")

    def addCBPeriod(self, opt):
        if opt in ["+","-"]:
            self.cbPeriod = ctk.CTkOptionMenu(self.master, values=['5m','15m','30m','60m','1d','1w'])
            self.cbPeriod.grid(row=self.r, column=self.c+5, padx=20, pady=20, sticky="w")
        if opt not in ["+","-"] and self.cbPeriod:
            self.cbPeriod.grid_forget()

    def get(self):
        p=""
        if self.cbPeriod and self.cbOpt2.get() in ["+","-"]:
            p=self.cbPeriod.get()
        return f"{self.cbOpt.get()} {self.cbOpt2.get()} {self.ttQty.get()} {p}"