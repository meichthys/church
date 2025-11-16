# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.website.website_generator import WebsiteGenerator


class ChurchPrayerRequest(Document):
	pass


def get_list_context(context):
	"""Sort the portal list view by status descenting"""
	context.order_by = "status desc"
	return context
