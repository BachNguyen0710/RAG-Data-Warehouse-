from app.core.database import engine, Base
from app.models import db_models  

Base.metadata.create_all(bind=engine)
print("Tạo bảng thành công!")