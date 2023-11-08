import datetime
from contextlib import contextmanager

import numpy as np
import pandas as pd
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from databases.database import Database
from databases.models import DeviceUsage, Asset, Computer, TempEmployee
from utils.config import config


@contextmanager
def database_session(session):
    try:
        yield session
    finally:
        session.close()


class AssetDatabase(Database):
    def __init__(self):
        super(AssetDatabase, self).__init__('asset')

    def process_dataframe(self, dataframe, not_null_column, reference_columns):
        df = dataframe.replace({np.nan: None, pd.NaT: None})
        for _, row in df.iterrows():
            not_null_value = row[not_null_column]
            if pd.isnull(not_null_value):
                print_msg = f"Skipping row with '{not_null_column}' '{not_null_value}' due to null value with"
                for column in reference_columns:
                    print_msg += f" '{column}' '{row[column]}'"
                print(print_msg)
        df = df.dropna(subset=[not_null_column])
        duplicates = df[df.duplicated(subset=[not_null_column], keep=False)]
        for item in duplicates[not_null_column].drop_duplicates():
            print(f"Skipping row with '{not_null_column}' '{item}' due to duplicate")
        return df.drop_duplicates(subset=[not_null_column], keep=False)

    def update_or_insert_data(self, table_class, dataframe, column_mapping: dict = None, ignore_fields: list = None,
                              check_columns: list = None):
        if column_mapping:
            dataframe.rename(columns=column_mapping, inplace=True)
        dataframe['updated_by'] = 'Updated By Script'

        data = dataframe.to_dict(orient='records')

        with database_session(self.session) as session:
            pk_column_name = self.get_table_primary_key_column_name(table_class)
            existing_records = session.query(table_class).filter(
                getattr(table_class, pk_column_name).in_([record[pk_column_name] for record in data])).all()
            existing_record_dict = {getattr(record, pk_column_name): record for record in existing_records}

            insert_values = []
            update_values = []

            for record in data:
                unique_key = record[pk_column_name]

                if unique_key in existing_record_dict:
                    existing_record = existing_record_dict[unique_key]

                    if check_columns:
                        check_columns_match = []
                        for key, value in record.items():
                            if key in check_columns:
                                if getattr(existing_record, key) == value:
                                    check_columns_match.append(True)
                                else:
                                    check_columns_match.append(False)
                        if all(check_columns_match):
                            continue

                    for key, value in record.items():
                        if ignore_fields and key in ignore_fields:
                            continue
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
                    if column_mapping:
                        update_dict = {key: getattr(update_record, key) for key in column_mapping.values()}
                    else:
                        update_dict = {key: getattr(update_record, key) for key in dataframe.columns.values}
                    update_dict['updated_by'] = 'Updated By Script'
                    update_dict['updated_time'] = func.timezone('Asia/Shanghai', func.now())
                    update_values_dict.append(update_dict)

                update_stmt = insert(table_class).values(update_values_dict)
                update_stmt = update_stmt.on_conflict_do_update(
                    constraint=self.get_table_constraint_name(table_class),
                    set_=update_stmt.excluded
                )
                session.execute(update_stmt)

            session.commit()

    def update_or_insert_sn_asset_data(self, table_class, dataframe):
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
        ignore_fields = ['updated_time']
        df = self.process_dataframe(dataframe, 'Serial number', ['Name'])
        self.update_or_insert_data(table_class, df, column_mapping, ignore_fields)

    def update_or_insert_sn_asset_sys_mapping_data(self, table_class, dataframe):
        ignore_fields = ['updated_time']
        df = self.process_dataframe(dataframe, 'sys_id', ['serial_number'])
        self.update_or_insert_data(table_class, df, None, ignore_fields)

    def update_or_insert_asset_data(self, table_class, dataframe):
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
        ignore_fields = ['updated_time']
        df = self.process_dataframe(dataframe, 'SN号', ['资产条码', '员工号'])
        self.update_or_insert_data(table_class, df, column_mapping, ignore_fields)

    def update_or_insert_device_usage_data(self, table_class, dataframe):
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
        ignore_fields = ['updated_time']
        df = self.process_dataframe(dataframe, 'Device ID', ['Device name'])
        self.update_or_insert_data(table_class, df, column_mapping, ignore_fields)

    def get_usage_info(self):
        with database_session(self.session) as session:
            query = session.query(
                Asset.serial_nu.label('serial_nu'),
                func.coalesce(DeviceUsage.device_name, Computer.name).label('device_name'),
                func.coalesce(DeviceUsage.os, Computer.operating_system).label('os'),
                func.coalesce(DeviceUsage.os_version, Computer.os_version).label('os_version'),
                func.coalesce(DeviceUsage.last_use_time, Computer.last_login_time).label('last_use_time'),
                func.coalesce(DeviceUsage.last_use_user, Computer.last_logged_user).label('last_use_employee')
            ).outerjoin(
                DeviceUsage, func.lower(func.trim(Asset.serial_nu)) == func.lower(func.trim(DeviceUsage.serial_nu))
            ).outerjoin(
                Computer, func.lower(func.trim(Asset.serial_nu)) == func.lower(func.trim(Computer.serial_number))
            )
            results = pd.DataFrame(query.all())
            results = results.replace({np.nan: None, pd.NaT: None})
            results['serial_nu'] = results['serial_nu'].map(lambda x: x.upper() if isinstance(x, str) else x)
            return results

    def update_or_insert_temp_employee_manager_mapping(self, table_class, dataframe):
        ignore_fields = ['updated_time']

        with database_session(self.session) as session:
            existing_records = session.query(table_class.employee_id, table_class.first_snapshot).all()
            existing_records = pd.DataFrame(existing_records, columns=['employee_id', 'first_snapshot'])
            df = dataframe.merge(existing_records, on='employee_id', how='left')
            df = df.replace({np.nan: None, pd.NaT: None})
            df['first_snapshot'].fillna(config.CST_NOW, inplace=True)
            self.update_or_insert_data(table_class, df, column_mapping=None, ignore_fields=ignore_fields)

    def get_historical_temp_employee_manager_mapping(self, day=config.CST_NOW):
        with database_session(self.session) as session:
            results = session.query(TempEmployee).filter(
                TempEmployee.updated_time >= f"{(day - datetime.timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')}",
                TempEmployee.updated_time < f"{(day + datetime.timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')}").all()
            column_names = [col.name for col in TempEmployee.__table__.columns]
            results = [dict(zip(column_names, [getattr(row, col) for col in column_names])) for row in results]
            results = pd.DataFrame(results)
            results = results.replace({np.nan: None, pd.NaT: None})
            results = results.drop(['updated_by', 'updated_time'], axis=1)
            return results
