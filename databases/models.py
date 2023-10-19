from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func, Float, Text, Enum, VARCHAR, NVARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Computer(Base):
    __tablename__ = 'cmdb_ci_computer'

    name = Column(String)
    manufacturer = Column(String)
    class_ = Column(String)
    serial_number = Column(String, primary_key=True)
    operating_system = Column(String)
    os_version = Column(String)
    city = Column(String)
    user_id = Column(String)
    active = Column(Boolean)
    vip = Column(Boolean)
    title = Column(String)
    last_login_time = Column(TIMESTAMP)
    mobile_phone = Column(String)
    employee_id = Column(Integer)
    business_unit = Column(String)
    is_virtual = Column(Boolean)
    is_deleted = Column(Boolean)
    most_recent_discovery = Column(TIMESTAMP)
    last_logged_user = Column(String)
    last_logged_in_user = Column(String)
    location = Column(String)
    city_1 = Column(String)
    site_code = Column(String)
    updated_by = Column(String)
    updated_time = Column(TIMESTAMP(timezone=True), server_default=func.timezone('Asia/Shanghai', func.now()))


class ComputerSysMappingTable(Base):
    __tablename__ = 'cmdb_ci_computer_sys_mapping'

    sys_id = Column(String, primary_key=True)
    serial_number = Column(String)
    updated_by = Column(String)
    updated_time = Column(TIMESTAMP(timezone=True), server_default=func.timezone('Asia/Shanghai', func.now()))


class Asset(Base):
    __tablename__ = 'asset_info'

    status = Column(String)
    confirmation = Column(String)
    inv_time = Column(TIMESTAMP)
    po_number = Column(String)
    barcode = Column(String)
    asset_name = Column(Text)
    cost_ctr = Column(String)
    class_code = Column(String)
    asset_class = Column(String)
    spec_model = Column(String)
    serial_nu = Column(String, primary_key=True)
    measure_unit = Column(String)
    amount = Column(Float)
    use_comp_code = Column(String)
    use_comp = Column(String)
    use_dept_code = Column(String)
    use_dept = Column(String)
    unit = Column(String)
    recipient_cost = Column(String)
    emp_id = Column(String)
    emp_email = Column(String)
    user = Column(String)
    emp_status = Column(String)
    dept_date = Column(TIMESTAMP)
    region_code = Column(String)
    region = Column(String)
    storage_loc = Column(String)
    administrator = Column(Text)
    comp_code = Column(String)
    comp = Column(String)
    purchase_dt = Column(TIMESTAMP)
    supplier = Column(Text)
    use_period = Column(String)
    remark = Column(Text)
    creation_time = Column(TIMESTAMP)
    last_updated = Column(TIMESTAMP)
    photo = Column(Text)
    error_feedback = Column(Text)
    return_dt = Column(TIMESTAMP)
    return_instr = Column(Text)
    contract_end = Column(TIMESTAMP)
    contract_rec = Column(TIMESTAMP)
    proc_status = Column(String)
    identity_change = Column(String)
    item_desc = Column(Text)
    receipt_remarks = Column(Text)
    receipt_instr = Column(Text)
    return_back_instr = Column(Text)
    cleanup_instr = Column(Text)
    ext_field = Column(Text)
    updated_by = Column(String)
    updated_time = Column(TIMESTAMP(timezone=True), server_default=func.timezone('Asia/Shanghai', func.now()))


class Employee(Base):
    __tablename__ = 'employee_info'

    emp_id = Column(String, primary_key=True)
    emp_name = Column(Text)
    emp_email = Column(String)
    emp_type = Column(String)
    lvl1_mgr_id = Column(String)
    lvl1_mgr_name = Column(Text)
    clt = Column(String)
    division = Column(String)
    clt_lvl1_mgr_name = Column(Text)
    clt_lvl2_mgr_id = Column(String)
    clt_lvl2_mgr_name = Column(Text)
    clt_lvl2_mgr_email = Column(String)
    updated_by = Column(String)
    updated_time = Column(TIMESTAMP(timezone=True), server_default=func.timezone('Asia/Shanghai', func.now()))


class EmployeeManagerMapping(Base):
    __tablename__ = 'emp_mgr_mapping'

    emp_id = Column(String, primary_key=True)
    emp_name = Column(Text)
    job_lvl = Column(Integer)
    term_date = Column(TIMESTAMP)
    mgr_id = Column(String)
    mgr_name = Column(Text)
    lvl1_mgr_id = Column(String)
    lvl1_mgr_name = Column(Text)
    lvl2_mgr_id = Column(String)
    lvl2_mgr_name = Column(Text)
    updated_by = Column(String)
    updated_time = Column(TIMESTAMP(timezone=True), server_default=func.timezone('Asia/Shanghai', func.now()))


class DeviceUsage(Base):
    __tablename__ = 'device_usage'

    device_id = Column(String, primary_key=True)
    device_name = Column(String)
    managed_by = Column(Enum('Co-managed', 'Intune', 'Other', name='managed_by_enum'))
    ownership = Column(Enum('Corporate', 'Personal', 'Unknown', name='ownership_enum'))
    compliance = Column(
        Enum('Compliant', 'ConfigManager', 'InGracePeriod', 'Noncompliant', 'Not Evaluated', name='compliance_enum'))
    os = Column(String)
    os_version = Column(String)
    last_use_user = Column(String)
    last_use_time = Column(TIMESTAMP)
    serial_nu = Column(String)
    updated_by = Column(String)
    updated_time = Column(TIMESTAMP(timezone=True), server_default=func.timezone('Asia/Shanghai', func.now()))


class EmployeeCollect(Base):
    __tablename__ = 'V_EMPLOYEE_ITAsset'

    employee_id = Column(VARCHAR(20), primary_key=True)
    worker_name = Column(NVARCHAR(200))
    email_primary_work = Column(NVARCHAR(100))
    domainaccount = Column(NVARCHAR(200))
