import frappe


def execute(filters=None):
	return get_columns(), get_data()


def get_columns():
	return [
		{"fieldname": "event", "fieldtype": "Link", "label": "Event", "options": "Function", "width": 200},
		{"fieldname": "attendance_count", "fieldtype": "Int", "label": "Attendance Count", "width": 150},
	]


def get_data():
	church_condition = ""
	values = {}

	if not frappe.has_role("System Manager"):
		church_condition = """AND `tabFunction`.church IN (
			SELECT for_value FROM `tabUser Permission`
			WHERE user = %(user)s AND allow = 'Church'
		)"""
		values["user"] = frappe.session.user

	return frappe.db.sql(
		f"""
		SELECT
			`tabEvent Attendance`.parent as event,
			count(`tabEvent Attendance`.person) as attendance_count
		FROM `tabEvent Attendance`
		INNER JOIN `tabFunction` ON `tabFunction`.name = `tabEvent Attendance`.parent
		WHERE `tabEvent Attendance`.attendance_type IN ('Assumed', 'Confirmed')
			{church_condition}
		GROUP BY `tabEvent Attendance`.parent
		""",
		values,
		as_dict=True,
	)
