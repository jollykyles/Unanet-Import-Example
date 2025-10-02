import os
import sys
import paramiko
import pandas as pd
import numpy as np
import re
from pathlib import Path

def normalize_location(location):
    match = re.search(r'\b([A-Z]{2})\b', str(location))
    return match.group(1) if match else None

def map_business_week(value):
    mapping = {
        'FT': 'WEEK-40: 100% (Full-Time)',
        'PT': 'WEEK-20: 50% (1/2 Time)',
        'PT60': 'WEEK-24: 60% (3 Days)', 
        'PT80': 'WEEK-32: 80% (4 Days)',
        'CAS': 'Casual Labor'
    }
    return mapping.get(str(value).strip().upper(), value)

def normalize_exempt_status(status):
    status = str(status).strip().lower()
    if 'salary' in status:
        return 'E'
    elif 'hourly' in status:
        return 'N'
    elif 'subcontractor' in status:
        return 'X'
    return None

def normalize_active(value):
    return 'Y' if str(value).strip().upper() in ['Y', 'A', 'ACTIVE'] else 'N'

def download_from_sftp():
    sftp_host = os.environ.get("SFTP_HOST")
    sftp_user = os.environ.get("SFTP_USER")
    sftp_private_key = os.environ.get("SFTP_RSA_PRIVATE_KEY")

    if not all([sftp_host, sftp_user, sftp_private_key]):
        print("Error: One or more SFTP credentials are missing.")
        sys.exit(1)

    key_path = Path("sftp_key.pem")
    key_path.write_text(sftp_private_key)
    key_path.chmod(0o600)

    remote_file = "people.csv"
    local_dir = Path("unanet_imu/data")
    local_dir.mkdir(parents=True, exist_ok=True)
    local_file = local_dir / "import.csv"

    try:
        key = paramiko.RSAKey.from_private_key_file(str(key_path))
        print("Connecting to SFTP server...")
        transport = paramiko.Transport((sftp_host, 22))
        transport.connect(username=sftp_user, pkey=key)
        sftp = paramiko.SFTPClient.from_transport(transport)

        print(f"Downloading {remote_file} to {local_file}...")
        sftp.get(remote_file, str(local_file))

        if local_file.exists():
            print(f"Download successful: {local_file} ({local_file.stat().st_size} bytes)")
            transform_csv(local_file)
        else:
            print("Download failed: File not found after transfer.")

        sftp.close()
        transport.close()

    except Exception as e:
        print(f"Error during SFTP download: {e}")
        sys.exit(1)
    finally:
        if key_path.exists():
            key_path.unlink()

