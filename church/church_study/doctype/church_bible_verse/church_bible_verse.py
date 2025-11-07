# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChurchBibleVerse(Document):
	pass

	def autoname(self):
		name = self.get_name()
		if not frappe.db.exists("Church Bible Verse", self.name):
			self.name = name
			return
		else:
			if self.name != self.get_name():
				frappe.rename_doc("Church Bible Verse", self.name, name)

	def get_name(self):
		"""Constructs the document name"""
		return f"{self.book} {self.chapter}:{self.verse}"

	def on_update(self):
		# Rename document when updating
		self.autoname()
