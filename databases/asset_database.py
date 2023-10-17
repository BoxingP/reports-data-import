from contextlib import contextmanager

import numpy as np
import pandas as pd
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from databases.database import Database
from databases.models import DeviceUsage, Asset, Computer


@contextmanager
def database_session(session):
    try:
        yield session
    finally:
        session.close()


class AssetDatabase(Database):
    def __init__(self):
        super(AssetDatabase, self).__init__('asset')

    def update_or_insert_sn_asset_data(self, table_class, dataframe):
        dataframe = dataframe.replace({np.nan: None, pd.NaT: None})
        column_mapping = {
            'Name': 'name',
            'Manufacturer': 'manufacturer',
            'Class': 'class_',
            'Serial number': 'serial_number',
            'Operating System': 'operating_system',
            'OS Version': 'os_version',
            'City': 'city',
            'User ID': 'user_id',
            'Active': 'active',
            'VIP': 'vip',
            'Title': 'title',
            'Last login time': 'last_login_time',
            'Mobile phone': 'mobile_phone',
            'Employee ID': 'employee_id',
            'Business Unit': 'business_unit',
            'Is Virtual': 'is_virtual',
            'Is deleted': 'is_deleted',
            'Most recent discovery': 'most_recent_discovery',
            'Last Logged User': 'last_logged_user',
            'Last logged in user': 'last_logged_in_user',
            'Location': 'location',
            'City.1': 'city_1',
            'Site Code ': 'site_code',
        }
        dataframe.rename(columns=column_mapping, inplace=True)
        dataframe['updated_by'] = 'Updated By Script'

        for _, row in dataframe.iterrows():
            serial_nu = row['serial_number']
            if pd.isnull(serial_nu):
                print(
                    f"Skipping row with serial_nu '{serial_nu}' due to null value with name '{row['name']}'")
        dataframe = dataframe.dropna(subset=['serial_number'])

        data = dataframe.to_dict(orient='records')

        with database_session(self.session) as session:
            serial_nus = [record['serial_number'] for record in data]

            existing_records = session.query(table_class).filter(table_class.serial_number.in_(serial_nus)).all()
            existing_record_dict = {record.serial_number: record for record in existing_records}

            insert_values = []
            update_values = []

            for record in data:
                serial_nu = record['serial_number']

                if serial_nu in existing_record_dict:
                    existing_record = existing_record_dict[serial_nu]
                    for key, value in record.items():
                        setattr(existing_record, key, value)
                    update_values.append(existing_record)
                else:
                    insert_values.append(record)

            if insert_values:
                insert_stmt = insert(table_class).values(insert_values)
                session.execute(insert_stmt)

            if update_values:
                update_values_dict = []
                for update_record in update_values:
                    update_dict = {
                        'name': update_record.name,
                        'manufacturer': update_record.manufacturer,
                        'class_': update_record.class_,
                        'serial_number': update_record.serial_number,
                        'operating_system': update_record.operating_system,
                        'os_version': update_record.os_version,
                        'city': update_record.city,
                        'user_id': update_record.user_id,
                        'active': update_record.active,
                        'vip': update_record.vip,
                        'title': update_record.title,
                        'last_login_time': update_record.last_login_time,
                        'mobile_phone': update_record.mobile_phone,
                        'employee_id': update_record.employee_id,
                        'business_unit': update_record.business_unit,
                        'is_virtual': update_record.is_virtual,
                        'is_deleted': update_record.is_deleted,
                        'most_recent_discovery': update_record.most_recent_discovery,
                        'last_logged_user': update_record.last_logged_user,
                        'last_logged_in_user': update_record.last_logged_in_user,
                        'location': update_record.location,
                        'city_1': update_record.city_1,
                        'site_code': update_record.site_code,
                        'updated_by': update_record.updated_by,
                        'updated_time': func.timezone('Asia/Shanghai', func.now())
                    }
                    update_values_dict.append(update_dict)
                update_stmt = insert(table_class).values(update_values_dict)
                update_stmt = update_stmt.on_conflict_do_update(
                    constraint='cmdb_ci_computer_pkey',
                    set_={
                        'name': update_stmt.excluded.name,
                        'manufacturer': update_stmt.excluded.manufacturer,
                        'class_': update_stmt.excluded.class_,
                        'serial_number': update_stmt.excluded.serial_number,
                        'operating_system': update_stmt.excluded.operating_system,
                        'os_version': update_stmt.excluded.os_version,
                        'city': update_stmt.excluded.city,
                        'user_id': update_stmt.excluded.user_id,
                        'active': update_stmt.excluded.active,
                        'vip': update_stmt.excluded.vip,
                        'title': update_stmt.excluded.title,
                        'last_login_time': update_stmt.excluded.last_login_time,
                        'mobile_phone': update_stmt.excluded.mobile_phone,
                        'employee_id': update_stmt.excluded.employee_id,
                        'business_unit': update_stmt.excluded.business_unit,
                        'is_virtual': update_stmt.excluded.is_virtual,
                        'is_deleted': update_stmt.excluded.is_deleted,
                        'most_recent_discovery': update_stmt.excluded.most_recent_discovery,
                        'last_logged_user': update_stmt.excluded.last_logged_user,
                        'last_logged_in_user': update_stmt.excluded.last_logged_in_user,
                        'location': update_stmt.excluded.location,
                        'city_1': update_stmt.excluded.city_1,
                        'site_code': update_stmt.excluded.site_code,
                        'updated_by': update_stmt.excluded.updated_by,
                        'updated_time': func.timezone('Asia/Shanghai', func.now())
                    }
                )
                session.execute(update_stmt)

            session.commit()

    def update_or_insert_sn_asset_sys_mapping_data(self, table_class, json):
        with database_session(self.session) as session:
            sys_ids = [record['sys_id'] for record in json['records']]

            existing_records = session.query(table_class).filter(table_class.sys_id.in_(sys_ids)).all()
            existing_record_dict = {record.sys_id: record for record in existing_records}

            insert_values = []
            update_values = []

            for record in json['records']:
                sys_id = record['sys_id']
                record['updated_by'] = 'Updated By Script'

                if sys_id in existing_record_dict:
                    existing_record = existing_record_dict[sys_id]
                    for key, value in record.items():
                        setattr(existing_record, key, value)
                    update_values.append(existing_record)
                else:
                    insert_values.append(record)

            if insert_values:
                insert_stmt = insert(table_class).values(insert_values)
                session.execute(insert_stmt)

            if update_values:
                update_values_dict = []
                for update_record in update_values:
                    update_dict = {
                        'sys_id': update_record.sys_id,
                        'serial_number': update_record.serial_number,
                        'updated_by': update_record.updated_by,
                        'updated_time': func.timezone('Asia/Shanghai', func.now())
                    }
                    update_values_dict.append(update_dict)
                update_stmt = insert(table_class).values(update_values_dict)
                update_stmt = update_stmt.on_conflict_do_update(
                    constraint='cmdb_ci_computer_sys_mapping_pkey',
                    set_={
                        'sys_id': update_stmt.excluded.sys_id,
                        'serial_number': update_stmt.excluded.serial_number,
                        'updated_by': update_stmt.excluded.updated_by,
                        'updated_time': func.timezone('Asia/Shanghai', func.now())
                    }
                )
                session.execute(update_stmt)

            session.commit()

    def update_or_insert_asset_data(self, table_class, dataframe):
        dataframe = dataframe.replace({np.nan: None, pd.NaT: None})
        column_mapping = {
            '状态': 'status',
            '用户确认': 'confirmation',
            '盘点时间': 'inv_time',
            'PO No': 'po_number',
            '资产条码': 'barcode',
            '资产名称': 'asset_name',
            '成本中心(charge)': 'cost_ctr',
            '资产类别编码': 'class_code',
            '资产类别': 'asset_class',
            '规格型号': 'spec_model',
            'SN号': 'serial_nu',
            '计量单位': 'measure_unit',
            '金额': 'amount',
            '使用公司编码': 'use_comp_code',
            '使用公司': 'use_comp',
            '使用部门编码': 'use_dept_code',
            '使用部门': 'use_dept',
            'BusinessUnit': 'unit',
            '领用人成本中心': 'recipient_cost',
            '员工号': 'emp_id',
            '员工邮箱': 'emp_email',
            '使用人': 'user',
            '在职状态': 'emp_status',
            '离职日期': 'dept_date',
            '区域编码': 'region_code',
            '区域': 'region',
            '存放地点': 'storage_loc',
            '管理员': 'administrator',
            '所属公司编码': 'comp_code',
            '所属公司': 'comp',
            '购入时间': 'purchase_dt',
            '供应商': 'supplier',
            '使用期限': 'use_period',
            '备注': 'remark',
            '创建时间': 'creation_time',
            '最后更新时间': 'last_updated',
            '照片': 'photo',
            '错误反馈': 'error_feedback',
            '待归还时间': 'return_dt',
            '待归还说明': 'return_instr',
            '合约结束': 'contract_end',
            '合约记录': 'contract_rec',
            '原资产处理状态': 'proc_status',
            '用户身份变更': 'identity_change',
            '物品描述': 'item_desc',
            '领用备注': 'receipt_remarks',
            '领用说明': 'receipt_instr',
            '退库说明': 'return_back_instr',
            '清理说明': 'cleanup_instr',
            '扩展字段': 'ext_field'
        }
        dataframe.rename(columns=column_mapping, inplace=True)
        dataframe['updated_by'] = 'Updated By Script'

        for _, row in dataframe.iterrows():
            serial_nu = row['serial_nu']
            if pd.isnull(serial_nu):
                print(
                    f"Skipping row with serial_nu '{serial_nu}' due to null value with employee '{row['emp_id']}' and barcode '{row['barcode']}'")
        dataframe = dataframe.dropna(subset=['serial_nu'])
        duplicates = dataframe[dataframe.duplicated(subset=['serial_nu'], keep=False)]
        for item in duplicates['serial_nu'].drop_duplicates():
            print(f"Skipping row with serial_nu '{item}' due to duplicate")
        dataframe = dataframe.drop_duplicates(subset=['serial_nu'], keep=False)

        data = dataframe.to_dict(orient='records')

        with database_session(self.session) as session:
            serial_nus = [record['serial_nu'] for record in data]

            existing_records = session.query(table_class).filter(table_class.serial_nu.in_(serial_nus)).all()
            existing_record_dict = {record.serial_nu: record for record in existing_records}

            insert_values = []
            update_values = []

            for record in data:
                serial_nu = record['serial_nu']

                if serial_nu in existing_record_dict:
                    existing_record = existing_record_dict[serial_nu]
                    for key, value in record.items():
                        setattr(existing_record, key, value)
                    update_values.append(existing_record)
                else:
                    insert_values.append(record)

            if insert_values:
                insert_stmt = insert(table_class).values(insert_values)
                session.execute(insert_stmt)

            if update_values:
                update_values_dict = []
                for update_record in update_values:
                    update_dict = {
                        'status': update_record.status,
                        'confirmation': update_record.confirmation,
                        'inv_time': update_record.inv_time,
                        'po_number': update_record.po_number,
                        'barcode': update_record.barcode,
                        'asset_name': update_record.asset_name,
                        'cost_ctr': update_record.cost_ctr,
                        'class_code': update_record.class_code,
                        'asset_class': update_record.asset_class,
                        'spec_model': update_record.spec_model,
                        'serial_nu': update_record.serial_nu,
                        'measure_unit': update_record.measure_unit,
                        'amount': update_record.amount,
                        'use_comp_code': update_record.use_comp_code,
                        'use_comp': update_record.use_comp,
                        'use_dept_code': update_record.use_dept_code,
                        'use_dept': update_record.use_dept,
                        'unit': update_record.unit,
                        'recipient_cost': update_record.recipient_cost,
                        'emp_id': update_record.emp_id,
                        'emp_email': update_record.emp_email,
                        'user': update_record.user,
                        'emp_status': update_record.emp_status,
                        'dept_date': update_record.dept_date,
                        'region_code': update_record.region_code,
                        'region': update_record.region,
                        'storage_loc': update_record.storage_loc,
                        'administrator': update_record.administrator,
                        'comp_code': update_record.comp_code,
                        'comp': update_record.comp,
                        'purchase_dt': update_record.purchase_dt,
                        'supplier': update_record.supplier,
                        'use_period': update_record.use_period,
                        'remark': update_record.remark,
                        'creation_time': update_record.creation_time,
                        'last_updated': update_record.last_updated,
                        'photo': update_record.photo,
                        'error_feedback': update_record.error_feedback,
                        'return_dt': update_record.return_dt,
                        'return_instr': update_record.return_instr,
                        'contract_end': update_record.contract_end,
                        'contract_rec': update_record.contract_rec,
                        'proc_status': update_record.proc_status,
                        'identity_change': update_record.identity_change,
                        'item_desc': update_record.item_desc,
                        'receipt_remarks': update_record.receipt_remarks,
                        'receipt_instr': update_record.receipt_instr,
                        'return_back_instr': update_record.return_back_instr,
                        'cleanup_instr': update_record.cleanup_instr,
                        'ext_field': update_record.ext_field,
                        'updated_by': update_record.updated_by,
                        'updated_time': func.timezone('Asia/Shanghai', func.now())
                    }
                    update_values_dict.append(update_dict)
                update_stmt = insert(table_class).values(update_values_dict)
                update_stmt = update_stmt.on_conflict_do_update(
                    constraint='asset_info_pkey',
                    set_={
                        'status': update_stmt.excluded.status,
                        'confirmation': update_stmt.excluded.confirmation,
                        'inv_time': update_stmt.excluded.inv_time,
                        'po_number': update_stmt.excluded.po_number,
                        'barcode': update_stmt.excluded.barcode,
                        'asset_name': update_stmt.excluded.asset_name,
                        'cost_ctr': update_stmt.excluded.cost_ctr,
                        'class_code': update_stmt.excluded.class_code,
                        'asset_class': update_stmt.excluded.asset_class,
                        'spec_model': update_stmt.excluded.spec_model,
                        'measure_unit': update_stmt.excluded.measure_unit,
                        'amount': update_stmt.excluded.amount,
                        'use_comp_code': update_stmt.excluded.use_comp_code,
                        'use_comp': update_stmt.excluded.use_comp,
                        'use_dept_code': update_stmt.excluded.use_dept_code,
                        'use_dept': update_stmt.excluded.use_dept,
                        'unit': update_stmt.excluded.unit,
                        'recipient_cost': update_stmt.excluded.recipient_cost,
                        'emp_id': update_stmt.excluded.emp_id,
                        'emp_email': update_stmt.excluded.emp_email,
                        'user': update_stmt.excluded.user,
                        'emp_status': update_stmt.excluded.emp_status,
                        'dept_date': update_stmt.excluded.dept_date,
                        'region_code': update_stmt.excluded.region_code,
                        'region': update_stmt.excluded.region,
                        'storage_loc': update_stmt.excluded.storage_loc,
                        'administrator': update_stmt.excluded.administrator,
                        'comp_code': update_stmt.excluded.comp_code,
                        'comp': update_stmt.excluded.comp,
                        'purchase_dt': update_stmt.excluded.purchase_dt,
                        'supplier': update_stmt.excluded.supplier,
                        'use_period': update_stmt.excluded.use_period,
                        'remark': update_stmt.excluded.remark,
                        'creation_time': update_stmt.excluded.creation_time,
                        'last_updated': update_stmt.excluded.last_updated,
                        'photo': update_stmt.excluded.photo,
                        'error_feedback': update_stmt.excluded.error_feedback,
                        'return_dt': update_stmt.excluded.return_dt,
                        'return_instr': update_stmt.excluded.return_instr,
                        'contract_end': update_stmt.excluded.contract_end,
                        'contract_rec': update_stmt.excluded.contract_rec,
                        'proc_status': update_stmt.excluded.proc_status,
                        'identity_change': update_stmt.excluded.identity_change,
                        'item_desc': update_stmt.excluded.item_desc,
                        'receipt_remarks': update_stmt.excluded.receipt_remarks,
                        'receipt_instr': update_stmt.excluded.receipt_instr,
                        'return_back_instr': update_stmt.excluded.return_back_instr,
                        'cleanup_instr': update_stmt.excluded.cleanup_instr,
                        'ext_field': update_stmt.excluded.ext_field,
                        'updated_by': update_stmt.excluded.updated_by,
                        'updated_time': func.timezone('Asia/Shanghai', func.now())
                    }
                )
                session.execute(update_stmt)

            session.commit()

    def update_or_insert_emp_data(self, table_class, dataframe):
        column_mapping = {
            'Employee ID': 'emp_id',
            'Legal Name': 'emp_name',
            'Email - Primary Work': 'emp_email',
            'Manager 1 Name': 'lvl1_mgr_name',
            'Manager 1 ID': 'lvl1_mgr_id',
            'CLT': 'clt',
            'Division/Dept.': 'division',
            'CLT-1 Manager': 'clt_lvl1_mgr_name',
            'Type': 'emp_type',
            'CLT-2 Manager ID': 'clt_lvl2_mgr_id',
            'CLT-2 Manager Name': 'clt_lvl2_mgr_name',
            'CLT-2 Manager Email': 'clt_lvl2_mgr_email'
        }
        dataframe.rename(columns=column_mapping, inplace=True)
        dataframe['updated_by'] = 'Updated By Script'

        data = dataframe.to_dict(orient='records')

        with database_session(self.session) as session:
            emp_ids = [record['emp_id'] for record in data]

            existing_records = session.query(table_class).filter(table_class.emp_id.in_(emp_ids)).all()
            existing_records_dict = {record.emp_id: record for record in existing_records}

            insert_values = []
            update_values = []

            for record in data:
                emp_id = record['emp_id']

                if emp_id in existing_records_dict:
                    existing_record = existing_records_dict[emp_id]
                    for key, value in record.items():
                        setattr(existing_record, key, value)
                    update_values.append(existing_record)
                else:
                    insert_values.append(record)

            if insert_values:
                insert_stmt = insert(table_class).values(insert_values)
                session.execute(insert_stmt)

            if update_values:
                update_values_dict = []
                for update_record in update_values:
                    update_dict = {
                        'emp_id': update_record.emp_id,
                        'emp_name': update_record.emp_name,
                        'emp_email': update_record.emp_email,
                        'lvl1_mgr_name': update_record.lvl1_mgr_name,
                        'lvl1_mgr_id': update_record.lvl1_mgr_id,
                        'clt': update_record.clt,
                        'division': update_record.division,
                        'clt_lvl1_mgr_name': update_record.clt_lvl1_mgr_name,
                        'emp_type': update_record.emp_type,
                        'clt_lvl2_mgr_id': update_record.clt_lvl2_mgr_id,
                        'clt_lvl2_mgr_name': update_record.clt_lvl2_mgr_name,
                        'clt_lvl2_mgr_email': update_record.clt_lvl2_mgr_email,
                        'updated_by': update_record.updated_by,
                        'updated_time': func.timezone('Asia/Shanghai', func.now())
                    }
                    update_values_dict.append(update_dict)
                update_stmt = insert(table_class).values(update_values_dict)
                update_stmt = update_stmt.on_conflict_do_update(
                    constraint='employee_info_pkey',
                    set_={
                        'emp_id': update_stmt.excluded.emp_id,
                        'emp_name': update_stmt.excluded.emp_name,
                        'emp_email': update_stmt.excluded.emp_email,
                        'lvl1_mgr_name': update_stmt.excluded.lvl1_mgr_name,
                        'lvl1_mgr_id': update_stmt.excluded.lvl1_mgr_id,
                        'clt': update_stmt.excluded.clt,
                        'division': update_stmt.excluded.division,
                        'clt_lvl1_mgr_name': update_stmt.excluded.clt_lvl1_mgr_name,
                        'emp_type': update_stmt.excluded.emp_type,
                        'clt_lvl2_mgr_id': update_stmt.excluded.clt_lvl2_mgr_id,
                        'clt_lvl2_mgr_name': update_stmt.excluded.clt_lvl2_mgr_name,
                        'clt_lvl2_mgr_email': update_stmt.excluded.clt_lvl2_mgr_email,
                        'updated_by': update_stmt.excluded.updated_by,
                        'updated_time': func.timezone('Asia/Shanghai', func.now())
                    }
                )
                session.execute(update_stmt)

            session.commit()

    def update_or_insert_emp_mgr_mapping_data(self, table_class, dataframe):
        column_mapping = {
            'employee_id': 'emp_id',
            'worker_name': 'emp_name',
            'band': 'job_lvl',
            'termination_date': 'term_date',
            'manager_id': 'mgr_id',
            'manager_legal_name': 'mgr_name',
            'Manager1ID': 'lvl1_mgr_id',
            'Manager1Name': 'lvl1_mgr_name',
            'Manager2ID': 'lvl2_mgr_id',
            'Manager2Name': 'lvl2_mgr_name'
        }
        dataframe.rename(columns=column_mapping, inplace=True)
        dataframe['updated_by'] = 'Updated By Script'

        data = dataframe.to_dict(orient='records')

        with database_session(self.session) as session:
            emp_ids = [record['emp_id'] for record in data]

            existing_records = session.query(table_class).filter(table_class.emp_id.in_(emp_ids)).all()
            existing_records_dict = {record.emp_id: record for record in existing_records}

            insert_values = []
            update_values = []

            for record in data:
                emp_id = record['emp_id']

                if emp_id in existing_records_dict:
                    existing_record = existing_records_dict[emp_id]
                    for key, value in record.items():
                        setattr(existing_record, key, value)
                    update_values.append(existing_record)
                else:
                    insert_values.append(record)

            if insert_values:
                insert_stmt = insert(table_class).values(insert_values)
                session.execute(insert_stmt)

            if update_values:
                update_values_dict = []
                for update_record in update_values:
                    update_dict = {
                        'emp_id': update_record.emp_id,
                        'emp_name': update_record.emp_name,
                        'job_lvl': update_record.job_lvl,
                        'term_date': update_record.term_date,
                        'mgr_id': update_record.mgr_id,
                        'mgr_name': update_record.mgr_name,
                        'lvl1_mgr_id': update_record.lvl1_mgr_id,
                        'lvl1_mgr_name': update_record.lvl1_mgr_name,
                        'lvl2_mgr_id': update_record.lvl2_mgr_id,
                        'lvl2_mgr_name': update_record.lvl2_mgr_name,
                        'updated_by': update_record.updated_by,
                        'updated_time': func.timezone('Asia/Shanghai', func.now())
                    }
                    update_values_dict.append(update_dict)
                update_stmt = insert(table_class).values(update_values_dict)
                update_stmt = update_stmt.on_conflict_do_update(
                    constraint='emp_mgr_mapping_pkey',
                    set_={
                        'emp_id': update_stmt.excluded.emp_id,
                        'emp_name': update_stmt.excluded.emp_name,
                        'job_lvl': update_stmt.excluded.job_lvl,
                        'term_date': update_stmt.excluded.term_date,
                        'mgr_id': update_stmt.excluded.mgr_id,
                        'mgr_name': update_stmt.excluded.mgr_name,
                        'lvl1_mgr_id': update_stmt.excluded.lvl1_mgr_id,
                        'lvl1_mgr_name': update_stmt.excluded.lvl1_mgr_name,
                        'lvl2_mgr_id': update_stmt.excluded.lvl2_mgr_id,
                        'lvl2_mgr_name': update_stmt.excluded.lvl2_mgr_name,
                        'updated_by': update_stmt.excluded.updated_by,
                        'updated_time': func.timezone('Asia/Shanghai', func.now())
                    }
                )
                session.execute(update_stmt)

            session.commit()

    def update_or_insert_device_usage_data(self, dataframe):
        df = dataframe.replace({np.nan: None, pd.NaT: None})
        column_mapping = {
            'Device ID': 'device_id',
            'Device name': 'device_name',
            'Managed by': 'managed_by',
            'Ownership': 'ownership',
            'Compliance': 'compliance',
            'OS': 'os',
            'OS version': 'os_version',
            'Primary user UPN': 'last_use_user',
            'Last check-in': 'last_use_time',
            'Serial number': 'serial_nu'
        }
        df.rename(columns=column_mapping, inplace=True)
        data = df.to_dict(orient='records')

        with database_session(self.session) as session:
            device_ids = [record['device_id'] for record in data]

            existing_records = session.query(DeviceUsage).filter(DeviceUsage.device_id.in_(device_ids)).all()
            existing_record_dict = {record.device_id: record for record in existing_records}

            insert_values = []
            update_values = []

            for record in data:
                device_id = record['device_id']

                if device_id in existing_record_dict:
                    existing_record = existing_record_dict[device_id]
                    for key, value in record.items():
                        setattr(existing_record, key, value)
                    update_values.append(existing_record)
                else:
                    insert_values.append(record)

            if insert_values:
                insert_stmt = insert(DeviceUsage).values(insert_values)
                session.execute(insert_stmt)

            if update_values:
                update_values_dict = []
                for update_record in update_values:
                    update_dict = {
                        'device_id': update_record.device_id,
                        'device_name': update_record.device_name,
                        'managed_by': update_record.managed_by,
                        'ownership': update_record.ownership,
                        'compliance': update_record.compliance,
                        'os': update_record.os,
                        'os_version': update_record.os_version,
                        'last_use_user': update_record.last_use_user,
                        'last_use_time': update_record.last_use_time,
                        'serial_nu': update_record.serial_nu,
                        'updated_time': func.timezone('Asia/Shanghai', func.now())
                    }
                    update_values_dict.append(update_dict)
                update_stmt = insert(DeviceUsage).values(update_values_dict)
                update_stmt = update_stmt.on_conflict_do_update(
                    constraint='device_usage_pkey',
                    set_={
                        'device_name': update_stmt.excluded.device_name,
                        'managed_by': update_stmt.excluded.managed_by,
                        'ownership': update_stmt.excluded.ownership,
                        'compliance': update_stmt.excluded.compliance,
                        'os': update_stmt.excluded.os,
                        'os_version': update_stmt.excluded.os_version,
                        'last_use_user': update_stmt.excluded.last_use_user,
                        'last_use_time': update_stmt.excluded.last_use_time,
                        'serial_nu': update_stmt.excluded.serial_nu,
                        'updated_time': func.timezone('Asia/Shanghai', func.now())
                    }
                )
                session.execute(update_stmt)

            session.commit()

    def get_usage_info(self):
        with database_session(self.session) as session:
            query = session.query(
                Asset.serial_nu,
                func.coalesce(DeviceUsage.device_name, Computer.name).label('device_name'),
                func.coalesce(DeviceUsage.os, Computer.operating_system).label('os'),
                func.coalesce(DeviceUsage.os_version, Computer.os_version).label('os_version'),
                func.coalesce(DeviceUsage.last_use_user, Computer.last_logged_user).label('last_use_user'),
                func.coalesce(DeviceUsage.last_use_time, Computer.last_login_time).label('last_use_time')
            ).outerjoin(
                DeviceUsage, func.lower(func.trim(Asset.serial_nu)) == func.lower(func.trim(DeviceUsage.serial_nu))
            ).outerjoin(
                Computer, func.lower(func.trim(Asset.serial_nu)) == func.lower(func.trim(Computer.serial_number))
            )
            return query.all()
