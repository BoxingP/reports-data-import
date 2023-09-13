import pandas as pd

from databases.database import Database


class AssetDatabase(Database):
    def __init__(self):
        super(AssetDatabase, self).__init__()

    def import_sn_asset_data(self, table_class, dataframe, is_truncate=False):
        if is_truncate:
            self.truncate_table(table_class.__tablename__)
        for column in dataframe.columns:
            new_name = column.strip().lower().replace(' ', '_').replace('.', '_')
            if new_name in ['class']:
                new_name = f'{new_name}_'
            dataframe.rename(columns={column: new_name}, inplace=True)
        dataframe['updated_by'] = 'Updated By Script'
        dataframe.to_sql(table_class.__tablename__, con=self.session.bind, if_exists='append', index=False)

    def import_sn_asset_sys_mapping_data(self, table_class, json):
        for record in json['records']:
            mapping = table_class(
                sys_id=record['sys_id'],
                serial_number=record['serial_number'],
                updated_by='Updated By Script'
            )
            self.session.merge(mapping)
        self.session.commit()
        self.session.close()

    def import_asset_info_data(self, table_class, dataframe):
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
        dataframe = dataframe.rename(columns=column_mapping)
        dataframe['updated_by'] = 'Updated By Script'

        for _, row in dataframe.iterrows():
            serial_nu = row['serial_nu']
            if pd.isnull(serial_nu):
                print(
                    f"Skipping row with serial_nu '{serial_nu}' due to null value with employee '{row['emp_id']}' and barcode '{row['barcode']}'")
                continue

            existing_row = self.session.query(table_class).filter_by(serial_nu=serial_nu).first()
            if existing_row:
                for col in dataframe.columns:
                    value = row[col]
                    if col != 'serial_nu':
                        setattr(existing_row, col, value)
            else:
                new_row = table_class(**row)
                self.session.add(new_row)
            self.session.commit()

    def import_emp_info_data(self, table_class, dataframe):
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
        dataframe = dataframe.rename(columns=column_mapping)
        dataframe['updated_by'] = 'Updated By Script'

        for _, row in dataframe.iterrows():
            emp_id = row['emp_id']
            existing_row = self.session.query(table_class).filter_by(emp_id=emp_id).first()
            if existing_row:
                for col in dataframe.columns:
                    value = row[col]
                    if col != 'emp_id':
                        setattr(existing_row, col, value)
            else:
                new_row = table_class(**row)
                self.session.add(new_row)

        self.session.commit()

    def import_emp_mgr_mapping_data(self, table_class, dataframe):
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
        dataframe = dataframe.rename(columns=column_mapping)
        dataframe['updated_by'] = 'Updated By Script'

        for _, row in dataframe.iterrows():
            emp_id = row['emp_id']
            existing_row = self.session.query(table_class).filter_by(emp_id=emp_id).first()
            if existing_row:
                for col in dataframe.columns:
                    value = row[col]
                    if col != 'emp_id':
                        setattr(existing_row, col, value)
            else:
                new_row = table_class(**row)
                self.session.add(new_row)

        self.session.commit()
