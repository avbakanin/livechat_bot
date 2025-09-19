-- Скрипт для изменения значения по умолчанию колонки gender_preference в таблице users
-- Изменяет значение по умолчанию с 'female' на NULL

-- Проверяем текущее значение по умолчанию
SELECT column_name, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' 
  AND table_schema = 'public' 
  AND column_name = 'gender_preference';

-- Изменяем значение по умолчанию для колонки gender_preference
ALTER TABLE public.users 
ALTER COLUMN gender_preference SET DEFAULT NULL;

-- Проверяем, что изменение применилось
SELECT column_name, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' 
  AND table_schema = 'public' 
  AND column_name = 'gender_preference';

-- Показываем статистику gender_preference в таблице
SELECT gender_preference, COUNT(*) as user_count
FROM public.users 
GROUP BY gender_preference 
ORDER BY user_count DESC;
