// Copyright (c) 2025, meichthys and contributors
// For license information, please see license.txt

frappe.ui.form.on('Church Alms Request', {
    refresh(frm) {
        // Add a custom button that creates an Expense from the Alms Request
        if (!frm.is_new()) {
            frm.add_custom_button(__('Create Expense'), function () {
                frappe.call({
                    method: 'church.church_finances.doctype.church_alms_request.church_alms_request.create_expense',
                    args: {
                        alms_request_name: frm.doc.name
                    },
                    callback: function () {
                        frm.reload_doc();
                    }
                });
            });
        }
    },
});



