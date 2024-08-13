import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from db import get_connection, fetch_students, fetch_student_course_records, fetch_student_grades, delete_grade, \
    check_student_exists, check_course_exists, add_grade


entry_student_id = None
entry_course_id = None
entry_grade = None
entry_student_id_delete = None
entry_student_id_update = None
entry_new_student_id = None
entry_grade_id = None
tree_grades_realtime = None
entry_grade_id_delete = None
column_names = None  # 存储列名
tree_student_courses = None  # 新增的Treeview
label_total_credits = None  # 显示总学分Label
label_avg_grade = None  # 显示平均成绩Label


def on_delete():
    student_id = entry_student_id_delete.get()
    if not student_id:
        messagebox.showwarning("输入错误", "请输入学生ID.")
        return

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            connection.begin()

            sql_delete_students = "DELETE FROM Student WHERE student_id = %s"
            cursor.execute(sql_delete_students, (student_id,))

            sql_delete_grades = "DELETE FROM Grade WHERE student_id = %s"
            cursor.execute(sql_delete_grades, (student_id,))

            fetch_students()
            on_query()

            connection.commit()

            messagebox.showinfo("删除成功", "学生信息删除成功.")
    except Exception as e:

        connection.rollback()
        messagebox.showerror("错误", f"删除学生时发生错误: {str(e)}")
    finally:
        connection.close()


def on_delete_grade():
    grade_id = entry_grade_id_delete.get()
    if not grade_id:
        messagebox.showwarning("输入错误", "请输入成绩ID.")
        return
    connection = get_connection()
    try:
        with connection.cursor() as cursor:

            connection.begin()

            delete_grade(grade_id)

            on_query()

            connection.commit()

            messagebox.showinfo("删除成功", "成绩记录删除成功.")
    except Exception as e:
        # 如果发生异常，则回滚事务
        connection.rollback()
        messagebox.showerror("错误", f"删除成绩时发生错误: {str(e)}")
    finally:
        connection.close()


def on_add():
    student_id = entry_student_id.get()
    course_id = entry_course_id.get()
    grade = entry_grade.get().upper()  # 转换为大写
    grade_id = entry_grade_id.get()
    if not all([student_id, course_id, grade, grade_id]):
        messagebox.showwarning("输入错误", "请填写所有字段.")
        return
    if grade not in ['A', 'B', 'C', 'D']:
        messagebox.showwarning("输入错误", "成绩必须是 A、B、C 或 D.")
        return
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # 检查学生ID和课程ID是否存在
            if not check_student_exists(student_id):
                messagebox.showerror("错误", "学生ID不存在.")
                return
            if not check_course_exists(course_id):
                messagebox.showerror("错误", "课程ID不存在.")
                return

            # 获取学生姓名和课程名称
            cursor.execute("SELECT name FROM Student WHERE student_id = %s", (student_id,))
            student_name = cursor.fetchone()['name']

            cursor.execute("SELECT course_name FROM Course WHERE course_id = %s", (course_id,))
            course_name = cursor.fetchone()['course_name']

            add_grade(grade_id, student_id, student_name, course_id, course_name, grade) #调用触发器

            messagebox.showinfo("添加成功", "成绩添加成功.")

            on_query()
    except Exception as e:
        messagebox.showerror("错误", f"添加成绩时发生错误: {str(e)}")
    finally:
        connection.close()

