from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CMDBComputer(Base):
    __tablename__ = 'cmdb_ci_computer'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    manufacturer = Column(String(100))
    class_ = Column(String(100))
    serial_number = Column(String(100))
    operating_system = Column(String(100))
    os_version = Column(String(100))
    city = Column(String(100))
    user_id = Column(String(100))
    is_active = Column(Boolean)
    is_vip = Column(Boolean)
    title = Column(String(100))
    last_login_time = Column(TIMESTAMP)
    mobile_phone = Column(String(100))
    employee_id = Column(Integer)
    business_unit = Column(String(100))
    is_virtual = Column(Boolean)
    is_deleted = Column(Boolean)
    most_recent_discovery = Column(TIMESTAMP)
    last_logged_user = Column(String(100))
    last_logged_in_user = Column(String(100))
    location = Column(String(100))
    city_location = Column(String(100))
    site_code = Column(String(50))
    updated_by = Column(String(50))
    updated_time = Column(TIMESTAMP(timezone=True), server_default=func.timezone('Asia/Shanghai', func.now()))
