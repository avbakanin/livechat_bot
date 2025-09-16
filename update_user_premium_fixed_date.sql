-- Альтернативный вариант: установка конкретной даты истечения
-- Например, до 1 мая 2025 года

UPDATE users 
SET 
    subscription_status = 'premium',
    subscription_expires_at = '2025-05-01 00:00:00'::timestamp
WHERE id = 627875032;

-- Проверка результата
SELECT 
    id,
    username,
    first_name,
    subscription_status,
    subscription_expires_at,
    subscription_expires_at - CURRENT_TIMESTAMP as time_remaining
FROM users 
WHERE id = 627875032;
