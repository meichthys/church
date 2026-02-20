// Copyright (c) 2025, meichthys and contributors
// For license information, please see license.txt

frappe.ui.form.on('Church Prayer Request', {
    recipient_type: function(frm) {
        // Dynamically update the Recipient field description based on the Recipient Type that is selected
        if (frm.doc.recipient_type) {
            frm.set_df_property('recipient', 'description', `Prayers are requested for this ${frm.doc.recipient_type}.`);
        }
    },
    onload: function(frm) {
        // Pre-populate the requestor field with the current user's name
        if (frm.is_new()) {
            frappe.db.get_value('Church Person', {'portal_user': frappe.session.user}, 'name')
                .then(r => {
                    if (r && r.message) {
                        frm.set_value('requestor', r.message.name);
                    }
                });
        }
    }
});