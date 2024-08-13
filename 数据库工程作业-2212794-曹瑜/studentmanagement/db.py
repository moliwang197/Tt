
import pymysql

def get_connection():
    connection = pymysql.connect(
        port=3306,
        user='root',
        password='197101',
        database='studentmanagement',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection



def fetch_students():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Student"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        connection.close()

def delete_student(student_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM Student WHERE student_id = %s"
            cursor.execute(sql, (student_id,))
        connection.commit()
    finally:
        connection.close()

def delete_grade(grade_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM Grade WHERE grade_id = %s"
            cursor.execute(sql, (grade_id,))
        connection.commit()
    finally:
        connection.close()



def fetch_student_grades():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # 查询 Grade 表的所有数据
            cursor.execute("SELECT * FROM Grade")
            grades = cursor.fetchall()

            return grades
    finally:
        connection.close()



def check_student_exists(student_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM Student WHERE student_id = %s", (student_id,))
            return cursor.fetchone() is not None
    finally:
        connection.close()

def check_course_exists(course_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM Course WHERE course_id = %s", (course_id,))
            return cursor.fetchone() is not None
    finally:
        connection.close()

def add_grade(grade_id, student_id,student_name, course_id,course_name, grade):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Grade (grade_id, student_id,student_name, course_id,course_name, grade) VALUES (%s, %s, %s, %s, %s, %s)",
                (grade_id, student_id,student_name, course_id,course_name, grade)
            )
            connection.commit()
    finally:
        connection.close()

def fetch_student_course_records(student_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # 获取学生的课程记录
            sql = """
                SELECT 
                    s.student_id, s.name, c.course_id, c.course_name, c.credits, g.grade
                FROM 
                    Student s
                    NATURAL JOIN Grade g
                    NATURAL JOIN Course c
                WHERE 
                    s.student_id = %s
            """
            cursor.execute(sql, (student_id,))
            records = cursor.fetchall()

            # 计算总学分和平均成绩
            total_credits = sum(record['credits'] for record in records)
            total_points = sum(
                record['credits'] * (100 if record['grade'] == 'A' else
                                           90 if record['grade'] == 'B' else
                                           75 if record['grade'] == 'C' else
                                           60)
                for record in records
            )
            avg_grade = total_points / total_credits if total_credits > 0 else 0

            return records, total_credits, avg_grade
    finally:
        connection.close()
