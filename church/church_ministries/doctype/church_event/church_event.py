# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class ChurchEvent(Document):
	pass


@frappe.whitelist()
def apply_template(source_name):
	# Get template document
	template = frappe.get_doc("Church Event", source_name)
	template_dict = template.as_dict()

	# Specify which fields to include (whitelist approach)
	include_fields = ["address", "all_day", "description"]

	copied_doc = {"attendance": {}}

	for field in include_fields:
		if field in template_dict:
			copied_doc[field] = template_dict[field]

	# Copy attendance child table
	if template_dict.get("attendance"):
		copied_doc["attendance"] = []
		for child_row in template_dict["attendance"]:
			new_row = {}  # Create NEW dict for each row
			for child_field in child_row:
				new_row[child_field] = child_row[child_field]
			copied_doc["attendance"].append(new_row)  # Append after building complete row

	return copied_doc
