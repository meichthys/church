"""
after_install patch — runs once when the Church app is installed on a new site.

Creates all default reference data, configuration, and website content so the
app is usable out of the box.  Existing sites are not affected (this hook only
fires on ``bench install-app church``).

Execution order matters for doctypes that reference each other:
  Form Tour  →  Onboarding Step  →  Module Onboarding
"""

import os

import frappe


def execute():
	# Simple lookup types (no inter-dependencies)
	_create_member_statuses()
	_create_event_types()
	_create_event_attendance_types()
	_create_position_types()
	_create_payment_types()
	_create_person_relation_types()
	_create_prayer_request_statuses()
	_create_prayer_request_types()
	_create_missionary_support_frequencies()

	# Bible reference data
	_create_bible_books()
	_create_bible_translations()

	# Module access control
	_create_module_profile()

	# Dashboard charts
	_create_dashboard_charts()

	# Custom HTML blocks
	_create_custom_html_blocks()

	# Guided setup — must be in dependency order
	_create_form_tours()  # referenced by Onboarding Step
	_create_onboarding_steps()  # referenced by Module Onboarding
	_create_module_onboarding()

	# Website content
	_create_web_pages()
	_setup_about_us_settings()
	_setup_website_settings()
	_setup_portal_menu_items()

	# Cleanup
	_clean_gender_options()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _insert_if_missing(doctype, name, **fields):
	"""Insert a record only if it does not already exist (idempotent)."""
	if not frappe.db.exists(doctype, name):
		frappe.get_doc({"doctype": doctype, "name": name, **fields}).insert(ignore_permissions=True)


def _read_template(filename):
	"""Read an HTML template from the templates/ subdirectory next to this file."""
	templates_dir = os.path.join(os.path.dirname(__file__), "templates")
	with open(os.path.join(templates_dir, filename)) as f:
		return f.read()


# ---------------------------------------------------------------------------
# Simple lookup types
# ---------------------------------------------------------------------------


def _create_member_statuses():
	for status in ("Active", "Inactive"):
		_insert_if_missing("Member Status", status, status=status)


def _create_event_types():
	for event_type in (
		"Sunday Morning Service",
		"Sunday Evening Service",
		"Prayer Meeting",
		"Business Meeting",
		"Communion",
		"Baptism",
	):
		_insert_if_missing("Event Type", event_type, type=event_type)


def _create_event_attendance_types():
	types = {
		"Unknown": "Attendance was not tracked for this event.",
		"Absent": "The person was not present at this event.",
		"Assumed": "The person was assumed to be present at this event (e.g. their family was present).",
		"Confirmed": "The person's attendance was confirmed at this event.",
	}
	for name, description in types.items():
		_insert_if_missing("Event Attendance Type", name, type=name, description=description)


def _create_position_types():
	for position in ("Pastor", "Elder", "Deacon", "Secretary", "Treasurer"):
		_insert_if_missing("Position Type", position, position=position)


def _create_payment_types():
	for payment_type in ("Cash", "Check"):
		_insert_if_missing("Payment Type", payment_type, type=payment_type)


def _create_person_relation_types():
	for relation in (
		"Uncle",
		"Aunt",
		"Brother",
		"Sister",
		"Husband",
		"Wife",
		"Father",
		"Mother",
		"Son",
		"Daughter",
		"Grandson",
		"Granddaughter",
		"Grandfather",
		"Grandmother",
		"Nephew",
		"Niece",
		"Brother-in-law",
		"Sister-in-law",
		"Father-in-law",
		"Mother-in-law",
		"Stepfather",
		"Stepmother",
		"Stepbrother",
		"Stepsister",
	):
		_insert_if_missing("Person Relation Type", relation, relation_type=relation)


