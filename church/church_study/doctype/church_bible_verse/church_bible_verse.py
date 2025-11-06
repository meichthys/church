# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChurchBibleVerse(Document):
	pass

	@frappe.whitelist()
	def rename_verse(self):
		"""
		Rename Church Bible Verse document to 'Book Chapter:Verse'.
		Returns the new name.
		"""
		doc = frappe.get_doc("Church Bible Verse", self.name)
		new_name = f"{doc.book} {doc.chapter}:{doc.verse}"

		# Only rename if different
		if doc.name != new_name:
			frappe.rename_doc("Church Bible Verse", doc.name, new_name)

		return new_name
