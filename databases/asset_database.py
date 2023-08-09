from databases.database import Database


class AssetDatabase(Database):
    def __init__(self):
        super(AssetDatabase, self).__init__()

    def import_data(self, table_name, dataframe, is_truncate=False):
        if is_truncate:
            self.truncate_table(table_name)
        column_mapping = {
            'Name': 'name',
            'Manufacturer': 'manufacturer',
            'Class': 'class',
            'Serial number': 'serial_number',
            'Operating System': 'operating_system',
            'OS Version': 'os_version',
            'City': 'city',
            'User ID': 'user_id',
            'Active': 'is_active',
            'VIP': 'is_vip',
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
            'City.1': 'city_location',
            'Site Code ': 'site_code'
        }
        dataframe = dataframe.rename(columns=column_mapping)
        dataframe['updated_by'] = 'Updated By Script'
        dataframe.to_sql(table_name, con=self.session.bind, if_exists='append', index=False)