def call_update_student_id_proc(old_student_id, new_student_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.callproc('update_student_id_proc', (old_student_id, new_student_id))
            connection.commit()
            print("学号更新成功.")
            return True
    except Exception as e:
        connection.rollback()
        print(f"更新学号时发生错误: {str(e)}")
        return str(e)
    finally:
        connection.close()



def on_update():
    old_student_id = entry_student_id.get()
    new_student_id = entry_new_student_id.get()
    if not all([old_student_id, new_student_id]):
        messagebox.showwarning("输入错误", "请输入旧学号和新学号.")
        return

    try:
        old_student_id_int = int(old_student_id)
        new_student_id_int = int(new_student_id)
        if not (1 <= old_student_id_int <= 99) or not (1 <= new_student_id_int <= 99):
            messagebox.showwarning("输入错误", "学号必须是1到99之间的整数.")
            return
    except ValueError:
        messagebox.showwarning("输入错误", "学号必须是1到99之间的整数.")
        return

    # 调用存储过程更新学号
    result = call_update_student_id_proc(old_student_id_int, new_student_id_int)
    if result is True:
        messagebox.showinfo("修改成功", "学号修改成功.")
    else:
        messagebox.showerror("修改失败", f"学号修改失败: {result}")

    fetch_students()
    on_query()



def fetch_grade_column_names():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM Grade")
            columns = cursor.fetchall()
            column_names = [column['Field'] for column in columns]
            return column_names
    finally:
        connection.close()

def on_query():

    # 获取 Grade 表的实时数据并展示在列表框中
    grades = fetch_student_grades()
    tree_grades_realtime.delete(*tree_grades_realtime.get_children())  # 清空 Treeview 中的数据

    # 添加数据
    for grade in grades:
        row_data = [grade[col] for col in column_names]
        tree_grades_realtime.insert('', 'end', values=row_data)


def on_query_student_courses():

    student_id = entry_student_id.get()
    if not student_id:
        messagebox.showwarning("输入错误", "请输入学生ID.")
        return

    records, total_credits, avg_grade = fetch_student_course_records(student_id)

    tree_student_courses.delete(*tree_student_courses.get_children())


    for record in records:
        row_data = [
            record['student_id'],
            record['name'],
            record['course_id'],
            record['course_name'],
            record['credits'],
            record['grade']
        ]
        tree_student_courses.insert('', 'end', values=row_data)

    # 更新总学分和平均成绩的显示
    label_total_credits.config(text=f"总学分: {total_credits}")
    label_avg_grade.config(text=f"平均成绩: {avg_grade:.2f}")



def main():
    global entry_student_id, entry_course_id, entry_grade, entry_student_id_delete, entry_grade_id_delete, entry_student_id_update, entry_new_student_id, entry_grade_id, tree_grades_realtime, column_names,tree_student_courses,label_avg_grade,label_total_credits

    root = tk.Tk()
    root.title("学生信息管理系统")

    # 学生信息和实时成绩展示布局
    frame_left = tk.Frame(root)
    frame_left.grid(row=0, column=0, padx=10, pady=10)

    frame_right = tk.Frame(root)
    frame_right.grid(row=0, column=1, padx=10, pady=10)

    # 学生信息管理部分
    label_student_id = tk.Label(frame_left, text="学生ID:")
    label_student_id.grid(row=0, column=0, padx=10, pady=10)

    entry_student_id = tk.Entry(frame_left)
    entry_student_id.grid(row=0, column=1, padx=10, pady=10)

    label_new_student_id = tk.Label(frame_left, text="新学生ID:")
    label_new_student_id.grid(row=1, column=0, padx=10, pady=10)

    entry_new_student_id = tk.Entry(frame_left)
    entry_new_student_id.grid(row=1, column=1, padx=10, pady=10)

    button_update = tk.Button(frame_left, text="修改学号", command=on_update)
    button_update.grid(row=1, column=2, padx=10, pady=10)

    label_course_id = tk.Label(frame_left, text="课程ID:")
    label_course_id.grid(row=2, column=0, padx=10, pady=10)

    entry_course_id = tk.Entry(frame_left)
    entry_course_id.grid(row=2, column=1, padx=10, pady=10)

    label_grade = tk.Label(frame_left, text="成绩 (A/B/C/D):")
    label_grade.grid(row=3, column=0, padx=10, pady=10)

    entry_grade = tk.Entry(frame_left)
    entry_grade.grid(row=3, column=1, padx=10, pady=10)

    label_grade_id = tk.Label(frame_left, text="成绩ID:")
    label_grade_id.grid(row=4, column=0, padx=10, pady=10)

    entry_grade_id = tk.Entry(frame_left)
    entry_grade_id.grid(row=4, column=1, padx=10, pady=10)

    button_add = tk.Button(frame_left, text="添加成绩", command=on_add)
    button_add.grid(row=4, column=2, padx=10, pady=10)

    label_delete = tk.Label(frame_left, text="按学生ID删除:")
    label_delete.grid(row=5, column=0, padx=10, pady=10)

    entry_student_id_delete = tk.Entry(frame_left)
    entry_student_id_delete.grid(row=5, column=1, padx=10, pady=10)

    button_delete = tk.Button(frame_left, text="删除", command=on_delete)
    button_delete.grid(row=5, column=2, padx=10, pady=10)

    label_grade_id_delete = tk.Label(frame_left, text="按成绩ID删除:")
    label_grade_id_delete.grid(row=6, column=0, padx=10, pady=10)

    entry_grade_id_delete = tk.Entry(frame_left)
    entry_grade_id_delete.grid(row=6, column=1, padx=10, pady=10)

    button_delete_grade = tk.Button(frame_left, text="删除成绩", command=on_delete_grade)
    button_delete_grade.grid(row=6, column=2, padx=10, pady=10)

    button_refresh = tk.Button(frame_left, text="刷新", command=on_query)
    button_refresh.grid(row=7, column=1, padx=10, pady=10)

    button_query_courses = tk.Button(frame_left, text="查询", command=on_query_student_courses)
    button_query_courses.grid(row=9, column=2, padx=10, pady=10)

    label_total_credits = tk.Label(frame_left, text="总学分: ")
    label_total_credits.grid(row=9, column=0, padx=10, pady=10)

    label_avg_grade = tk.Label(frame_left, text="平均成绩: ")
    label_avg_grade.grid(row=9, column=1, padx=10, pady=10)

    # 创建表格型的列表框，用于实时展示 Grade 表内容
    tree_grades_realtime = ttk.Treeview(frame_right)
    tree_grades_realtime.grid(row=0, column=0, padx=10, pady=10)

    # 添加数据展示区域的滚动条
    scroll_y = ttk.Scrollbar(frame_right, orient="vertical", command=tree_grades_realtime.yview)
    scroll_y.grid(row=0, column=1, sticky='ns')
    tree_grades_realtime.configure(yscrollcommand=scroll_y.set)

    scroll_x = ttk.Scrollbar(frame_right, orient="horizontal", command=tree_grades_realtime.xview)
    scroll_x.grid(row=1, column=0, sticky='ew')
    tree_grades_realtime.configure(xscrollcommand=scroll_x.set)

    # 初始化时定义列
    column_names = fetch_grade_column_names()
    tree_grades_realtime["columns"] = column_names
    tree_grades_realtime["show"] = "headings"
    for col in column_names:
        tree_grades_realtime.heading(col, text=col)
        tree_grades_realtime.column(col, width=100, stretch=False)  # 设置列宽为100并禁用自适应

    # 启动时进行数据查询
    on_query()
    fetch_students()

    # 创建用于展示学生课程记录的 Treeview
    tree_student_courses = ttk.Treeview(frame_right)
    tree_student_courses.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')

    # 添加滚动条
    scroll_y_courses = ttk.Scrollbar(frame_right, orient="vertical", command=tree_student_courses.yview)
    scroll_y_courses.grid(row=2, column=1, sticky='ns')
    tree_student_courses.configure(yscrollcommand=scroll_y_courses.set)

    scroll_x_courses = ttk.Scrollbar(frame_right, orient="horizontal", command=tree_student_courses.xview)
    scroll_x_courses.grid(row=3, column=0, sticky='ew')
    tree_student_courses.configure(xscrollcommand=scroll_x_courses.set)


    course_column_names = ['学生ID', '学生姓名', '课程ID', '课程名', '课程学分', '课程成绩']
    tree_student_courses["columns"] = course_column_names
    tree_student_courses["show"] = "headings"
    for col in course_column_names:
        tree_student_courses.heading(col, text=col)
        tree_student_courses.column(col, width=100, stretch=False)

    root.mainloop()


if __name__ == "__main__":
    main()