def _create_prayer_request_statuses():
	statuses = {
		"Requested": "This prayer request has been submitted and is awaiting prayer.",
		"Being Prayed For": "This prayer request is currently being prayed for.",
		"Answered": "This prayer has been answered.",
	}
	for name, description in statuses.items():
		_insert_if_missing("Prayer Request Status", name, status=name, description=description)


def _create_prayer_request_types():
	types = {
		"Praise": "A prayer of praise and thanksgiving to God.",
		"Health": "A prayer request related to health or healing.",
		"Salvation": "A prayer request for the salvation of a person.",
		"Unspoken": "A prayer request that the person does not wish to share details about.",
	}
	for name, description in types.items():
		_insert_if_missing("Prayer Request Type", name, type=name, description=description)


def _create_missionary_support_frequencies():
	frequencies = {
		"Weekly": "Support is sent once per week.",
		"Bi-Weekly": "Support is sent every two weeks.",
		"Monthly": "Support is sent once per month.",
		"Bi-Monthly": "Support is sent every two months.",
		"Quarterly": "Support is sent four times per year.",
		"Yearly": "Support is sent once per year.",
	}
	for name, description in frequencies.items():
		_insert_if_missing("Missionary Support Frequency", name, frequency=name, description=description)


# ---------------------------------------------------------------------------
# Bible reference data
# ---------------------------------------------------------------------------


def _create_bible_books():
	"""Insert all 66 canonical Bible books with their standard abbreviations.

	The record ``name`` is the full book name (e.g. "Genesis") and
	``abbreviation`` is the short code used by bible-api.com (e.g. "GEN").
	"""
	books = [
		# Old Testament
		("Genesis", "GEN"),
		("Exodus", "EXO"),
		("Leviticus", "LEV"),
		("Numbers", "NUM"),
		("Deuteronomy", "DEU"),
		("Joshua", "JOS"),
		("Judges", "JDG"),
		("Ruth", "RUT"),
		("1 Samuel", "1SA"),
		("2 Samuel", "2SA"),
		("1 Kings", "1KI"),
		("2 Kings", "2KI"),
		("1 Chronicles", "1CH"),
		("2 Chronicles", "2CH"),
		("Ezra", "EZR"),
		("Nehemiah", "NEH"),
		("Esther", "EST"),
		("Job", "JOB"),
		("Psalms", "PSA"),
		("Proverbs", "PRO"),
		("Ecclesiastes", "ECC"),
		("Song of Solomon", "SNG"),
		("Isaiah", "ISA"),
		("Jeremiah", "JER"),
		("Lamentations", "LAM"),
		("Ezekiel", "EZK"),
		("Daniel", "DAN"),
		("Hosea", "HOS"),
		("Joel", "JOL"),
		("Amos", "AMO"),
		("Obadiah", "OBA"),
		("Jonah", "JON"),
		("Micah", "MIC"),
		("Nahum", "NAM"),
		("Habakkuk", "HAB"),
		("Zephaniah", "ZEP"),
		("Haggai", "HAG"),
		("Zechariah", "ZEC"),
		("Malachi", "MAL"),
		# New Testament
		("Matthew", "MAT"),
		("Mark", "MRK"),
		("Luke", "LUK"),
		("John", "JHN"),
		("Acts", "ACT"),
		("Romans", "ROM"),
		("1 Corinthians", "1CO"),
		("2 Corinthians", "2CO"),
		("Galatians", "GAL"),
		("Ephesians", "EPH"),
		("Philippians", "PHP"),
		("Colossians", "COL"),
		("1 Thessalonians", "1TH"),
		("2 Thessalonians", "2TH"),
		("1 Timothy", "1TI"),
		("2 Timothy", "2TI"),
		("Titus", "TIT"),
		("Philemon", "PHM"),
		("Hebrews", "HEB"),
		("James", "JAS"),
		("1 Peter", "1PE"),
		("2 Peter", "2PE"),
		("1 John", "1JN"),
		("2 John", "2JN"),
		("3 John", "3JN"),
		("Jude", "JUD"),
		("Revelation", "REV"),
	]
	for book_name, abbreviation in books:
		_insert_if_missing("Bible Book", book_name, book=book_name, abbreviation=abbreviation)


