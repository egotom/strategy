import customtkinter as ctk
from tkinter import messagebox 
from component import *
import uuid
import json
from datetime import datetime
import threading, queue, time

ctk.set_appearance_mode("dark")     #   "system"   "light"
app = ctk.CTk()
app.geometry("1300x800")
app.title("证券交易策略编辑器   V1.0")
isNew=True
saved=["created","open_at","close_at","open_value","close_value","profit"]
order={
    "sequence":str(uuid.uuid4()),
    "code":"",
    "open":"",
    "trigger":[],
    "close":[],
    "quantity":1,
    "expiry":"",
    "created":"",
    "open_at":"",
    "close_at":"",
    "open_value":0,
    "close_value":0,
    "profit":0
}

os=[]
sq=[]
entries={}

def loadData():
    global os,sq
    fr=open("data.txt","r")
    lines = fr.read()
    fr.close()
    if lines=="":
        lines="[]"
    os=json.loads(lines)
    sq=[]
    for o in os:
        sq.append(o["sequence"])

loadData()
def addCondition():
    tTrigger=ttCondition.get()
    parm = set(tTrigger.split(" "))
    if "" in parm:
        parm.remove("")
    if len(parm)<3:
        messagebox.showerror("错误！", "缺少条件参数。")  
        return 

    if len(parm)<4 and ("+" in parm or "-" in parm):
        messagebox.showerror("错误！", "缺少条件参数。")  
        return 

    order["trigger"].append(tTrigger)
    order["trigger"]=list(set(order["trigger"]))
    entries["trigger"].setv(json.dumps(order["trigger"]))

def addClose():
    ttc=ttClose.get()
    parm = set(ttc.split(" "))
    if "" in parm:
        parm.remove("")
    if len(parm)<3:
        messagebox.showerror("错误！", "缺少条件参数。")  
        return 

    if len(parm)<4 and ("+" in parm or "-" in parm):
        messagebox.showerror("错误！", "缺少条件参数。")  
        return 

    order["close"].append(ttc)
    order["close"]=list(set(order["close"]))
    entries["close"].setv(json.dumps(order["close"]))

def loadOrder(choice):
    global order, entries,isNew
    for o in os:
        if o["sequence"]==choice:
            btnCreater.configure(text="新建策略")
            order=o
            isNew=False
            btnCondition.configure(state="disabled")
            btnCondition2.configure(state="disabled")
            btnDelete.configure(state="normal")
            for key in entries.keys():
                entries[key].setv(order[key])
                entries[key].setSate("disabled")
            return

def createOrder():
    global os, order, entries, isNew
    if not isNew:
        newOrder()
        btnCreater.configure(text="保存策略")
        return

    for key in entries.keys():
        order[key] = entries[key].get()
    order["created"] = datetime.now().isoformat(timespec='minutes') 
    # print("----6666666666666666------", order)
    if order["code"] == "" or order["open"] not in ["Sell","Buy"] or len(order["trigger"])<1:
        messagebox.showerror("错误！", "缺少条件参数。")  
        return 
    
    # print("-----------", order)
    os.append(order)
    fw=open("data.txt","w")
    json.dump(os,fw)
    fw.close()
    messagebox.showinfo("成功！", "保存策略成功。")
    loadData()
    newOrder()
    combobox.configure(values=sq)

def deleteOrder():
    global os, sq, order
    fw=open("data.txt","w")
    for o in os:
        if o["sequence"]==order["sequence"]:
            os.remove(o)
            sq.remove(order["sequence"])
    json.dump(os,fw)
    fw.close()
    loadData()
    newOrder()
    combobox.configure(values=sq)
    btnDelete.configure(state="disabled")

Summary_window=None
def summaryOrder():
    global Summary_window, result_queue
    if Summary_window is None or not Summary_window.winfo_exists():
        Summary_window = SummaryView(app, result_queue)  # create window if its None or destroyed
        # TreeView(Summary_window, result_queue)
        Summary_window.focus()
    else:
        Summary_window.focus()

