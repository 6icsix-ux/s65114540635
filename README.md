ขั้นตอนการเตรียมความพร้อมสำหรับโปรเจค
1. ดาวโหลดและติดตั้ง Python, Mysql
ลิ้งโหลด Python https://www.python.org/downloads/
ลิ้งโหลด Mysql https://dev.mysql.com/downloads/installer/
เพิ่ม PATH ของทั้ง 2 ให้เรียบร้อย
 ![image](https://github.com/user-attachments/assets/5ae5e38f-b176-42e2-b30c-38f55603ba53)
2. Clone โปรเจค https://github.com/6icsix-ux/CICD_Project.git
3. CD เข้าโปรเจค คำสั่ง CD CICD_Project
4. ติดตั้ง reauirements คำสั่ง pip install -r reauirements.txt
5. ทำการแก้ไขชื่อ Database และ Password ให้เข้าไปที่ finalpj - settings.py เลื่อนลงมาจนถึง DATABASES แก้ไข 'USER' และ 'Password' โดยใช้จากที่ทำการติดตั้ง Mysql
![image](https://github.com/user-attachments/assets/8cf75df5-10d5-4233-aecd-48546d2226a1)
6. ทำการสร้าง DATABASE โดยใช้คำสั่ง Mysql -u "username" -p ตัวอย่าง Mysql -u root -p
7. เมื่อเข้าสู่ระบบสำเร็จ ให้ทำการสร้าง DATABASE โดยใช้คำสั่ง CREATE DATABASE dbfinalapp;
8. ทำการ Makemigrations โดยเปิด Terminal ขึ้มาละใช้คำสั่ง python manage.py makemigrations และ migrste ตามลำดับ คำสั่ง python manage.py migrate
9. เมื่อทำการ Makemigrations และ migrate สำเร็จ ให้ Run โปรเจคได้เลย โดยใช้คำสั่ง python manage.py runserver


Log ที่ถาม AI
https://chatgpt.com/share/686e9534-bea0-800d-aed4-16d90107eddb