def _create_bible_translations():
	"""Insert common English Bible translations used by bible-api.com."""
	translations = [
		("King James Version", "KJV"),
		("New International Version", "NIV"),
		("English Standard Version", "ESV"),
		("New Living Translation", "NLT"),
		("Christian Standard Bible", "CSB"),
		("New King James Version", "NKJV"),
		("New American Standard Bible", "NASB"),
		("New American Bible Revised Edition", "NABRE"),
		("The Message", "MSG"),
		("Amplified Bible", "AMP"),
		("New Revised Standard Version", "NRSV"),
		("American Standard Version", "ASV"),
		("Douay-Rheims Bible", "DRB"),
		("Revised Standard Version", "RSV"),
		("Jerusalem Bible", "JB"),
		("New Jerusalem Bible", "NJB"),
		("Common English Bible", "CEB"),
		("Good News Translation", "GNT"),
		("Contemporary English Version", "CEV"),
		("New English Translation", "NET"),
		("New International Reader's Version", "NIrV"),
		("Complete Jewish Bible", "CJB"),
		("The Passion Translation", "TPT"),
		("The Living Bible", "LIVING"),
		("Modern English Version", "MEV"),
		("New Century Version", "NCV"),
		("The Voice", "VOICE"),
		("World English Bible", "WEB"),
		("Berean Standard Bible", "BSB"),
		("Bible in Basic English", "BBE"),
	]
	for translation_name, abbreviation in translations:
		_insert_if_missing(
			"Bible Translation",
			translation_name,
			translation=translation_name,
			abbreviation=abbreviation,
		)


# ---------------------------------------------------------------------------
# Module Profile — controls which Frappe modules Church users can see
# ---------------------------------------------------------------------------


def _create_module_profile():
	"""Create the 'Church' Module Profile, blocking all non-church modules.

	Users assigned this profile will only see Church app modules in the desk,
	hiding unrelated ERPNext/Frappe modules that would otherwise be confusing.
	"""
	if frappe.db.exists("Module Profile", "Church"):
		return

	blocked_modules = [
		"Manufacturing",
		"Quality Management",
		"Selling",
		"EDI",
		"Stock",
		"Accounts",
		"Assets",
		"Automation",
		"Bulk Transaction",
		"Buying",
		"Contacts",
		"CRM",
		"Custom",
		"Email",
		"ERPNext Integrations",
		"Integrations",
		"Maintenance",
		"Geo",
		"Projects",
		"Regional",
		"Setup",
		"Social",
		"Subcontracting",
		"Support",
		"Telephony",
		"Utilities",
		"Workflow",
		"Communication",
		"Printing",
		"Portal",
		"Desk",
		"Core",
	]
	frappe.get_doc(
		{
			"doctype": "Module Profile",
			"module_profile_name": "Church",
			"block_modules": [{"module": m} for m in blocked_modules],
		}
	).insert(ignore_permissions=True)


# ---------------------------------------------------------------------------
# Dashboard Charts
# ---------------------------------------------------------------------------


def _create_dashboard_charts():
	"""Create People and Members line charts shown on the Church workspace."""
	if not frappe.db.exists("Dashboard Chart", "People"):
		frappe.get_doc(
			{
				"doctype": "Dashboard Chart",
				"chart_name": "People",
				"module": "Church People",
				"document_type": "Person",
				"based_on": "creation",
				"type": "Line",
				"time_interval": "Weekly",
				"timespan": "Last Year",
				"timeseries": 1,
				"is_standard": 1,
				"show_values_over_chart": 1,
				"filters_json": "[]",
				"dynamic_filters_json": "[]",
			}
		).insert(ignore_permissions=True)

	if not frappe.db.exists("Dashboard Chart", "Members"):
		frappe.get_doc(
			{
				"doctype": "Dashboard Chart",
				"chart_name": "Members",
				"module": "Church People",
				"document_type": "Person",
				"based_on": "membership_date",
				"type": "Line",
				"time_interval": "Monthly",
				"timespan": "Last Year",
				"timeseries": 1,
				"is_standard": 1,
				"show_values_over_chart": 1,
				"filters_json": '[["Person","is_member","=",1,false]]',
				"dynamic_filters_json": "[]",
			}
		).insert(ignore_permissions=True)


