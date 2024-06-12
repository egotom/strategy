from .stockData import *
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import json, time, random, math
import threading, queue, re
from datetime import datetime, timezone, tzinfo, timedelta
import pprint
import pandas as pd  

class SummaryView(ctk.CTkToplevel):
    def __init__(self, result_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x600")
        self.title("策略汇总")

        self.result_queue=result_queue
        frame = ctk.CTkFrame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=10)

        scrollbar_y = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        self.tree = ttk.Treeview(frame, columns=( "sequence", "代码", "操作", "数量", "开仓时间", "平仓时间", "利润"),  yscrollcommand=scrollbar_y.set)
        scrollbar_y.config(command=self.tree.yview)

        # 设置表头
        self.tree.heading("#0", text="")
        self.tree.heading("sequence", text="", anchor=tk.CENTER)
        self.tree.heading("代码", text="代码")
        self.tree.heading("操作", text="操作")
        self.tree.heading("数量", text="数量")
        self.tree.heading("开仓时间", text="开仓时间")
        self.tree.heading("平仓时间", text="平仓时间")
        self.tree.heading("利润", text="利润")

        # 设置列
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("sequence",  width=0, stretch=tk.NO)
        self.tree.column("代码", anchor=tk.CENTER, width=80)
        self.tree.column("操作", anchor=tk.CENTER, width=80)
        self.tree.column("数量", anchor=tk.CENTER, width=80)
        self.tree.column("开仓时间", anchor=tk.CENTER, width=150)
        self.tree.column("平仓时间", anchor=tk.CENTER, width=150)
        self.tree.column("利润", anchor=tk.CENTER, width=100)

        # 放置滚动条和表格
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        # 配置表格框架的网格
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.check_queue()

    def check_queue(self):
        print("+++++++++++777777777777++++++++++++")
        # while True:
        try:
            r = self.result_queue.get_nowait()
            print("+++++++++++++++++++++++")
            row=(r["sequence"], r["code"], r["open"], r["quantity"], r["open_at"], r["close_at"], r["profit"])
            for item in self.tree.get_children():
                item_values = self.tree.item(item, "values")
                if item_values[0] == r["sequence"]:
                    self.tree.item(item, values = row)
                    return
            self.tree.insert("", "end", values = row)

        except Exception as e:
            print("TreeView.check_queue(): ",e)
        self.after(1000, self.check_queue)

def Summary(q):
    fp=open("data.txt","r+")
    txt=fp.read()
    fp.close()
    if len(txt)<10:
        return 
    tasks= json.loads(txt)
    for task in tasks:
        q.put(task)
    for task in tasks:
        print("\n\nSummary:\t", task["sequence"], "\t", task["code"], "\t", task["open"], "\t", task["trigger"], "\t", task["close"])
        # sleep_time = random.uniform(0, 5)
        # time.sleep(sleep_time)
        data=getData(task)
        if data is not None:
            (task["open_at"], task["open_value"])=judge(task["trigger"], data)
            if task["open_at"] == "" or task["open_value"] == "":
                continue
            else:
                q.put(task)
            data = data.loc[task["open_at"]:]
            (task["close_at"], task["close_value"])=judge(task["close"], data)
            if task["close_value"] == "" or task["close_at"] == "":
                continue
            else:
                q.put(task)
            factor = 1 if task["open"] == "Buy" else -1
            task["profit"] = round(factor * ( task["close_value"] - task["open_value"] ) * float(task["quantity"]), 2)
            q.put(task)
            pprint.pprint(task)

    print("\nDone")
    # pprint.pprint(tasks)

