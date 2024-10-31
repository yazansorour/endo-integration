import frappe
import requests
from requests.auth import HTTPBasicAuth

@frappe.whitelist(allow_guest=True)
def upload_file(file_path, file_name, docname):
    url = "http://127.0.0.1:8000/api/method/upload_file"

    # with open(file_path.split('.')[0] + ".txt", "r") as f:
    #     session_id = f.read()

    headers = {
        'Cookie': 'full_name=Guest; sid=Guest; system_user=no; user_id=Guest; user_image='
    }
    payload = {
        'is_private': "1",
        "doctype": "Endo Orders",
        "docname": docname,
    }
    files=[
        ('file',(file_name, open(file_path,'rb'), 'application/octet-stream'))
    ]

    print(payload)

    username = "f7059fd7b83b376"
    password = "1cce817655ae836"
    auth = HTTPBasicAuth(username, password)
    try:
        response = requests.request("POST", url, headers=headers, data=payload, files=files, auth=auth)
        if response.status_code == 200:
            return True

        else:
            return False

        
    except Exception as e:
        return None


@frappe.whitelist(allow_guest=True)
def removeUploadingFile(file_path, queue_file_path):
    lines = []
    with open(queue_file_path, 'r') as queue_file:
        lines = queue_file.readlines()

    lines = [line.strip() for line in lines]
    for i, line in enumerate(lines):
        if line == file_path:
            del lines[i]
            break

    with open(queue_file_path, 'w') as queue_file:
        queue_file.writelines(lines)
        os.remove(file_path)
    os.remove(file_path.split('.')[0] + ".txt")

    with open(queue_file_path, 'r') as queue_file:
        lines = queue_file.readlines()

    if len(lines) == 0:
        os.remove(queue_file_path)