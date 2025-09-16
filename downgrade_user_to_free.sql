-- Превращение пользователя 627875032 в обычного (бесплатного)

-- 1. Обновить пользователя до бесплатного статуса
UPDATE users 
SET 
    subscription_status = 'free',
    subscription_expires_at = NULL,
    consent_given = TRUE,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 627875032;

-- 2. Проверить результат
SELECT 
    id,
    username,
    first_name,
    subscription_status,
    subscription_expires_at,
    consent_given,
    created_at,
    updated_at
FROM users 
WHERE id = 627875032;
