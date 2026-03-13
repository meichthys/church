# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

import frappe


def sync_user_permission(doc, method):
	"""Auto-create/update User Permission for Church when a user is saved.

	Users with Church User or Church Manager roles are scoped to their assigned
	church. System Manager and other roles are left unrestricted and can view
	documents across all churches.
	"""
	user_roles = {r.role for r in doc.get("roles", [])}

	if not user_roles:
		return

	church = doc.get("church")

	# Remove existing User permissions for this user
	frappe.db.delete("User Permission", {"user": doc.name, "allow": "Church"})

	# Create new User Permission
	if church:
		frappe.get_doc(
			{
				"doctype": "User Permission",
				"user": doc.name,
				"allow": "Church",
				"for_value": church,
				"apply_to_all_doctypes": 1,
			}
		).insert(ignore_permissions=True)
		frappe.defaults.set_user_default("church", church, user=doc.name)
	else:
		frappe.defaults.clear_user_default("church", user=doc.name)


def validate_church_manager_edits(doc, method):
	"""Prevent Church Managers from escalating user privileges."""
	if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles():
		return

	if "Church Manager" not in frappe.get_roles():
		return

	# Require a role profile — direct role assignment is not allowed
	allowed_profiles = {"Church Manager", "Church User"}
	if not doc.role_profile_name:
		frappe.throw(
			"Church Managers cannot modify individual roles. A role profile must be selected ('Church Manager' or 'Church User').",
			frappe.PermissionError,
		)

	if doc.role_profile_name not in allowed_profiles:
		frappe.throw(
			"Church Managers can only assign the 'Church Manager' or 'Church User' role profiles.",
			frappe.PermissionError,
		)

