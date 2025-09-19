-- Скрипт для изменения значения по умолчанию колонки language в таблице users
-- Изменяет значение по умолчанию с 'ru' на 'en'

-- Проверяем текущее значение по умолчанию
SELECT column_name, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' 
  AND table_schema = 'public' 
  AND column_name = 'language';

-- Изменяем значение по умолчанию для колонки language
ALTER TABLE public.users 
ALTER COLUMN language SET DEFAULT 'en';

-- Проверяем, что изменение применилось
SELECT column_name, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' 
  AND table_schema = 'public' 
  AND column_name = 'language';

-- Опционально: обновляем существующих пользователей, у которых language = 'ru'
-- (только если хотите, чтобы все существующие пользователи с русским языком получили английский)
-- UPDATE public.users SET language = 'en' WHERE language = 'ru';

-- Показываем статистику языков в таблице
SELECT language, COUNT(*) as user_count
FROM public.users 
GROUP BY language 
ORDER BY user_count DESC;
