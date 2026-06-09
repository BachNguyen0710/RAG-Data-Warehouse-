# test_connection.py
import pyodbc

# Test SQL Auth
conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=ragdb;"
    "UID=sa;"
    "PWD=123456789;"   # ← thay password thật vào đây
    "TrustServerCertificate=yes;"
)

# Hoặc test Windows Auth
# conn_str = (
#     "DRIVER={ODBC Driver 18 for SQL Server};"
#     "SERVER=localhost;"
#     "DATABASE=ragdb;"
#     "Trusted_Connection=yes;"
#     "TrustServerCertificate=yes;"
# )

try:
    conn = pyodbc.connect(conn_str)
    print("Kết nối thành công!")
    conn.close()
except Exception as e:
    print(f"Lỗi: {e}")

from app.core.config import settings
print("URL đang dùng:", settings.DATABASE_URL)