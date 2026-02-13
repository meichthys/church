import frappe


def before_install():
	# Ensure ERPNext is installed
	if "erpnext" not in frappe.get_installed_apps():
		raise FileNotFoundError("ERPNext must be installed before installing this app.")


def after_install():
	adjust_gender_options()


def adjust_gender_options():
	"""Remove non-biblical Genders from default gender list"""
	genders = frappe.db.get_all("Gender")
	for gender in genders:
		if gender.name not in ["Male", "Female", "Unknown"]:
			frappe.delete_doc("Gender", gender.name, force=True)
