from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func, Float, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Computer(Base):
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
    active = Column(Boolean)
    vip = Column(Boolean)
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
    city_1 = Column(String(100))
    site_code = Column(String(50))
    updated_by = Column(String(50))
    updated_time = Column(TIMESTAMP(timezone=True), server_default=func.timezone('Asia/Shanghai', func.now()))


class ComputerSysMappingTable(Base):
    __tablename__ = 'cmdb_ci_computer_sys_mapping'

    sys_id = Column(String(100), primary_key=True)
    serial_number = Column(String(100))
    updated_by = Column(String(50))
    updated_time = Column(TIMESTAMP(timezone=True), server_default=func.timezone('Asia/Shanghai', func.now()))


class Asset(Base):
    __tablename__ = 'asset_info'

    status = Column(String(20))
    confirmation = Column(String(20))
    inv_time = Column(TIMESTAMP)
    po_number = Column(String(50))
    barcode = Column(String(50))
    asset_name = Column(Text)
    cost_ctr = Column(String(50))
    class_code = Column(String(50))
    asset_class = Column(String(50))
    spec_model = Column(String(100))
    serial_nu = Column(String(50), primary_key=True)
    measure_unit = Column(String(20))
    amount = Column(Float)
    use_comp_code = Column(String(20))
    use_comp = Column(String(20))
    use_dept_code = Column(String(50))
    use_dept = Column(String(50))
    unit = Column(String(50))
    recipient_cost = Column(String(100))
    emp_id = Column(String(50))
    emp_email = Column(String(100))
    user = Column(String(100))
    emp_status = Column(String(50))
    dept_date = Column(TIMESTAMP)
    region_code = Column(String(50))
    region = Column(String(50))
    storage_loc = Column(String(100))
    administrator = Column(Text)
    comp_code = Column(String(50))
    comp = Column(String(50))
    purchase_dt = Column(TIMESTAMP)
    supplier = Column(Text)
    use_period = Column(String(50))
    remark = Column(Text)
    creation_time = Column(TIMESTAMP)
    last_updated = Column(TIMESTAMP)
    photo = Column(Text)
    error_feedback = Column(Text)
    return_dt = Column(TIMESTAMP)
    return_instr = Column(Text)
    contract_end = Column(TIMESTAMP)
    contract_rec = Column(TIMESTAMP)
    proc_status = Column(String(100))
    identity_change = Column(String(100))
    item_desc = Column(Text)
    receipt_remarks = Column(Text)
    receipt_instr = Column(Text)
    return_back_instr = Column(Text)
    cleanup_instr = Column(Text)
    ext_field = Column(Text)
    updated_by = Column(String(50))
    updated_time = Column(TIMESTAMP(timezone=True), server_default=func.timezone('Asia/Shanghai', func.now()))


class Employee(Base):
    __tablename__ = 'employee_info'

    emp_id = Column(String(20), primary_key=True)
    emp_name = Column(Text)
    emp_email = Column(String(100))
    emp_type = Column(String(50))
    lvl1_mgr_id = Column(String(50))
    lvl1_mgr_name = Column(Text)
    clt = Column(String(50))
    division = Column(String(50))
    clt_lvl1_mgr_name = Column(Text)
    clt_lvl2_mgr_id = Column(String(50))
    clt_lvl2_mgr_name = Column(Text)
    clt_lvl2_mgr_email = Column(String(100))
    updated_by = Column(String(50))
    updated_time = Column(TIMESTAMP(timezone=True), server_default=func.timezone('Asia/Shanghai', func.now()))


class EmployeeManagerMapping(Base):
    __tablename__ = 'emp_mgr_mapping'

    emp_id = Column(String(20), primary_key=True)
    emp_name = Column(Text)
    job_lvl = Column(Integer)
    term_date = Column(TIMESTAMP)
    mgr_id = Column(String(20))
    mgr_name = Column(Text)
    lvl1_mgr_id = Column(String(20))
    lvl1_mgr_name = Column(Text)
    lvl2_mgr_id = Column(String(20))
    lvl2_mgr_name = Column(Text)
    updated_by = Column(String(50))
    updated_time = Column(TIMESTAMP(timezone=True), server_default=func.timezone('Asia/Shanghai', func.now()))


class DeviceUsage(Base):
    __tablename__ = 'device_usage'

    id = Column(Integer, primary_key=True)
    device_name = Column(Text)
    serial_nu = Column(Text)
    device_os = Column(Text)
    os_version = Column(Text)
    last_use_user = Column(Text)
    last_use_time = Column(TIMESTAMP)
    got_from = Column(String(10))
    updated_time = Column(TIMESTAMP(timezone=True), server_default=func.timezone('Asia/Shanghai', func.now()))
