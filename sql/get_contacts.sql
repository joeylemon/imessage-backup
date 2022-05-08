-- Get a list of all contacts including a list of their identifiers (phone numbers, emails)
SELECT
	a.rowid as id,
	a."First" as first_name,
	a."Last" as last_name,
	GROUP_CONCAT(av.value) as identifiers
FROM ABPerson a
LEFT JOIN ABMultiValue av ON av.record_id = a.rowid
WHERE av.value IS NOT NULL
GROUP BY a.rowid
ORDER BY a.rowid;