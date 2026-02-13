# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChurchAlmsRequest(Document):
	pass


@frappe.whitelist()
def create_expense(alms_request_name):
	"""Create a Church Expense from the given Alms Request."""
	alms = frappe.get_doc("Church Alms Request", alms_request_name)
	# Make sure an expense type and amount are provided
	if not alms.amount:
		frappe.throw("⚠️ An amount is required for an expense to be created.")
	if not alms.expense_type:
		frappe.throw("⚠️ An expense type is required for an expense to be created.")
	expense = frappe.new_doc("Church Expense")
	expense.amount = alms.amount
	expense.notes = f"Church Alms Request: {alms.name}"
	expense.type = frappe.db.get_value("Church Expense Type", alms.expense_type, "type")
	expense.date = frappe.utils.now()
	expense.insert(ignore_permissions=True)
	frappe.msgprint(f"✅ {expense.type} expense created.")
	expense.submit()


def get_list_context(context):
	# Only show documents created by active user
	context.filters = {"owner": frappe.session.user}
	# Sort the portal list view by status descending
	context.order_by = "modified desc"
	return context
