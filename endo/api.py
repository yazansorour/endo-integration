import frappe
from endo.gdt.classes.GDTMessage import GDTMessage
from endo.gdt.enums.GDTMessageDataTag import GDTMessageDataTag
from endo.gdt.classes.GDTNetworkConnection import GDTNetworkConnection
from endo.util import upload_file
import os 

@frappe.whitelist(allow_guest=True)
def uploadTestResult(testResult , files):
    gdtMessage = GDTMessage()
    message = gdtMessage.parseMessage(testResult)
    message.pop()
    tag_map = {}
    for item in message:
        tag_value = item['tag']
        enum_member = next((tag.name for tag in GDTMessageDataTag if tag.value == tag_value), None)
        tag_map[enum_member] = item['value'] if enum_member else f"Unknown Tag {tag_value}"
    
    query = """
    SELECT name FROM `tabEndo Orders`
    WHERE patient_identifier = %s
    AND workflow_state = %s
    """
    patientOrders = frappe.db.sql(query , (tag_map['PATIENT_NUMBER'] , 'Waiting For Result'), as_dict=True)
    
    if len(patientOrders) > 0 :
        order = frappe.get_doc('Endo Orders',patientOrders[0].name)

        isSuccess = False
        for file in files:
            extenstion = file.split('.')[len(file.split('.'))-1]
            new_path = f"{order.name}.{extenstion}"
            ## 0000011-TW-Endoscopic Drainage.gdt
            ## 0000011-TW-Endoscopic Drainage1.png
            i = 1
            while os.path.exists(f'/home/frappe/frappe-bench/sites/wow.sa/private/files/{new_path}'):
                new_path = f"{order.name}_{i}.{extenstion}"
                i += 1
            isSuccess = upload_file(file , new_path ,order.name)
            if isSuccess != True:
                frappe.throw(f'failed to upload : this file {file} in order {order.name}')
        GDTNetworkConnection.cleanRemoteFolderFiles('/home/frappe/frappe-bench/sites/gdt/out')
        
        frappe.db.sql("""
            UPDATE `tabEndo Orders`
            SET workflow_state = %s
            WHERE name = %s
        """ , ('Waiting For Approval' , order.name))

        frappe.db.commit()
            


    return 'Success'
    


