import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import main

# 创建窗口
root = tk.Tk()
root.title("WELCOME")

# 设置窗口尺寸和位置
window_width = 500
window_height = 480
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# 使用PIL库调整图片大小
original_image = Image.open("pic.png")  # 替换成你的背景图片路径
resized_image = original_image.resize((window_width, window_height), Image.ANTIALIAS)
bg_image = ImageTk.PhotoImage(resized_image)

# 创建Label组件显示背景图片
background_label = tk.Label(root, image=bg_image)
background_label.place(relx=0.5, rely=0.5, anchor="center")

# 创建半透明输入框样式
style = ttk.Style()
style.theme_use('clam')  # 使用'clam'主题
style.configure('Transparent.TEntry', fieldbackground='gray80')  # 设置输入框背景为半透明灰色

# 创建半透明输入框
entry = ttk.Entry(root, style='Transparent.TEntry')
entry.place(relx=0.5, rely=0.8, relwidth=0.3, anchor="center")  # 设置输入框位置
entry.focus()  # 让输入框获取焦点

# 创建按钮
def on_enter_button(event=None):
    on_enter()

button_enter = tk.Button(root, text="Enter", command=on_enter_button)
button_enter.place(relx=0.5, rely=0.88, anchor="center")

# 定义回车键事件处理函数
def on_enter(event=None):
    password = entry.get()
    if password == "mysql":  # 替换成你设置的密码
        root.destroy()  # 关闭登录窗口
        messagebox.showinfo("欢迎", "欢迎进入学生成绩信息管理系统！")
        main.main()  # 打开主界面
    else:
        messagebox.showerror("登录失败", "密码错误")

# 绑定回车键与事件处理函数
root.bind('<Return>', on_enter)

# 运行窗口
root.mainloop()
