INSERT INTO mensagens (id, sender, message, timestamp)
VALUES (%s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    sender = VALUES(sender),
    message = VALUES(message),
    timestamp = VALUES(timestamp);