def judge(state, df):
    expression = {"and":[], "or":[]}
    period = {'1m':1,'5m':5,'15m':15,'30m':30,'60m':60,'1d':240,'1w':1200,'1M':7200}
    dfp = (df.index[1] - df.index[0]).total_seconds()/60
    # print(dfp)
    for it in state:
        pn = 0
        p=it.split(" ")
        # print(it,"........",p)
        if len(p)<4 or p[0] not in ["and", "or"] or p[1] not in ["=", ">", "<", "+", "-"]:
            continue 
        if p[1] in ["+", "-"] and p[3] not in ['5m','15m','30m','60m','1d','1w']:
            continue 
        if p[1] in ["=", ">", "<"] and p[3] !="":
            continue 
        if p[1] ==">":
            tmp = f"LOW {p[1]} {p[2]} "
        if p[1] =="<":
            tmp = f"HIGH {p[1]} {p[2]} "
        if p[1] == "=":
            tmp = f"HIGH > {p[2]} and {p[2]} > LOW "
        if p[1] in ["+","-"]:
            if dfp > period[p[3]]:
                continue 
            else:
                pn = math.ceil(period[p[3]] / dfp)
        if p[1] == "+":
            tmp = f"RISE-{pn} > {p[2]} "
        if p[1] == "-":
            tmp = f"{p[0]} FALL-{pn} > {p[2]} "
        if p[0] == "and":
            expression["and"].append(tmp)
        if p[0] == "or":
            expression["or"].append(tmp)
        # print(expression,"........")

    if len(expression["and"]) < 1 and len(expression["or"]) < 1:
        return ("", "")

    stack=[]
    rise=[0, 0]
    fall=[0, 0]
    mgs=expression["and"] + expression["or"] 
    for it in  mgs:
        rer=re.findall(r'RISE-(\d+)', it)
        if len(rer)>0:
            rise[0]=int(rer[0])
        
        ref=re.findall(r'FALL-(\d+)', it)
        if len(ref)>0:
            fall[0]=int(ref[0])

    # print(rise, fall,"===============",expression)
    for id, row in df.iterrows():
        # print(id )
        allAnd = True
        retv = ""
        for tt, its in  expression.items():
            for it in its:
                express = it.replace("LOW", str(row["low"])).replace("HIGH", str(row["high"]))
                if rise[0] or fall[0]:
                    mean = row[['open','high','low','close']].mean()
                    stack.append(mean)
                    if rise[0]:
                        # print("-------------", rise[0])
                        rValue = mean - min(stack[:rise[0]])
                        express = re.sub(r'RISE-\d+', str(rValue), express)

                    if fall[0]:
                        fValue = max(stack[:fall[0]]) - mean
                        express = re.sub(r'FALL-\d+', str(fValue), express)

                    if len(stack) > rise[0] and len(stack)>fall[0]:
                        stack=stack[1:]

                # print(express, "\t----------------", stack )
                optn=re.findall(r'(-?\d+\.?\d+)', express)
                if len(optn)>1:
                    if " and " in express:
                        retv=float(optn[1])
                    else: 
                        retv=float(optn[0])
                else:
                    continue
                try:
                    if eval(express):
                        # print(express,True,tt)
                        if tt=="or":
                            print(id, "\tat: ",retv, "\tLow:",row["low"], "\tHigh: ",row["low"], "\tregex: ",it)
                            return (id, retv)
                        else:
                            continue
                    else:
                        if tt=="and":
                            allAnd = False
                            # print(allAnd,"----->>>>>>>>>>>>>>>--------")
                            break
                except Exception as e:
                    print(e)

            if not allAnd:
                break
        if allAnd:
            print(id, "\tat: ", retv, "\tLow:",row["low"], "\tHigh: ",row["low"], "\tregex: ",it)
            return (id, retv)
    return ("", "")

def str2timestamp(date_str, date_format=""):
    dfs=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M"]
    if date_format != "":
        dfs.insert(0,date_format)

    for df in dfs:
        try:
            return pd.to_datetime(date_str, format=df)
        except Exception as e:
            print("str2timestamp: ",e)
    return None
    
def getData(order):
    period = {'1m':1,'5m':5,'15m':15,'30m':30,'60m':60,'1d':240,'1w':1200,'1M':7200}
    start = str2timestamp(order["created"])
    end = str2timestamp(order["expiry"])
    if start is None or end is None:
        return None
    df=None
    # print(start, "---------------",  end)
    for key, value in period.items():
        df=get_price(order["code"], frequency=key, count=99999999)
        # print(key, df.shape, df.index[0] )
        # print(df.iloc[:3])
        if df.index[0] < start:
            df=df.loc[start:end]
            # print(df)
            break
        df=None
    return df 

if __name__ == "__main__":
    tasks = [{
		"sequence": "eaf2f7ed-5213-451a-b2b6-3d0acb36aac2",
		"code": "000001.XSHG",
		"open": "Sell",
		"trigger": ["and = 3080 "],
		"close": ["and = 3051 "],
		"quantity": "3",
		"expiry": "2024-06-07T17:18",
		"created": "2024-06-01T17:18",
		"open_at": "",
		"close_at": "",
		"open_value": "0",
		"close_value": "0",
		"profit": "0"
	},{
		"sequence": "111111-5213-451a-b2b6-3d0acb36aac2",
		"code": "000001.XSHG",
		"open": "Buy",
		"trigger": ["and < 2970 "],
		"close": ["and > 3050 "],
		"quantity": "1",
		"expiry": "2024-06-07T17:18",
		"created": "2024-01-01T17:18",
		"open_at": "",
		"close_at": "",
		"open_value": "0",
		"close_value": "0",
		"profit": "0"
	}]
    for task in tasks:
        print("\n\nSummary:\t", task["sequence"], "\t", task["code"], "\t", task["open"], "\t", task["trigger"], "\t", task["close"])
        data=getData(task)
        if data is not None:
            (task["open_at"], task["open_value"])=judge(task["trigger"], data)
            if task["open_at"] == "" or task["open_value"] == "":
                continue
            # else:
            #     q.put(task)
            data = data.loc[task["open_at"]:]
            (task["close_at"], task["close_value"])=judge(task["close"], data)
            if task["close_value"] == "" or task["close_at"] == "":
                continue
            # else:
            #     q.put(task)
            factor = 1 if task["open"] == "Buy" else -1
            task["profit"] = factor * ( task["close_value"] - task["open_value"] ) * float(task["quantity"])
            # pprint.pprint(task)
    pprint.pprint(tasks)