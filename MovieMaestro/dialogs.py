import tkinter as tk
from tkinter import messagebox

class Dialogs:
    @staticmethod
    def show_error(title, message):
        messagebox.showerror(title, message)

    @staticmethod
    def show_info(title, message):
        messagebox.showinfo(title, message)

    @staticmethod
    def ask_yes_no(title, question):
        result = messagebox.askquestion(title, question)
        return result == 'yes'

    @staticmethod
    def ask_integer(title, question):
        answer = tk.simpledialog.askinteger(title, question)
        return answer

    @staticmethod
    def ask_string(title, question):
        answer = tk.simpledialog.askstring(title, question)
        return answer
