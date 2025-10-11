# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChurchCollection(Document):
	def on_submit(self):
		self.update_church_funds(reverse=False)

	def on_cancel(self):
		self.update_church_funds(reverse=True)

	def update_church_funds(self, reverse=False):
		fund_data = {}
		for donation in self.donations:
			if donation.fund and donation.amount:
				fund_data.setdefault(donation.fund, 0)
				fund_data[donation.fund] += donation.amount

		messages = []

		for fund_name, fund_total in fund_data.items():
			fund_doc = frappe.get_doc("Church Fund", fund_name)

			if reverse:
				fund_doc.transactions = [
					txn
					for txn in fund_doc.transactions
					if not (txn.source_type == "Church Collection" and txn.source == self.name)
				]
				fund_doc.balance = (fund_doc.balance or 0) - fund_total
				fund_doc.save(ignore_permissions=True)
				messages.append(f"💸 {fund_name} fund decreased by ${fund_total}")
			else:
				fund_doc.append(
					"transactions",
					{
						"amount": fund_total,
						"source_type": "Church Collection",
						"source": self.name,
						"date": frappe.utils.now(),
					},
				)
				fund_doc.balance = (fund_doc.balance or 0) + fund_total
				fund_doc.save(ignore_permissions=True)
				messages.append(f"💰 {fund_name} fund increased by ${fund_total}")
		if messages:
			frappe.msgprint("<br>".join(messages))
		# Warn if funds are now negative
		if fund_doc.balance < 0:
			frappe.msgprint(f"⚠️ {fund_name} fund balance is negative: {fund_doc.balance}")
