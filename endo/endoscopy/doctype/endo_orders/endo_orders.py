# Copyright (c) 2024, WOW and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from endo.gdt.classes.GDTMessage import GDTMessage
from endo.gdt.enums.GDTMessageDataTag import GDTMessageDataTag
from endo.gdt.classes.GDTNetworkConnection import GDTNetworkConnection
import os

class EndoOrders(Document):
	def validate(self):
		if self.workflow_state == 'Waiting For Result':
			birthDate = str(self.dob)
			endoModality = frappe.get_doc('Endoscopy Modalities' , self.endoscopy_modalities)
			message6301 = {
				'ROOT_DATA_TRANSFER_SET_TYPE': '6302',  # Message type
				'SENTENCE_LENGTH': '',
				'DEVICE_METHOD': endoModality.device_method,
				'RECEIVER_GDT_ID': endoModality.receiver_id , # Receiver ID
				'SENDER_GDT_ID':frappe.get_single('Endo Connection Settings').sender_id, # Sender ID (same as before)
				'SET_TYPE_USED': '2',                     # Type of data transfer
				'VERSION_GDT': '02.10',                    # Version of the GDT
				'PATIENT_NUMBER': self.patient_identifier,              # Patient number
				'PATIENT_NAME': self.patient_name,           # Surname
				'PATIENT_FIRST_NAME': self.patient_name.split(" ")[0],            # First name
				'PATIENT_BIRTH_DATE': birthDate.split("-")[2] + birthDate.split("-")[1] + birthDate.split("-")[0],          # Date of birth (DDMMYY)
				'PATIENT_SEX': '2' if self.gender == 'Female' else '1', # Sex: 1=male, 2=female
				'PATIENT_HEIGHT': self.patient_height,# Height in cm
				'PATIENT_WEIGHT': self.patient_weight,# Weight in kg
				'TEST_ID': 'PEndo'                   
			}

			gdtMessage = GDTMessage()
			gdtTags = list(message6301.items())

			for index, (key  , value) in enumerate(gdtTags):
				field_tag = getattr(GDTMessageDataTag , key)
				gdtMessage.appendLine(field_tag , value)

			gdtFormattedMessage = gdtMessage.buildMessage()

			filePath = f'{frappe.get_single('Endo Connection Settings').import_path}/{self.name}.gdt'
			with open(filePath , 'w', encoding='cp437') as file:
				file.write(gdtFormattedMessage)

			if not os.path.exists(f'/home/frappe/share/{endoModality.modalities_name}/{endoModality.base_path}/{endoModality.import_path}'):
				os.makedirs(f'/home/frappe/share/{endoModality.modalities_name}/{endoModality.base_path}/{endoModality.import_path}')
			GDTNetworkConnection.sendFile(filePath ,f'/home/frappe/share/{endoModality.modalities_name}/{endoModality.base_path}/{endoModality.import_path}' )