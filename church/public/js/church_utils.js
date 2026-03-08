window.church = window.church || {};

// Auto-fill the `church` field on new documents using the current user's default church.
frappe.ui.form.on("*", {
	onload(frm) {
		if (frm.is_new() && frm.fields_dict.church) {
			const default_church = frappe.defaults.get_user_default("church");
			if (default_church) {
				frm.set_value("church", default_church);
			}
		}
	}
});

// Sets a query filter on a DocType link field to only show DocTypes belonging to the church app.
// fieldname: the Link field to filter
// child_table: (optional) the child table fieldname if the field is in a child doctype
church.set_church_doctype_query = function(frm, fieldname, child_table) {
	frappe.db.get_list('Module Def', {
		filters: { app_name: 'church' },
		fields: ['name'],
		limit: 0
	}).then(modules => {
		const module_names = modules.map(m => m.name);
		const query = function() {
			return {
				filters: [['DocType', 'module', 'in', module_names]]
			};
		};
		if (child_table) {
			frm.set_query(fieldname, child_table, query);
		} else {
			frm.set_query(fieldname, query);
		}
	});
};
