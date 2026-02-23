// Copyright (c) 2025, meichthys and contributors
// For license information, please see license.txt

frappe.ui.form.on("Church Person", {
	refresh(frm) {
		// Add 'New Family From Person' button if Last Name is populated
		if (frm.doc.last_name) {
			frm.add_custom_button(__('New Family From Person'), function () {
				frm.call("new_family_from_person")
			})
		}

		// Add 'Invite to Portal' button if email is provided and no Portal User is linked
		if (frm.doc.email && !frm.doc.portal_user) {
			frm.add_custom_button(__('Invite to Portal'), function () {
				frm.call("invite_to_portal")
			});
		}

		// Add 'Church Person Tour' button
		frm.add_custom_button(__('Tutorial'), function () {
			frm.tour.init("Church Person").then(() => frm.tour.start());
		});

	},

	after_save(frm) {
		frm.call("update_is_current_role")
	},

	// Set mailing address to home address if "Different Mailing Address" is unchecked
	before_save: function(frm) {
		if (!frm.doc.different_mailing_address) {
			frm.set_value("mailing_address", frm.doc.home_address);
		}
	}

});