def newOrder():
    global os, order, entries
    order ={
        "sequence":str(uuid.uuid4()),
        "code":"",
        "open":"",
        "trigger":[],
        "close":[],
        "quantity":1,
        "expiry":"",
        "created":"",
        "open_at":"",
        "close_at":"",
        "open_value":0,
        "close_value":0,
        "profit":0
    }
    for key in entries.keys():
        entries[key].setSate("normal")
        if key in saved:
            entries[key].grid_forget()
        else:
            entries[key].setv(order[key])
            entries[key].grid()
    btnCondition.configure(state="normal")
    btnCondition2.configure(state="normal")
    btnCreater.configure(text="保存策略")

entries["sequence"]=TextFrame(app,title="序列号", r=0, c=3, v=order["sequence"], s="disabled")
entries["code"]=TextFrame(app, title="证券代码", r=0, c=0, v=order["code"], s="")
entries["open"]=LabelMenu(app, title="", r=2, c=0, v=order["open"], s="")
ttCondition = ConditionFrame(app, title="开仓", r=2, c=0)
entries["trigger"] = TextList(app, r=3, c=0, v=order["trigger"])
btnCondition = ctk.CTkButton(app, text="添加", command=addCondition)
btnCondition.grid(row=3, column=5, padx=20, pady=20, sticky="w")
ttClose = ConditionFrame(app, title="平仓", r=4, c=0)
entries["close"] = TextList(app, r=5, c=0, v=order["close"])
btnCondition2 = ctk.CTkButton(app, text="添加", command=addClose)
btnCondition2.grid(row=5, column=5, padx=20, pady=20, sticky="w")
entries["quantity"]= TextFrame(app, title="数量", r=6, c=0, v=order["quantity"], s="")
entries["expiry"]= TextFrame(app, title="有效期至", r=6, c=3, v=order["expiry"], s="")
entries["created"]=TextFrame(app, title="创建日期", r=7, c=0, v=order["created"], s="disabled")
entries["open_at"]=TextFrame(app, title="开仓日期", r=7, c=3, v=order["open_at"], s="disabled")
entries["close_at"]=TextFrame(app, title="平仓日期", r=8, c=0, v=order["close_at"], s="disabled")
entries["open_value"]=TextFrame(app, title="开仓价格", r=8, c=3, v=order["open_value"], s="disabled")
entries["close_value"]=TextFrame(app, title="平仓价格", r=9, c=0, v=order["close_value"], s="disabled")
entries["profit"]=TextFrame(app, title="利润", r=9, c=3, v=order["profit"], s="disabled")

combobox_var = ctk.StringVar(value="")
combobox = ctk.CTkOptionMenu(app, values=sq, command=loadOrder, variable=combobox_var)
combobox.grid(row=11, column=2, padx=20, pady=20, sticky="we")
combobox_var.set("")

btnSummary = ctk.CTkButton(app, text="策略汇总", command=summaryOrder,state="")
btnSummary.grid(row=11, column=3, padx=20, pady=20, sticky="w")
btnDelete = ctk.CTkButton(app, text="删除策略", command=deleteOrder,state="disabled")
btnDelete.grid(row=11, column=4, padx=20, pady=20, sticky="w")
btnCreater = ctk.CTkButton(app, text="保存策略", command=createOrder)
btnCreater.grid(row=11, column=5, padx=20, pady=20, sticky="w")

newOrder()

result_queue = queue.Queue()
threading.Thread(target=Summary, args=(result_queue,), daemon=True).start()

# def check_queue():
#     try:
#         while True:
#             result = result_queue.get_nowait()
#             print(result)
#     except queue.Empty:
#         pass
#     app.after(100, check_queue)
# check_queue()
try:
    app.mainloop()
except Exception as e:
    print("app.mainloop(): ", e)