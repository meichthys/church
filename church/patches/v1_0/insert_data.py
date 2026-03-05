import json
import os
import frappe


def execute():
	seed_dir = os.path.join(os.path.dirname(__file__), "data")
	if not os.path.isdir(seed_dir):
		return

	for filename in sorted(os.listdir(seed_dir)):
		if not filename.endswith(".json"):
			continue
		with open(os.path.join(seed_dir, filename)) as f:
			records = json.load(f)
		for record in records:
			doctype = record.get("doctype")
			name = record.get("name")
			if not doctype or not name:
				continue
			if not frappe.db.exists(doctype, name):
				frappe.get_doc(record).insert(ignore_permissions=True)
