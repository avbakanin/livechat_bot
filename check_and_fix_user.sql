-- Проверка пользователя 627875032 в базе данных
SELECT 
    id,
    username,
    first_name,
    last_name,
    gender_preference,
    subscription_status,
    consent_given,
    subscription_expires_at,
    created_at,
    updated_at
FROM users 
WHERE id = 627875032;

-- Если пользователя нет, создадим его
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
    updated_at = CURRENT_TIMESTAMP;

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
