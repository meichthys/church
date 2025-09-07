// Copyright (c) 2025, meichthys and contributors
// For license information, please see license.txt

// Add button to goto `Church Collection Bank Reconciliation` report
frappe.ui.form.on("Church Collection", {
	refresh(frm) {
		// Add 'Bank Reconciliation Report' button
		frm.add_custom_button(__('Bank Reconciliation Report'), function () {
			if (frm.is_new()) {
				frappe.show_alert("Save the Collection first!")
				return;
			};
			frm.refresh_field('date');
			frappe.set_route("query-report", "Church Collection Bank Reconciliation", {
				"parent_filter": frm.doc.date
			});
			frappe.query_report.load();
		});
	},
});



// Keep Collection `total_amount` up to date when amounts are changed/added
frappe.ui.form.on("Church Donation", "amount", update_collection_total);
// Keep Collection `total_amount` up to date when rows are removed from grid
frappe.ui.form.on("Church Donation", {
	donations_remove: update_collection_total
});

// Update Collection `total_amount` with sum of donation amounts
function update_collection_total(frm) {
	var total = 0;
	frm.doc.donations.forEach(function (donation) {
		total += donation.amount || 0;
	});
	frm.set_value("total_amount", total);
}
