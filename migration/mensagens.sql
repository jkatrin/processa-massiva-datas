CREATE TABLE IF NOT EXISTS mensagens (
    id INT PRIMARY KEY, -- Garante a não duplicidade: se existe, atualiza; se não, insere
    sender VARCHAR(100),
    message TEXT,
    timestamp DATETIME
)