def transform_csv(file_path):
    print("Transforming CSV file with data cleaning and mapping...")

    column_mapping = {
        "Username": "*Username",
        "FirstName": "First_Name",
        "LastName": "Last_Name",
        "MiddleInitial": "Middle_Initial",
        "Suffix": "Suffix",
        "Exempt_Status": "Exempt_Status",
        "Time_Period": "Time_Period",
        "Pay_Code": "Pay_Code",
        "Hour_Increment": "Hour_Increment",
        "Expense_Approval_Group": "Expense_Approval_Group",
        "Person_Code": "Person_Code",
        "ID_Code_1": "ID_Code_1",
        "ID_Code_2": "ID_Code_2",
        "Password": "Password",
        "Email": "Email",
        "Person_Org_Code": "Person_Org_Code",
        "Bill_Rate": "Bill_Rate",
        "Cost_Rate": "Cost_Rate",
        "Time_Approval_Group": "Time_Approval_Group",
        "Active": "Active",
        "Timesheet_Emails": "Timesheet_Emails",
        "Expense_Emails": "Expense_Emails",
        "Autofill_Timesheet": "Autofill_Timesheet",
        "Expense_Approval_Amount": "Expense_Approval_Amount",
        "Effective_Date": "Effective_Date",
        "Default_Project_Org": "Default_Project_Org",
        "Default_Project": "Default_Project",
        "Default_Task": "Default_Task",
        "Default_Payment_Method": "Default_Payment_Method",
        "TITO_Required": "TITO_Required",
        "Assignment_Emails": "Assignment_Emails",
        "User01": "Remove",
        "Annual_Rate": "User01",
        "User02": "User02",
        "User03": "User03",
        "User04": "User04",
        "User05": "User05",
        "User06": "User06",
        "User07": "User07",
        "User08": "User08",
        "User09": "User09",
        "User10": "User10",
        "Hire_Date": "Hire_Date",
        "Payment_Currency": "Payment_Currency",
        "Cost_Structure": "Cost_Structure",
        "Cost_Element": "Cost_Element",
        "Location": "Location",
        "Employee_Type": "Employee_Type",
        "Business_Week1": "Business_Week"
    }

    valid_columns = [
        "*Username", "First_Name", "Last_Name", "Middle_Initial", "Suffix", "Nickname", 
        # "Exempt_Status",
        "Time_Period", "Pay_Code", "Hour_Increment", "Expense_Approval_Group", "Person_Code", "ID_Code_1", "ID_Code_2", 
        "Email", "Person_Org_Code", 
        # "Bill_Rate", "Cost_Rate", 
        "Time_Approval_Group", "Active", "Expense_Approval_Amount", 
        # "Effective_Date", 
        "Assignment_Emails", "User01", "User02", "User03", "User04", "User05", "User06", "User07", "User08", 
        "User09", "User10", "Business_Week", "Hire_Date", "Payment_Currency",
        # "Cost_Structure", "Cost_Element", 
        "Location", "Employee_Type", "Time_Vendor", "Expense_Vendor", "Payroll_Hire_Date", "Payroll_Marital_Status",
        "Payroll_Federal_Exemptions", "Payroll_SUI_Tax_Code", "Payroll_State_Worked_In", "Payroll_Immigration_Status",
        "Payroll_EEO_Code", "Payroll_Medical_Plan", "Payroll_Last_Rate_Change_Date", "Payroll_Last_Rate_Change",
        "Person_Purchase_Approval_Amt", "Person_Purchase_Email", "Person_Approval_Grp_Timesheet",
        "Person_Approval_Grp_Leave", "Person_Approval_Grp_Exp_Rep", "Person_Approval_Grp_Exp_Req",
        "Person_Approval_Grp_PO", "Person_Approval_Grp_PR", "Person_Approval_Grp_VI", "User11", "User12", "User13",
        "User14", "User15", "User16", "User17", "User18", "User19", "User20", "Vendor_Invoice_Person", "PO_Form_Title",
        "Allow_Items", "Subcontractor", "SCA_Wage_Flag", "AR_Approval_Amount", "Vehicle_Number", "Preferred_Currency",
        "Customer_Invoice_Receive_Emails", "Default_Legal_Entity_Code"
    ]

    try:
        df = pd.read_csv(file_path)
        df = df.rename(columns=column_mapping)
        df = df[[col for col in df.columns if col in valid_columns]]

        # Apply normalization and defaults
        df['Location'] = df['Location'].str.replace("–", "-")    
        # df['Exempt_Status'] = df['Exempt_Status'].apply(normalize_exempt_status)        
        df['Active'] = df['Active'].apply(normalize_active)
        df['Person_Org_Code'] = df['Person_Org_Code'].fillna('PROTEQ')
        df['Business_Week'] = df['Business_Week'].apply(map_business_week)
        df['Person_Code'] = df['Person_Code'].astype(str)
        df['ID_Code_1'] = df['ID_Code_1'].astype(str)
        df['ID_Code_2'] = df['ID_Code_2'].astype(str)

        local_dir = Path("unanet_imu/data")
        
        # Print all files and directories inside local_dir
        for item in local_dir.iterdir():
            print(item)

        local_file = local_dir / "person.csv"
        person = pd.read_csv(local_file)
        person = person[['*username', 'person_code']]

        print(person.head(1))
        print(df.head(1))

        df = df.merge(person, left_on=['Person_Code'], right_on=['person_code'], how='left')
        # Generate *Username as FIRSTNAME.LASTNAME in all caps
        df['*Username'] = df['*username']
        df['*Username'] = np.where(df['*Username'].isnull(), 
                                   (df['First_Name'].fillna('') + '.' + df['Last_Name'].fillna('')).str.upper(),
                                   df['*Username'])
        df['*Username'] = df['*Username'].replace(" ", "")

        df = df.drop(['*username', 'person_code'], axis=1)

        df.to_csv(file_path, index=False)
        print("CSV transformation and cleaning complete.")

    except Exception as e:
        print(f"Error during CSV transformation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_from_sftp()