# ---------------------------------------------------------------------------
# Custom HTML Blocks
# ---------------------------------------------------------------------------


def _create_custom_html_blocks():
	"""Create a cover photo block shown on the Church workspace."""
	if frappe.db.exists("Custom HTML Block", "Church Cover Photo"):
		return

	frappe.get_doc(
		{
			"doctype": "Custom HTML Block",
			"name": "Church Cover Photo",
			"html": (
				'<div style="text-align: center;">\n'
				'  <img src="/assets/church/media/church_photo.jpg"'
				' alt="Church Photo" style="max-width: 100%; border-radius: 8px;">\n'
				"</div>\n"
			),
			"private": 0,
		}
	).insert(ignore_permissions=True)


# ---------------------------------------------------------------------------
# Guided setup: Form Tour → Onboarding Step → Module Onboarding
# (must be created in this order — each references the one above it)
# ---------------------------------------------------------------------------


def _create_form_tours():
	"""Create all Church Form Tours.

	Tours must exist before the Onboarding Steps that reference them.
	"""
	_create_form_tour_church_manager()
	_create_form_tour_person()
	_create_form_tour_church()


def _create_form_tour_church_manager():
	"""Walk an administrator through creating a new User with the correct
	Module Profile and Role Profile for church management.
	"""
	if frappe.db.exists("Form Tour", "Church Manager"):
		return

	frappe.get_doc(
		{
			"doctype": "Form Tour",
			"name": "Church Manager",
			"title": "Church Manager",
			"reference_doctype": "User",
			"module": "Desk",
			"is_standard": 1,
			"save_on_complete": 1,
			"steps": [
				{
					"title": "Email",
					"fieldname": "email",
					"fieldtype": "Data",
					"position": "Bottom",
					"description": (
						"Enter the email of the user. This may be used for resetting passwords,"
						" sending notifications, etc.\nFor email notifications to work, the"
						" Administrator must configure a default outgoing email server using the"
						" `New Email Account` action."
					),
					"has_next_condition": 1,
					"next_step_condition": 'eval: doc.email.includes("@");',
				},
				{
					"title": "First Name",
					"fieldname": "first_name",
					"fieldtype": "Data",
					"position": "Bottom",
					"description": (
						"A first name is required. You can use something generic like"
						' "Manager" or "ChurchManager".'
					),
					"has_next_condition": 1,
					"next_step_condition": "eval: doc.first_name !== null;",
				},
				{
					"title": "Timezone",
					"fieldname": "time_zone",
					"fieldtype": "Autocomplete",
					"position": "Top",
					"description": (
						"You may want to update the timezone if it doesn't match what you would expect."
					),
				},
				{
					"title": "Module Profile",
					"fieldname": "module_profile",
					"fieldtype": "Link",
					"position": "Right Center",
					"description": (
						'Select "Church" as the Module Profile.\n'
						"This gives the user access to all the 'Church' app modules.\n\n"
						"⚠️ After saving this user, come back to this page and assign the"
						' "Church Manager" (or "Church User") \'RoleProfile\' to this user'
						' (Not just the "Church Manager" permission). This will give the user'
						" permission to actually make changes to the Church records."
					),
					"has_next_condition": 1,
					"next_step_condition": 'eval: doc.module_profile == "Church";',
				},
				{
					"title": "Settings",
					"fieldname": "mute_sounds",
					"fieldtype": "Check",
					"element_selector": "#user-settings_tab-tab",
					"position": "Top",
					"description": (
						"After saving the user, you can come back to this settings tab"
						" to set (reset) the user's password."
					),
				},
			],
		}
	).insert(ignore_permissions=True)


