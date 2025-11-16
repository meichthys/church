# Copyright (c) 2025, meichthys and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.website.website_generator import WebsiteGenerator


class ChurchPrayerRequest(Document):
	pass


def get_list_context(context):
	# Only show documents created by active user
	context.filters = {"owner": frappe.session.user}
	# Sort the portal list view by status descending
	context.order_by = "modified desc"
	return context
