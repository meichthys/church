import json
import os

import frappe


def execute():
	data_dir = os.path.join(os.path.dirname(__file__), "data")
	if not os.path.isdir(data_dir):
		return

	for filename in sorted(os.listdir(data_dir)):
		if not filename.endswith(".json"):
			continue
		with open(os.path.join(data_dir, filename)) as f:
			records = json.load(f)
		for record in records:
			doctype = record.get("doctype")
			name = record.get("name")
			if not doctype or not name:
				continue
			if not frappe.db.exists(doctype, name):
				try:
					frappe.get_doc(record).insert(ignore_permissions=True)
				except Exception:
					frappe.log_error(frappe.get_traceback(), f"insert_data patch failed: {doctype} {name}")
