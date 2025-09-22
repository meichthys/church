# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChurchFamily(Document):
	pass

	@property
	def head_of_household(self):
		# To ensure we don't have multiple people returned here,
		#   After saving a 'Church Person', we uncheck `head_of_household`
		#   for any other 'Church Person's that are part of the same family
		doc_dict = frappe.get_list(
			doctype="Church Person",
			filters=[["family", "=", self.name], ["is_head_of_household", "=", True]],
		)
		if not doc_dict:
			return
		doc_dict[0]["doctype"] = "Church Person"
		return frappe.get_doc(doc_dict[0]).name