def _create_form_tour_person():
	"""Walk a user through adding their first Person record."""
	if frappe.db.exists("Form Tour", "Person"):
		return

	frappe.get_doc(
		{
			"doctype": "Form Tour",
			"name": "Person",
			"title": "Person",
			"reference_doctype": "Person",
			"module": "Desk",
			"is_standard": 1,
			"save_on_complete": 1,
			"steps": [
				{
					"title": "First Name",
					"fieldname": "first_name",
					"fieldtype": "Data",
					"position": "Bottom",
					"description": (
						"A `First Name` is the only required(*) field.\nLet's give this person a name."
					),
					"has_next_condition": 1,
					"next_step_condition": "eval: doc.first_name",
				},
				{
					"title": "Last Name",
					"fieldname": "last_name",
					"fieldtype": "Data",
					"position": "Bottom",
					"description": (
						"Add a `Last Name`.\n"
						"The `Last Name` field is required if you want to create a family from this person.\n"
						"After saving, a `Full Name` field will appear and auto-populate."
					),
					"has_next_condition": 1,
					"next_step_condition": "eval: doc.last_name ",
				},
				{
					"title": "Photo",
					"fieldname": "photo",
					"fieldtype": "Attach Image",
					"position": "Bottom",
					"description": (
						"Let's not bother adding a photo now, but if you were to add a photo,"
						" it will be displayed at the top left of this form after the document is saved."
					),
				},
				{
					"title": "Membership",
					"fieldname": "is_member",
					"fieldtype": "Check",
					"position": "Top",
					"description": (
						"Let's check this box to set this person as a member of the church.\n"
						"Additional fields will be displayed to track the membership date and status."
					),
					"has_next_condition": 1,
					"next_step_condition": "eval:doc.is_member == 1;",
				},
				{
					"title": "Membership Date",
					"fieldname": "membership_date",
					"fieldtype": "Date",
					"element_selector": '[data-fieldname="membership_date"]',
					"position": "Top Right",
					"description": (
						"A membership date is required when checking the `Is Member` box.\n"
						"Let's choose today's date as the membership date."
					),
					"has_next_condition": 1,
					"next_step_condition": "eval: doc.membership_date;",
				},
				{
					"title": "Membership Status",
					"fieldname": "membership_status",
					"fieldtype": "Link",
					"position": "Right",
					"description": (
						"Let's set this person as an `Active` member, but note that additional"
						" `Membership Status Type`s can be created directly from the drop-down list."
					),
					"has_next_condition": 1,
					"next_step_condition": 'eval: doc.membership_status=="Active";',
				},
				{
					"title": "Church",
					"fieldname": "church",
					"fieldtype": "Link",
					"position": "Top",
					"description": (
						"Select the `Church` this person belongs to.\n"
						"This links the person to their church congregation."
					),
				},
				{
					"title": "Church Position",
					"fieldname": "positions",
					"fieldtype": "Table",
					"position": "Top Center",
					"description": (
						"You can define `Church Position`s that this person has been or is currently assigned.\n"
						"Go ahead and assign this person a 'Secretary' position starting today by clicking"
						" on the `Add Row` button below."
					),
					"next_step_condition": "eval: doc.positions;",
				},
			],
		}
	).insert(ignore_permissions=True)


