// Copyright (c) 2025, meichthys and contributors
// For license information, please see license.txt

frappe.ui.form.on("Church Missionary", {
	refresh(frm) {
        //Add an 'intro' indicating if a missionary is published to the website
        if (frm.doc.sensitive && frm.doc.publish){
            frm.set_intro('🚨 This missionary is marked as sensitive and is published \
                to the public website. Make sure sensitive content is not being \
                leaked to the public!', 'red')
        }
        else if(frm.doc.sensitive) {
            frm.set_intro('⚠️ This missionary is marked as sensitive. \
                be careful not to disclose sensitive information.', 'yellow');
        }
        else if(frm.doc.publish) {
            frm.set_intro('🌐 This missionary is published to the public website', 'blue');
        }
	},
});
