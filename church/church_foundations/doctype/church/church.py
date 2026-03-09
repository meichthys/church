# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Church(Document):
	def validate(self):
		if not self.parent_church:
			existing_root = frappe.db.get_value(
				"Church",
				{"parent_church": ("is", "not set"), "name": ("!=", self.name)},
				"name",
			)
			if existing_root:
				frappe.throw(
					_("Only one root Church is allowed. '{0}' is already the root church. Please set a Parent Church.").format(
						existing_root
					)
				)
