// Copyright (c) 2025, meichthys and contributors
// For license information, please see license.txt


frappe.ui.form.on('Church Event', {
	before_save(frm) {
		// Update Attendance Total when saving
		// Only include the number of 'Confirmed' and 'Assumed' attendees
		var total_attendance = 0;
		frm.doc.attendance.forEach(function (row) {
			if (["Confirmed", "Assumed"].includes(row.attendance_type)) {
				total_attendance += 1;
			}
		});
		frm.set_value('attendance_total', total_attendance);
	}
});
