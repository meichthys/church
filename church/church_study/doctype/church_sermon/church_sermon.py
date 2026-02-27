# Copyright (c) 2026, meichthys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.rename_doc import rename_doc


class ChurchSermon(Document):
	def before_save(self):
		if not self.is_new() and self.has_value_changed("title") and self.title != self.name:
			rename_doc(self.doctype, self.name, self.title, merge=False)
			self.name = self.title
