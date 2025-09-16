-- Диагностика и исправление пользователя 627875032

-- 1. Проверить, существует ли пользователь
SELECT 
    id,
    username,
    first_name,
    subscription_status,
    subscription_expires_at,
    consent_given,
    created_at
FROM users 
WHERE id = 627875032;

-- 2. Если пользователя нет, создать его с премиум статусом
INSERT INTO users (
    id, 
    username, 
    first_name, 
    subscription_status, 
    subscription_expires_at,
    consent_given
) VALUES (
    627875032, 
    'test_user', 
    'Test User', 
    'premium', 
    CURRENT_TIMESTAMP + INTERVAL '4 months',
    TRUE
) ON CONFLICT (id) DO UPDATE SET
    subscription_status = 'premium',
    subscription_expires_at = CURRENT_TIMESTAMP + INTERVAL '4 months',
    consent_given = TRUE,
    updated_at = CURRENT_TIMESTAMP;

-- 3. Проверить результат
SELECT 
    id,
    username,
    first_name,
    subscription_status,
    subscription_expires_at,
    subscription_expires_at - CURRENT_TIMESTAMP as time_remaining,
    consent_given
FROM users 
WHERE id = 627875032;

-- 4. Проверить кэш пользователя (если есть таблица кэша)
-- SELECT * FROM user_cache WHERE user_id = 627875032;
