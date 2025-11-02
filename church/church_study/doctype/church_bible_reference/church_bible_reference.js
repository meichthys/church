frappe.ui.form.on("Church Bible Reference", {
    import_reference_text: frm => {
        fetch_bible_text(frm);
    }
});

async function fetch_bible_text(frm) {
    try {
        const start_verse = await get_verse_reference(frm.doc.start_verse);
        const end_verse = frm.doc.end_verse ? await get_verse_reference(frm.doc.end_verse) : null;
        const translation = await get_translation(frm.doc.translation);

        if (!start_verse || !translation) {
            frappe.msgprint("Missing start verse or translation information.");
            return;
        }

        // Build passage string
        let passage = `${start_verse.book} ${start_verse.chapter}:${start_verse.verse}`;
        if (end_verse) {
            passage += `-${end_verse.chapter}:${end_verse.verse}`;
        }

        // Check if translation is supported
        const translationsData = await fetch("https://bible-api.com/data")
            .then(res => {
                if (!res.ok) throw new Error(`Failed to fetch translation data (${res.status})`);
                return res.json();
            });
        const supportedTranslations = (translationsData.translations || []).map(t => t.identifier || t.id);
        const version = (translation.abbreviation || "").toLowerCase();

        if (!supportedTranslations.includes(version)) {
            frappe.msgprint(`The “${translation.abbreviation}” translation is not supported by bible-api.com.
                It is likely that the version you are trying to use is copyrighted and therefore illegal to
                use freely. We recommend using translations that are not bound by copyright because God's word
                should not be for sale! (see <a href="https://copy.church/initiatives/bibles/">
                https://copy.church/initiatives/bibles/</a> for more details.)`, "Unsupported Translation");
            return;
        }


        const url = `https://bible-api.com/${encodeURIComponent(passage)}?translation=${version}`;

        // Fetch passage from https://bible-api.com/
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Failed to fetch passage (${response.status})`);
        const data = await response.json();

        frm.set_value("reference_text", data.text.trim());
        frappe.show_alert({ message: "Bible passage fetched!", indicator: "green" }, 3);

    } catch (err) {
        console.error(err);
        frappe.msgprint("Error fetching passage. Please ensure you have valid verse references.");
    }
}

// Fetch a Bible verse from DB
function get_verse_reference(name) {
    if (!name) return Promise.resolve(null);
    return frappe.db.get_doc("Church Bible Verse", name)
        .then(doc => ({ book: doc.book, chapter: doc.chapter, verse: doc.verse }))
        .catch(() => {
            console.warn("Verse not found:", name);
            return null;
        });
}

// Fetch translation from DB
function get_translation(name) {
    if (!name) return Promise.resolve(null);
    return frappe.db.get_doc("Church Bible Translation", name)
        .catch(() => {
            console.warn("Translation not found:", name);
            return null;
        });
}
