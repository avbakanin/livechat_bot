-- Обновление пользователя 627875032 до премиум статуса на 4 месяца
-- Дата истечения: текущая дата + 4 месяца

UPDATE users 
SET 
    subscription_status = 'premium',
    subscription_expires_at = CURRENT_TIMESTAMP + INTERVAL '4 months'
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
