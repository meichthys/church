import frappe


def execute(filters=None):
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"fieldname": "status", "fieldtype": "Link", "label": "Status", "options": "Prayer Request Status", "width": 120},
		{"fieldname": "type", "fieldtype": "Link", "label": "Type", "options": "Prayer Request Type", "width": 120},
		{"fieldname": "related_person", "fieldtype": "Link", "label": "Related Person", "options": "Person", "width": 150},
		{"fieldname": "request", "fieldtype": "Data", "label": "Request", "width": 300},
	]


def get_data(filters):
	filters = filters or {}
	church_condition = ""
	values = {"request_since": filters.get("request_since")}

	if not frappe.has_role("System Manager"):
		church_condition = """AND church IN (
			SELECT for_value FROM `tabUser Permission`
			WHERE user = %(user)s AND allow = 'Church'
		)"""
		values["user"] = frappe.session.user

	return frappe.db.sql(
		f"""
		SELECT status, type, related_person, request
		FROM `tabPrayer Request`
		WHERE creation > %(request_since)s
			AND status = 'answered'
			{church_condition}
		""",
		values,
		as_dict=True,
	)
