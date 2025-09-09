// Copyright (c) 2025, meichthys and contributors
// For license information, please see license.txt

frappe.ui.form.on("Church Person", {
	refresh(frm) {
		// Add 'New Family From Person' button
		frm.add_custom_button(__('New Family From Person'), function () {
			frm.call("new_family_from_person")
		});
		// Add 'Church Person Tour' button
		frm.add_custom_button(__('Tutorial'), function () {
			frm.tour.init("Church Person").then(() => frm.tour.start());
		});
	},
	before_save(frm) {
		// Call ensure_single_head_of_household
		frm.call("ensure_single_head_of_household");
		// Call add_spouse_to_relationships
		frm.call("add_spouse_to_relationships");
	},
	after_save(frm) {
		frm.call("update_is_current_role")
	},

});


