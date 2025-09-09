# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe
from frappe.model.document import Document


class ChurchPerson(Document):
	def before_save(self):
		# We set this here since virtual fields do not work with
		#   View Settings -> Title Field as of 2025-08-26
		self.full_name = f"{self.first_name} {self.last_name}"

	@frappe.whitelist()
	def add_spouse_to_relationships(self):
		if not self.spouse:
			return
		self.spouse_doc = frappe.get_doc("Church Person", self.spouse, for_update=True)
		# Determine relationship type based on gender
		if self.spouse_doc.gender == "Male":
			spouse_relationship_type = "Wife"
			relationship_type = "Husband"
		elif self.spouse_doc.gender == "Female":
			spouse_relationship_type = "Husband"
			relationship_type = "Wife"
		else:
			frappe.throw(__(f"Invalid spouse gender: {self.spouse_doc.gender}"))

		spouse_doc = frappe.get_doc("Church Person", self.spouse)
		spouse_doc.db_set("is_married", True)
		spouse_doc.db_set("spouse", self.name)
		already_exists = False
		if spouse_doc.relationships:
			for spouse_relationship in spouse_doc.relationships:
				if spouse_relationship.relation_type == spouse_relationship_type and spouse_relationship.church_person == self.name:
					already_exists = True
		if not already_exists:
			spouse_doc.append("relationships", {"church_person": self.name, "relation_type": spouse_relationship_type})
		spouse_doc.save()

		already_exists = False
		if self.relationships:
			for self_relationship in self.relationships:
				if self_relationship.relation_type == relationship_type and self_relationship.church_person == spouse_doc.name:
					already_exists = True
		if not already_exists:
			self.append("relationships", {"church_person": spouse_doc.name, "relation_type": relationship_type})
		self.save()
		frappe.msgprint("✅ Spousal relationships have been synced between spouses.")


	@frappe.whitelist()
	def ensure_single_head_of_household(self):
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
					# ToDo: It may be good to display a message that we are
					#   changing these documents. For some reason frappe.msgprint
					#   seems to only return an empty message here:
					# frappe.msgprint(
					# 	f"A Head of Household for '{self.family}' was already set.\n"
					# 	f"{head_doc.name} was removed from being Head of Household for '{self.family}'"
					# )
					head_doc.is_head_of_household = False
					head_doc.save()

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
			) or (not role.end_date and frappe.utils.get_datetime(role.start_date) < datetime.now()):
				role.is_current_role = 1
			else:
				role.is_current_role = 0
