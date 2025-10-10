# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_link_to_form


class ChurchExpense(Document):
	def before_delete(self):
		# This probably should never get called since frappe prevents the deletion
		# of submitted documents by default, but just to be sure we'll provide our own warning.
		# Prevent deletion if the document is not cancelled
		if not self.docstatus == 2:  # 2 is Cancelled
			frappe.throw("❌ You must cancel this Church Expense before deleting it.")

	def on_cancel(self):
		fund_name = frappe.db.get_value("Church Expense Type", self.type, "fund")
		if not fund_name:
			frappe.throw("⚠️ No fund linked to the selected Church Expense Type.")

		fund = frappe.get_doc("Church Fund", fund_name)

		# Remove transaction that matches this expense
		updated_transactions = []
		for transaction in fund.transactions:
			if not (transaction.source_type == "Church Expense" and transaction.source == self.name):
				updated_transactions.append(transaction)
			else:
				frappe.msgprint(
					f"💰 Associated {get_link_to_form('Church Fund', fund_name)} fund has been increased by ${-transaction.amount}"
				)
		fund.transactions = updated_transactions
		fund.save(ignore_permissions=True)
		fund.reload()

	def on_submit(self):
		# Get related Church Fund via Expense Type
		fund_name = frappe.db.get_value("Church Expense Type", self.type, "fund")

		if not fund_name:
			frappe.throw("⚠️ No fund linked to the selected Church Expense Type.")

		fund = frappe.get_doc("Church Fund", fund_name)

		# Add new row to fund's transactions table
		fund.append(
			"transactions",
			{
				"amount": -self.amount,
				"source_type": "Church Expense",
				"source": self.name,
				"date": self.date,
				"notes": self.notes,
			},
		)
		fund.save(ignore_permissions=True)
		fund.reload()
		frappe.msgprint(
			f"💸 Associated {get_link_to_form('Church Fund', fund_name)} fund has been reduced by ${self.amount}"
		)
