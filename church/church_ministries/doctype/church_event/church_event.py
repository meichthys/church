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

	copied_doc = {}

	# Specify which fields to include (whitelist approach)
	include_fields = ["address", "all_day", "description"]

	# Copy normal fields
	for field in include_fields:
		if field in template_dict:
			copied_doc[field] = template_dict[field]

	# Copy child tables
	include_child_tables = ["attendance", "schedule"]
	for child_table in include_child_tables:
		if template_dict.get(child_table):
			copied_doc[child_table] = []
			for child_row in template_dict[child_table]:
				new_row = {}
				for child_field in child_row:
					new_row[child_field] = child_row[child_field]
				copied_doc[child_table].append(new_row)
	return copied_doc
