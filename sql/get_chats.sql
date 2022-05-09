-- Get a list of all chat conversations with their last message date.
SELECT
    DISTINCT c.rowid as id,
	c.chat_identifier,
	c.display_name,
	MAX(cmj.message_date) as last_message_date,
	GROUP_CONCAT(DISTINCT h.id) as participants
FROM chat c
LEFT JOIN chat_message_join cmj ON cmj.chat_id = c.rowid
LEFT JOIN chat_handle_join chj ON chj.chat_id = c.rowid
LEFT JOIN handle h ON h.rowid = chj.handle_id
WHERE cmj.message_date IS NOT NULL
GROUP BY c.chat_identifier
ORDER BY last_message_date DESC;