import frappe
from . import insert_data


def execute():
	insert_data.execute()
	adjust_gender_options()


def adjust_gender_options():
	"""Remove non-biblical Genders from default gender list"""
	genders = frappe.db.get_all("Gender")
	for gender in genders:
		if gender.name not in ["Male", "Female", "Unknown"]:
			frappe.delete_doc("Gender", gender.name, force=True)
