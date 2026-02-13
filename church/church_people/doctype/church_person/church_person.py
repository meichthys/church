# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe
from frappe.model.document import Document
from frappe.utils import get_link_to_form


class ChurchPerson(Document):
	def on_update(self):
		# Update Family Member list in Church Family
		if self.family:
			family = frappe.get_doc("Church Family", self.family)
			found = False
			for member in family.members:
				if member.member == self.name:
					found = True
					break
			if not found:
				family.append("members", {"member": self.name})
			family.save()

		# Return if person doesn't have family
		if not self.family and not self.get_doc_before_save().family:
			return
		# Remove person from Church Family if family is removed
		if not self.family and self.get_doc_before_save().family is not None:
			family = frappe.get_doc("Church Family", self.get_doc_before_save().family)
			for member in family.members:
				if member.member == self.name:
					family.remove(member)
					break
			family.save()

	def before_save(self):
		# We set this here since virtual fields do not work with
		#   View Settings -> Title Field as of 2025-08-26
		self.full_name = f"{self.first_name}" + ((" " + self.last_name) if self.last_name else "")

	def before_delete(self):
		# Remove person from Church Family
		if self.family:
			family = frappe.get_doc("Church Family", self.family)
			for member in family.members:
				if member.name == self.name:
					family.remove(member)
					break
			family.save()

	def validate(self):
		# Remove head of household status when family is removed
		if not self.family and self.is_head_of_household:
			self.set("is_head_of_household", False)
		# Remove old head of household when new one is assigned - Also rename family
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
				# There should only be one head of household, but just in case we loop through all of them.
				for head in old_heads_of_household:
					head_doc = frappe.get_doc("Church Person", head["name"])
					frappe.msgprint(
						f"ℹ️ {head_doc.full_name} was removed from being the head of this household."
					)
					head_doc.is_head_of_household = False
					head_doc.save()
				# Rename family with new head of household
				family_doc = frappe.get_doc("Church Family", self.family)
				dashes = family_doc.family_name.rfind("-")
				if dashes == -1:  # If no dashes found, add one
					family_doc.family_name = f"{self.family} - {self.first_name}"
				else:
					family_doc.family_name = f"{family_doc.family_name[: dashes + 1]} {self.first_name}"
				family_doc.save()

		# Sync spouses
		if self.spouse and self.is_married:
			# Sync spouses
			spouse = frappe.get_doc("Church Person", self.spouse)
			if spouse.spouse != self.name:
				# Unlink spouse's old spouse if there was one
				frappe.db.set_value("Church Person", spouse.spouse, "spouse", None)
				frappe.db.set_value("Church Person", spouse.spouse, "anniversary", None)
				frappe.db.set_value("Church Person", spouse.spouse, "is_married", False)
				# Link spouses
				frappe.db.set_value("Church Person", spouse.name, "spouse", self.name)
				frappe.db.set_value("Church Person", spouse.name, "is_married", True)
				frappe.msgprint(f"Spouses have been linked:<br>{self.full_name} 👩‍❤️‍👨 {spouse.full_name}")
		else:
			if self._doc_before_save and self._doc_before_save.is_married and self._doc_before_save.spouse:
				spouse = frappe.get_doc("Church Person", self._doc_before_save.spouse)
				frappe.db.set_value("Church Person", spouse.name, "spouse", None)
				frappe.db.set_value("Church Person", spouse.name, "is_married", False)
				self.spouse = None
				self.anniversary = None
				self.is_married = False
				frappe.msgprint(f"Spouses have been unlinked:<br>{self.full_name} 💔 {spouse.full_name}")

	@frappe.whitelist()
	def new_family_from_person(self):
		doc = frappe.new_doc("Church Family")
		doc.family_name = f"{self.last_name} - {self.first_name}"
		doc.save()
		self.set("family", doc)
		self.set("is_head_of_household", True)
		self.save()
		self.reload()
		family_link = get_link_to_form("Church Family", doc.name, doc.family_name)
		frappe.msgprint(f"👨‍👩‍👧‍👦 New family created: {family_link}")

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

	@frappe.whitelist()
	def invite_to_portal(self):
		# Check if user already exists with this email
		user = frappe.db.exists("User", {"email": self.email})

		if not user:
			# Create a new portal user
			new_user = frappe.new_doc("User")
			new_user.email = self.email
			new_user.first_name = self.first_name
			new_user.last_name = self.last_name
			new_user.send_welcome_email = 1
			new_user.enabled = 1
			new_user.role_profile_name = "Church User"
			new_user.save(ignore_permissions=True)

			# Update Church Person to mark as portal user
			self.portal_user = new_user.name
			self.save(ignore_permissions=True)

			frappe.msgprint(
				f"👤 Portal user created and linked: <a href='/app/user/{new_user.name}'>{self.full_name}</a>"
			)
		else:
			# User already exists, just update the portal_user field
			self.portal_user = user
			self.save(ignore_permissions=True)
			frappe.msgprint(
				f"⚠️ Portal user <a href='/app/user/{user}'>{user}</a> already exists. User is now linked to this person."
			)


def get_list_context(context):
	# Only show documents related to the active user
	context.filters = {"portal_user": frappe.session.user}
	# Sort the portal list view by status descending
	context.order_by = "modified desc"
	return context
