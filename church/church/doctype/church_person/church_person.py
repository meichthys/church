# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe
from frappe.model.document import Document


class ChurchPerson(Document):
	def before_save(self):
		# We set this here since virtual fields do not work with
		#   View Settings -> Title Field as of 2025-08-26
		self.full_name = f"{self.first_name}" + (
			(" " + self.last_name) if self.last_name else ""
		)

	def validate(self):
		if self.is_head_of_household:
			old_heads_of_household = frappe.db.get_all(
				doctype="Church Person",
				filters=[
					["family", "=", self.family],
					["is_head_of_household", "=", True],
					["name", "!=", self.name],
				],
			)
			if old_heads_of_household:
				for head in old_heads_of_household:
					head_doc = frappe.get_doc("Church Person", head["name"])
					frappe.msgprint(
						f"ℹ️ {head_doc.full_name} was removed from being the head of this household."
					)
					head_doc.is_head_of_household = False
					head_doc.save()

		# Sync spouses
		if self.spouse:
			# Sync spouses
			spouse = frappe.get_doc("Church Person", self.spouse)
			if spouse.spouse != self.name:
				frappe.db.set_value("Church Person", spouse.name, "spouse", self.name)
				frappe.db.set_value("Church Person", spouse.name, "is_married", True)
				frappe.msgprint(
					f"Spouses have been linked:<br>"
					f"{self.full_name} 👩‍❤️‍👨 {spouse.full_name}"
				)
		else:
			if self._doc_before_save.spouse:
				spouse = frappe.get_doc("Church Person", self._doc_before_save.spouse)
				frappe.db.set_value("Church Person", spouse.name, "is_married", False)
				frappe.db.set_value("Church Person", spouse.name, "spouse", None)
				self.is_married = False
				frappe.msgprint(
					f"Spouses have been unlinked:<br>"
					f"{self.full_name} 💔 {spouse.full_name}"
				)

	@frappe.whitelist()
	def new_family_from_person(self):
		doc = frappe.new_doc("Church Family")
		doc.family_name = self.last_name
		doc.save()
		self.set("family", doc)
		self.save()
		self.reload()
		frappe.msgprint(f"New family created: {doc.family_name}")

	@frappe.whitelist()
	def update_is_current_role(self):
		for role in self.church_roles:
			if (
				frappe.utils.get_datetime(role.start_date)
				< datetime.now()
				< frappe.utils.get_datetime(role.end_date)
			) or (
				not role.end_date
				and frappe.utils.get_datetime(role.start_date) < datetime.now()
			):
				role.is_current_role = 1
			else:
				role.is_current_role = 0
