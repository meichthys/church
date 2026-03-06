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
