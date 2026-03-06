const CHURCH_SCOPED_ROLES = new Set(["Church Manager", "Church User"]);

frappe.ui.form.on("User", {
	validate(frm) {
		const has_church_role = (frm.doc.roles || []).some(r => CHURCH_SCOPED_ROLES.has(r.role));
		if (has_church_role && !frm.doc.church) {
			frappe.msgprint({
				title: __("Missing Church"),
				message: __(
					"This user has a church-scoped role but no Church is assigned. ",
					"They will be able to see records from all churches until a church is set."
				),
				indicator: "orange",
			});
		}
	},
});
