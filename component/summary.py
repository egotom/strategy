from .stockData import *
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import json, time, random, math
import threading, queue, re
from datetime import datetime, timezone, tzinfo, timedelta

class SummaryView(ctk.CTkToplevel):
    def __init__(self, result_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x600")
        self.title("策略汇总")

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
        print("Summary:\t", task["sequence"], "\t", task["code"], "\t", task["open"], "\t", task["trigger"], "\t", task["close"])
        # sleep_time = random.uniform(0, 5)
        # time.sleep(sleep_time)
        data=getData(task)
        if data is not None:
            (task["open_at"], task["open_value"])=judge(task["trigger"], data)
            if task["open_at"] == "" or task["open_value"] == "":
                continue
            else:
                q.put(task)
            # (task["close_at"], task["close_value"])=judge(task["close"], data)
            # if task["close_value"] == "" or task["close_at"] == "":
            #     continue
            # else:
            #     q.put(task)
            # factor = 1 if task["open"] == "Buy" else -1
            # task["profit"] = factor * ( task["close_value"] - task["open_value"] ) * float(task["quantity"])
            # q.put(task)
        print("Done")

def judge(state, df):
    expression = ""
    period = {'1m':1,'5m':5,'15m':15,'30m':30,'60m':60,'1d':1440,'1w':10080}
    dfp = (df.index[1] - df.index[0]).total_seconds()/60
    # print(dfp)
    for it in state:
        pn = 0
        p=it.split(" ")
        if len(p)<4 or p[0] not in ["and", "or", "not"] or p[1] not in ["=", ">", "<", "+", "-"]:
            continue 
        if p[1] in ["+", "-"] and p[3] not in ['5m','15m','30m','60m','1d','1w']:
            continue 
        if p[1] in ["=", ">", "<"] and p[3] !="":
            continue 
            
        if p[1] ==">":
            expression = expression + f"{p[0]} LOW {p[1]} {p[2]} "
        if p[1] =="<":
            expression = expression + f"{p[0]} HIGH {p[1]} {p[2]} "
        if p[1] == "=":
            expression = expression + f"{p[0]} HIGH > {p[2]} and {p[2]} > LOW "
        if p[1] in ["+","-"]:
            if dfp > period[p[3]]:
                continue 
            else:
                pn = math.ceil(period[p[3]] / dfp)
        if p[1] == "+":
            expression = expression + f"{p[0]} RISE-{pn} > {p[2]} "
        if p[1] == "-":
            expression = expression + f"{p[0]} FALL-{pn} > {p[2]} "

    if len(expression) < 4:
        return ("", "")

    if expression[:3] == "and":
        expression=expression[3:]
    if expression[:2] == "or":
        expression ="False "+expression

    rise=[0,0]
    rer=re.findall(r'RISE-(\d+)', expression)
    if len(rer)>0:
        rise[0]=int(rer[0])
    fall=[0,0]
    ref=re.findall(r'FALL-(\d+)', expression)
    if len(ref)>0:
        fall[0]=int(ref[0])
    stack=[]
    # print(rise, fall,"===============",expression)
    for id, row in df.iterrows():
        express = expression
        express = express.replace("LOW", str(row["low"])).replace("HIGH", str(row["high"]))

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
            
        print(express, "\t----------------", stack )
        try:
            if eval(express):
                exps = express.split(" ")
                for index, exp in enumerate(exps):
                    if exp in ["<",">"]:
                        return (id, float(exps[index+1]))
                    
        except Exception as e:
            continue

    return ("", "")

def stateTest(exp):

def calculate_minutes_between(datetime_str1, datetime_str2, date_format ):
    dfs=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M"]
    dfs.insert(0,date_format)
    for df in dfs:
        try:
            datetime1 = datetime.strptime(datetime_str1, df)
            datetime2 = datetime.strptime(datetime_str2, df)
            delta = datetime1 - datetime2
            return abs(delta.total_seconds() / 60)
        except Exception as e:
            print(e)
            
    return None

def getData(order):
    period = {'1m':1,'5m':5,'15m':15,'30m':30,'60m':60,'1d':1440,'1w':10080}
    minutes=calculate_minutes_between(order["created"], order["expiry"],"")
    if minutes is None:
        return None
    df=None
    for key, value in period.items():
        ct= math.floor( minutes/value )
        print(key, ct)
        df=get_price(order["code"], frequency=key, count=ct)
        if ct < df.shape[0]+2:
            break
        df=None
    return df 

if __name__ == "__main__":
    states=[
        ["or < 200 ", "or = 400 ", "and + 20 15m", "and = 300 "],
    ]
    df=get_price("000001.XSHG", frequency="5m", count=1000)
    for state in states:
        (at,value)=judge(state, df)
        print("====",at, value)