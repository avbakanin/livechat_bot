-- Полное понижение пользователя 627875032 до бесплатного статуса

-- 1. Обновить пользователя до бесплатного статуса
UPDATE users 
SET 
    subscription_status = 'free',
    subscription_expires_at = NULL,
    consent_given = TRUE,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 627875032;

-- 2. Очистить кэш пользователя (если есть таблица кэша)
-- DELETE FROM user_cache WHERE user_id = 627875032;

-- 3. Проверить результат
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

-- 4. Проверить, что пользователь теперь бесплатный
SELECT 
    CASE 
        WHEN subscription_status = 'free' THEN '✅ Пользователь бесплатный'
        WHEN subscription_status = 'premium' AND subscription_expires_at IS NULL THEN '⚠️ Премиум без даты истечения'
        WHEN subscription_status = 'premium' AND subscription_expires_at > CURRENT_TIMESTAMP THEN '❌ Премиум все еще активен'
        ELSE '❓ Неизвестный статус'
    END as status_check
FROM users 
WHERE id = 627875032;
