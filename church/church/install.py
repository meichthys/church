import frappe


def before_install():
	# Ensure ERPNext is installed
	if "erpnext" not in frappe.get_installed_apps():
		raise FileNotFoundError(
			f"ERPNext must be installed before installing this app."
		)


def after_install():
	# Remove non-biblical Genders
	genders = frappe.db.get_all("Gender")
	for gender in genders:
		if gender.name not in ["Male", "Female", "Unknown"]:
			frappe.delete_doc("Gender", gender.name, force=True)
