import pymysql

# MariaDB Connection
db = pymysql.connect(
    host="localhost",
    user="root",
    password="admin", 
    database="pwd_appointment_system"
)

cursor = db.cursor()

admin_email = "admin@pwd.gov"
admin_pass = "admin123" 

try:
    sql = """INSERT INTO users (full_name, email, password_hash, role, pwd_id_number) 
             VALUES (%s, %s, %s, 'admin', 'ADMIN-001')"""
    val = ("System Administrator", admin_email, admin_pass)
    
    cursor.execute(sql, val)
    db.commit()
    print("✅ SUCCESS: Admin account created!")
    print(f"Login with Email: {admin_email}")
    print(f"Login with Pass:  {admin_pass}")

except pymysql.MySQLError as err:
    print(f"❌ ERROR: {err}")
    print("Likely cause: An admin with this email already exists.")
finally:
    db.close()