def _create_form_tour_church():
	"""Walk a user through filling in their Church record."""
	if frappe.db.exists("Form Tour", "Church"):
		return

	frappe.get_doc(
		{
			"doctype": "Form Tour",
			"name": "Church",
			"title": "Church",
			"reference_doctype": "Church",
			"module": "Desk",
			"is_standard": 1,
			"save_on_complete": 0,
			"steps": [
				{
					"title": "Legal Name",
					"fieldname": "legal_name",
					"fieldtype": "Data",
					"element_selector": "div.form-dashboard",
					"position": "Bottom",
					"description": (
						"All of the information entered on this page may be used on the"
						" public-facing website. (i.e. in the footer or 'about-us' page.).\n"
						"When you are finished entering the information, click the 'save'"
						" button at the top right."
					),
				},
			],
		}
	).insert(ignore_permissions=True)


def _create_onboarding_steps():
	"""Create the 'Church Manager' Onboarding Step.

	Explains how to set up the first admin user and links to the Form Tour above.
	"""
	if frappe.db.exists("Onboarding Step", "Church Manager"):
		return

	frappe.get_doc(
		{
			"doctype": "Onboarding Step",
			"name": "Church Manager",
			"title": "Church Manager",
			"action": "Create Entry",
			"action_label": "Create Church Manager User",
			"reference_document": "User",
			"form_tour": "Church Manager",
			"show_form_tour": 1,
			"show_full_form": 1,
			"validate_action": 1,
			"description": (
				"Before you get started, you should create a new user. The `Administrator`"
				" user should not be used on a daily basis and should be reserved for"
				" setting up new users, troubleshooting and system configuration. At least"
				" one separate user should be created with the `Church Manager` RoleProfile"
				" and the `Church` ModuleProfile permissions. These users will have full"
				" access to the Church app.\n\nAdditional users can also be created with"
				" the `Church User` RoleProfile and no ModuleProfile permissions. These"
				" users will only have access to specific forms.\n\nTo see the exact"
				" permissions that a user has, you can (with the `Administrator` account)"
				" use the search bar at the top to search for `Role Permissions Manager`"
				" and select the `Church Manager` or `Church User` role to see what is"
				" accessible by each type of user.\n\nTo summarize:\n- Only the"
				" `Administrator` user has permission to create new users.\n- `Church"
				" Managers` have full access to the Church app - This is best for church"
				" leadership.\n- `Church Users` have limited (portal) access - This is"
				" best for church members/attendees."
			),
		}
	).insert(ignore_permissions=True)


def _create_module_onboarding():
	"""Create the 'Church' Module Onboarding shown on the Church workspace.

	Guides new installations through essential setup steps.
	"""
	if frappe.db.exists("Module Onboarding", "Church"):
		return

	frappe.get_doc(
		{
			"doctype": "Module Onboarding",
			"name": "Church",
			"title": "⛪ Let's Set Up Your Church.",
			"subtitle": "People, Families, Events, Ministries, Collections, and more...",
			"module": "Church Foundations",
			"documentation_url": "https://github.com/meichthys/church",
			"success_message": "Your Church is setup! 🎉 May God grow your ministry 🙏",
			"allow_roles": [
				{"role": "Administrator"},
				{"role": "Church Manager"},
				{"role": "Church User"},
			],
			"steps": [
				{"step": "Email Configuration"},
				{"step": "Church Manager"},
				{"step": "Church"},
				{"step": "Person"},
				{"step": "Family"},
				{"step": "Function"},
				{"step": "Prayer Request"},
			],
		}
	).insert(ignore_permissions=True)


# ---------------------------------------------------------------------------
# Web Pages — dynamic Jinja templates stored in templates/*.html
# ---------------------------------------------------------------------------


