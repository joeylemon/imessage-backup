-- Get a list of all messages including their group names and list of participants
SELECT
	m.rowid as id,
	CASE
		WHEN c.display_name != '' THEN c.display_name
		ELSE c.chat_identifier
	END as chat_title,
	c.chat_identifier,
	GROUP_CONCAT(h1.id) as participants,
	h2.id as sender,
	m.is_from_me,
	m.text,
	m.date,
	a.filename as attachment_path
FROM message m
LEFT JOIN chat_message_join cmj ON cmj.message_id = m.rowid
LEFT JOIN chat c ON cmj.chat_id = c.rowid
LEFT JOIN chat_handle_join chj ON chj.chat_id = c.rowid
LEFT JOIN handle h1 ON chj.handle_id = h1.rowid
LEFT JOIN handle h2 ON m.handle_id = h2.rowid
LEFT JOIN message_attachment_join maj ON maj.message_id = m.rowid
LEFT JOIN attachment a ON a.rowid = maj.attachment_id
WHERE m.text IS NOT NULL
GROUP BY m.rowid;