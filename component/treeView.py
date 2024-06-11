import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import threading, queue

class TreeView(ctk.CTk):
    def __init__(self, top, result_queue):
        super().__init__()
        self.result_queue=result_queue

        frame = ctk.CTkFrame(top)
        frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=10)

        scrollbar_y = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        self.tree = ttk.Treeview(frame, columns=( "sequence", "代码", "操作", "开仓时间", "平仓时间", "利润"),  yscrollcommand=scrollbar_y.set)
        scrollbar_y.config(command=self.tree.yview)

        # 设置表头
        self.tree.heading("#0", text="")
        self.tree.heading("sequence", text="", anchor=tk.CENTER)
        self.tree.heading("代码", text="代码")
        self.tree.heading("操作", text="操作")
        self.tree.heading("开仓时间", text="开仓时间")
        self.tree.heading("平仓时间", text="平仓时间")
        self.tree.heading("利润", text="利润")

        # 设置列
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("sequence",  width=0, stretch=tk.NO)
        self.tree.column("代码", anchor=tk.CENTER, width=80)
        self.tree.column("操作", anchor=tk.CENTER, width=100)
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
        try:
            while True:
                r = self.result_queue.get_nowait()
                row=(r["sequence"], r["code"], r["open"], r["open_at"], r["close_at"], "{}".format(r["profit"]))
                for item in self.tree.get_children():
                    item_values = self.tree.item(item, "values")
                    if item_values[0] == r["sequence"]:
                        self.tree.item(item, values = row)
                        return
                self.tree.insert("", "end", values = row)

        except queue.Empty:
            pass
        self.after(500, self.check_queue)