def _create_web_pages():
	"""Create the four default church website pages.

	HTML content is stored in separate template files under templates/ so it
	can be edited without touching this Python script.
	"""
	pages = [
		{
			"name": "home",
			"title": "Home",
			"route": "home",
			"template_file": "home.html",
		},
		{
			"name": "beliefs",
			"title": "Beliefs",
			"route": "beliefs",
			"template_file": "beliefs.html",
		},
		{
			"name": "missions",
			"title": "Missions",
			"route": "missions",
			"template_file": "missions.html",
		},
		{
			"name": "locations",
			"title": "Locations",
			"route": "locations",
			"template_file": "locations.html",
		},
	]
	for page in pages:
		if frappe.db.exists("Web Page", page["name"]):
			continue
		frappe.get_doc(
			{
				"doctype": "Web Page",
				"name": page["name"],
				"title": page["title"],
				"route": page["route"],
				"published": 1,
				"dynamic_template": 1,
				"content_type": "HTML",
				"module": "Church Website",
				"show_title": 1,
				"text_align": "Center",
				"main_section_html": _read_template(page["template_file"]),
			}
		).insert(ignore_permissions=True)


# ---------------------------------------------------------------------------
# Single DocType setup
# Only set the specific fields we own; leave all other fields untouched so
# we do not overwrite anything the user may have configured.
# ---------------------------------------------------------------------------


def _setup_about_us_settings():
	"""Populate the About Us page with default church-oriented content."""
	doc = frappe.get_doc("About Us Settings")
	doc.page_title = "About Our Church"
	doc.company_introduction = (
		"<p>We are a congregation of believers committed to worshipping God, growing"
		" in His Word, and serving one another and our community in love.</p>"
		'<p>To learn more about what we believe, visit our <a href="/beliefs">Beliefs</a>'
		" page. To see how we support missionaries around the world, visit our"
		' <a href="/missions">Missions</a> page.</p>'
	)
	doc.company_history_heading = "Church History"
	doc.team_members_heading = "Our Leadership"
	doc.save(ignore_permissions=True)


def _setup_website_settings():
	"""Configure default website settings for a church site.

	Sets the app name, login visibility, home page, theme, and navigation bar.
	Only the fields listed here are written; any other Website Settings fields
	that the user has configured are left untouched.
	"""
	doc = frappe.get_doc("Website Settings")
	doc.app_name = "Church"
	doc.disable_signup = 1
	doc.hide_login = 1
	doc.home_page = "home"
	doc.website_theme = "Standard"
	doc.top_bar_items = []
	for item in [
		{"label": "Home", "url": "/home", "right": 1},
		{"label": "Beliefs", "url": "/beliefs", "right": 1},
		{"label": "Missions", "url": "/missions", "right": 1},
		{"label": "Locations", "url": "/locations", "right": 1},
		{"label": "Blog", "url": "/blog", "right": 1},
		{"label": "About Us", "url": "/about", "right": 1},
		{"label": "Contact Us", "url": "/contact", "right": 1},
		{"label": "Login", "url": "/login", "right": 1},
	]:
		doc.append("top_bar_items", item)
	doc.save(ignore_permissions=True)


def _setup_portal_menu_items():
	"""Append Church portal menu items to Portal Settings.

	Items are only appended if they are not already present, so this is safe
	to run on sites that may have other portal menu items configured.
	"""
	desired_items = [
		{
			"title": "Prayer Requests",
			"route": "prayer-request",
			"reference_doctype": "Prayer Request",
			"enabled": 1,
		},
		{
			"title": "Alms Requests",
			"route": "alms-request",
			"reference_doctype": "Alms Request",
			"enabled": 1,
		},
	]
	doc = frappe.get_doc("Portal Settings")
	existing_titles = {row.title for row in doc.custom_menu}
	changed = False
	for item in desired_items:
		if item["title"] not in existing_titles:
			doc.append("custom_menu", item)
			changed = True
	if changed:
		doc.save(ignore_permissions=True)


# ---------------------------------------------------------------------------
# Gender cleanup
# ---------------------------------------------------------------------------


def _clean_gender_options():
	"""Remove non-biblical genders from Frappe's default gender list.

	Keeps only Male, Female, and Unknown.
	"""
	for gender in frappe.db.get_all("Gender"):
		if gender.name not in ("Male", "Female", "Unknown"):
			frappe.delete_doc("Gender", gender.name, force=True)
