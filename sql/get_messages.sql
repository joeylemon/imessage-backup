-- Get a list of all messages including their chat identifier.
SELECT
	m.rowid as id,
	c.chat_identifier,
	h.id as sender,
	m.is_from_me,
	m.text,
	m.date,
	a.filename as attachment_path
FROM message m
LEFT JOIN chat_message_join cmj ON cmj.message_id = m.rowid
LEFT JOIN chat c ON cmj.chat_id = c.rowid
LEFT JOIN handle h ON m.handle_id = h.rowid
LEFT JOIN message_attachment_join maj ON maj.message_id = m.rowid
LEFT JOIN attachment a ON a.rowid = maj.attachment_id
WHERE m.text IS NOT NULL OR a.filename IS NOT NULL
ORDER BY m.date;