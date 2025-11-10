// Copyright (c) 2025, meichthys and contributors
// For license information, please see license.txt

frappe.ui.form.on('Church Bible Verse', {
    after_save: function(frm) {
        // If document was renamed, reload to new URL
        const expected_name = `${frm.doc.book} ${frm.doc.chapter}:${frm.doc.verse}`;
        if (frm.doc.name !== expected_name) {
            frappe.set_route('Form', frm.doctype, expected_name);
        }
    },

    refresh: async function(frm) {
        // Set chapter options when form loads
        if (frm.doc.book) {
            try {
                let chapters = await get_chapter_count(frm.doc.book);
                let options = Array.from({ length: chapters }, (_, i) => i + 1).join('\n');
                frm.set_df_property('chapter', 'options', options);
            } catch (e) {
                frm.set_df_property('chapter', 'options', Array.from({ length: 150}, (_, i) => i + 1).join('\n'));
            }
        }
        // Set verse options when form loads
        if (frm.doc.book && frm.doc.chapter) {
            try {
                let verses = await get_verse_count(frm.doc.book, frm.doc.chapter);
                let options = Array.from({ length: verses }, (_, i) => i + 1).join('\n');
                frm.set_df_property('verse', 'options', options);
            } catch (e) {
                frm.set_df_property('verse', 'options', Array.from({ length: 176 }, (_, i) => i + 1).join('\n'));
            }
        }
    },

    book: async function(frm) {
        // Set options for chapter field when book changes
        try {
            let chapters = await get_chapter_count(frm.doc.book);
            let options = Array.from({ length: chapters }, (_, i) => i + 1).join('\n');
            frm.set_df_property('chapter', 'options', options);
        } catch (e) {
            frm.set_df_property('chapter', 'options', Array.from({ length: 150}, (_, i) => i + 1).join('\n'));
        }
    },

    chapter: async function(frm) {
        // Set options for verse field when chapter changes
        try {
            let verses = await get_verse_count(frm.doc.book, frm.doc.chapter);
            let options = Array.from({ length: verses }, (_, i) => i + 1).join('\n');
            frm.set_df_property('verse', 'options', options);
        } catch (e) {
            frm.set_df_property('verse', 'options', Array.from({ length: 176 }, (_, i) => i + 1).join('\n'));
        }
    }
});

async function get_chapter_count(book) {
    // Get the number of chapters in a book
    const book_doc = await frappe.db.get_doc("Church Bible Book", book);
    let book_abbreviation = book_doc.abbreviation
    const url = `https://bible-api.com/data/kjv/${book_abbreviation}`;
    const resp = await fetch(url);
    if (!resp.ok) {
        frappe.show_alert(`Failed to fetch chapter count for ${book}`, indicator="yellow")
    }
    const data = await resp.json();
    const chapters = data.chapters;
    if (!Array.isArray(chapters)) {
        frappe.show_alert(`Failed to fetch chapter count for ${book}`, indicator="yellow")
    }
    return chapters.length;
}

async function get_verse_count(book, chapter) {
    // Get the number of verses in a chapter of a book
    const book_doc = await frappe.db.get_doc("Church Bible Book", book);
    let book_abbreviation = book_doc.abbreviation
    const url = `https://bible-api.com/data/kjv/${book_abbreviation}/${chapter}`;
    const resp = await fetch(url);
    if (!resp.ok) {
        frappe.show_alert({message:`Failed to fetch verse count for ${book}`, indicator:"yellow"},5)
        throw new Error("Failed to fetch verse count");
    }
    const data = await resp.json();
    const verses = data.verses;
    if (!Array.isArray(verses)) {
        frappe.show_alert({message:`Failed to fetch verse count for ${book}`, indicator:"yellow"},5)
    }
    return verses.length;
}