# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChurchBibleReference(Document):
	pass

	def autoname(self):
		name = self.get_name()
		if not frappe.db.exists("Church Bible Reference", self.name):
			self.name = name
			return
		else:
			if self.name != self.get_name():
				frappe.rename_doc("Church Bible Reference", self.name, name)

	def get_name(self):
		"""Constructs the document name"""
		if self.start_verse and self.end_verse:
			ref = f"{self.start_verse} - {self.end_verse}"
		elif self.start_verse:
			ref = f"{self.start_verse}"
		else:
			frappe.throw("A start verse is required to name the reference")
		if self.translation:
			return f"{ref} ({self.translation})"
		else:
			return ref

	def on_update(self):
		# Rename document when updating
		self.autoname()
