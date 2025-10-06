# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChurchCollection(Document):
	def after_insert(self):
		self.update_church_funds()

	def update_church_funds(self):
		# Group donations by fund
		fund_data = {}
		for donation in self.donations:
			if donation.fund and donation.amount:
				if donation.fund not in fund_data:
					fund_data[donation.fund] = 0
				fund_data[donation.fund] += donation.amount

		# Update each Church Fund
		for fund_name, fund_total in fund_data.items():
			fund_doc = frappe.get_doc("Church Fund", fund_name)

			# Add financial transaction
			transaction = fund_doc.append(
				"transactions",
				{"amount": fund_total, "source_type": "Church Collection", "source": self.name},
			)
			transaction.creation = frappe.utils.now()
			# Update balance (assuming you want to add to existing balance)
			current_balance = fund_doc.get("balance") or 0
			fund_doc.balance = current_balance + fund_total

			fund_doc.save()
