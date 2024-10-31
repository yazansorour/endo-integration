# Copyright (c) 2024, WOW and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import os

class EndoscopyModalities(Document):
	def after_insert(self):
		if not os.path.exists(f'/home/frappe/share/{self.modalities_name}'):
			os.makedirs(f'/home/frappe/share/{self.modalities_name}')

	def validate(self):
		if self.workflow_state == 'Active':
			os.system(f'nohup python3 /home/frappe/frappe-bench/apps/endo/endo/gdt/gdt_listener.py {frappe.get_single('Endo Connection Settings').export_path} /home/frappe/share/{self.modalities_name}/{self.base_path}/{self.export_path} & echo $! > /home/frappe/frappe-bench/apps/endo/endo/gdt/pid/{self.modalities_name}.pid')
		elif self.workflow_state == 'Not Active':
			os.system(f'kill `cat /home/frappe/frappe-bench/apps/endo/endo/gdt/pid/{self.modalities_name}.pid`  && rm -rf /home/frappe/frappe-bench/apps/endo/endo/gdt/pid/{self.modalities_name}.pid')

