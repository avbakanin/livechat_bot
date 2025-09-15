CREATE TABLE public.users (
    id BIGINT NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    gender_preference TEXT DEFAULT 'female',
    subscription_status TEXT DEFAULT 'free',
	consent_given BOOLEAN DEFAULT FALSE,
	subscription_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT users_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_users_subscription_expires_at ON public.users USING btree (subscription_expires_at);

-- Partitioned messages table by month on created_at
CREATE TABLE public.messages (
    id BIGSERIAL NOT NULL,
    user_id BIGINT NOT NULL,
    role TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT messages_pkey PRIMARY KEY (id, created_at),
    CONSTRAINT messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
) PARTITION BY RANGE (created_at);

-- Global index definition will be created on each partition
CREATE INDEX idx_messages_user_id_created_at ON public.messages USING btree (user_id, created_at DESC);

-- Helper: ensure monthly partition exists for a given month start date
CREATE OR REPLACE FUNCTION public.ensure_messages_partition(p_month_start DATE)
RETURNS VOID LANGUAGE plpgsql AS $$
DECLARE
    v_start TIMESTAMP;
    v_end   TIMESTAMP;
    v_suffix TEXT;
    v_partition_name TEXT;
BEGIN
    v_start := date_trunc('month', p_month_start)::timestamp;
    v_end := (v_start + INTERVAL '1 month');
    v_suffix := to_char(v_start, 'YYYYMM');
    v_partition_name := format('messages_%s', v_suffix);

    IF NOT EXISTS (
        SELECT 1 FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relname = v_partition_name
    ) THEN
        EXECUTE format(
            'CREATE TABLE public.%I PARTITION OF public.messages FOR VALUES FROM (%L) TO (%L)',
            v_partition_name, v_start, v_end
        );
    END IF;
END;
$$;

-- Initialize partitions for current and next month
# выполняется 25ого числа каждого месяца, создавая партицию на следующий месяц
# SELECT public.ensure_messages_partition(date_trunc('month', CURRENT_DATE)::date);

# выполняется 1ого числа каждого месяца, удаляя партицию с данными за пред предыдущий месяц
# SELECT public.drop_messages_partition((date_trunc('month', CURRENT_DATE) - INTERVAL '2 months')::date);


-- Cleanup helper: drop partition for a given month start (useful on month rollover)
CREATE OR REPLACE FUNCTION public.drop_messages_partition(p_month_start DATE)
RETURNS VOID LANGUAGE plpgsql AS $$
DECLARE
    v_start TIMESTAMP;
    v_suffix TEXT;
    v_partition_name TEXT;
BEGIN
    v_start := date_trunc('month', p_month_start)::timestamp;
    v_suffix := to_char(v_start, 'YYYYMM');
    v_partition_name := format('messages_%s', v_suffix);

    IF EXISTS (
        SELECT 1 FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relname = v_partition_name
    ) THEN
        EXECUTE format('DROP TABLE public.%I', v_partition_name);
    END IF;
END;
$$;

-- Optional: unique constraint on id to aid lookups by id
# CREATE UNIQUE INDEX IF NOT EXISTS idx_messages_id_unique ON public.messages (id);

CREATE TABLE public.payments (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_status TEXT NOT NULL,
    payment_id TEXT,  -- ID платежа от YooKassa
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT payments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);
CREATE INDEX idx_payments_user_id ON public.payments USING btree (user_id);


CREATE TABLE IF NOT EXISTS public.user_daily_counters (
    user_id BIGINT NOT NULL,
    date DATE NOT NULL,
    message_count INTEGER DEFAULT 0,
    last_reset_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_daily_counters_pkey PRIMARY KEY (user_id, date),
    CONSTRAINT user_daily_counters_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);

-- Index for efficient date-based queries
CREATE INDEX IF NOT EXISTS idx_user_daily_counters_date ON public.user_daily_counters USING btree (date);

-- Function to increment user's daily message count
CREATE OR REPLACE FUNCTION public.increment_user_daily_count(p_user_id BIGINT, p_date DATE DEFAULT CURRENT_DATE)
RETURNS INTEGER LANGUAGE plpgsql AS $$
DECLARE
    v_count INTEGER;
BEGIN
    -- Insert or update counter for the user and date
    INSERT INTO public.user_daily_counters (user_id, date, message_count)
    VALUES (p_user_id, p_date, 1)
    ON CONFLICT (user_id, date)
    DO UPDATE SET 
        message_count = user_daily_counters.message_count + 1,
        last_reset_at = CURRENT_TIMESTAMP
    RETURNING message_count INTO v_count;
    
    RETURN v_count;
END;
$$;

-- Function to get user's daily message count
CREATE OR REPLACE FUNCTION public.get_user_daily_count(p_user_id BIGINT, p_date DATE DEFAULT CURRENT_DATE)
RETURNS INTEGER LANGUAGE plpgsql AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COALESCE(message_count, 0) INTO v_count
    FROM public.user_daily_counters
    WHERE user_id = p_user_id AND date = p_date;
    
    RETURN COALESCE(v_count, 0);
END;
$$;

-- Function to reset all counters for a specific date (useful for cleanup)
CREATE OR REPLACE FUNCTION public.reset_daily_counters_for_date(p_date DATE)
RETURNS INTEGER LANGUAGE plpgsql AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    DELETE FROM public.user_daily_counters WHERE date = p_date;
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RETURN v_deleted_count;
END;
$$;

-- Function to cleanup old counters (older than 30 days)
CREATE OR REPLACE FUNCTION public.cleanup_old_counters()
RETURNS INTEGER LANGUAGE plpgsql AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    DELETE FROM public.user_daily_counters 
    WHERE date < CURRENT_DATE - INTERVAL '30 days';
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RETURN v_deleted_count;
END;
$$;

-- Bot metrics table for persistent storage
CREATE TABLE public.bot_metrics (
    id SERIAL PRIMARY KEY,
    metric_name TEXT NOT NULL UNIQUE,
    metric_value BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default metrics
INSERT INTO public.bot_metrics (metric_name, metric_value) VALUES
('total_messages_processed', 0),
('successful_responses', 0),
('failed_responses', 0),
('limit_exceeded_count', 0),
('active_users_today', 0),
('new_users_today', 0),
('openai_errors', 0),
('database_errors', 0),
('validation_errors', 0),
('cache_hits', 0),
('cache_misses', 0),
('total_response_time', 0),
('average_response_time', 0),
('uptime_seconds', 0),
('last_reset', EXTRACT(EPOCH FROM NOW())),
('started_at', EXTRACT(EPOCH FROM NOW()))
ON CONFLICT (metric_name) DO NOTHING;

-- Function to get metric value
CREATE OR REPLACE FUNCTION public.get_metric(p_metric_name TEXT)
RETURNS BIGINT LANGUAGE plpgsql AS $$
DECLARE
    v_value BIGINT;
BEGIN
    SELECT metric_value INTO v_value 
    FROM public.bot_metrics 
    WHERE metric_name = p_metric_name;
    
    RETURN COALESCE(v_value, 0);
END;
$$;

-- Function to set metric value
CREATE OR REPLACE FUNCTION public.set_metric(p_metric_name TEXT, p_value BIGINT)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO public.bot_metrics (metric_name, metric_value, updated_at)
    VALUES (p_metric_name, p_value, CURRENT_TIMESTAMP)
    ON CONFLICT (metric_name) 
    DO UPDATE SET 
        metric_value = p_value,
        updated_at = CURRENT_TIMESTAMP;
END;
$$;

-- Function to increment metric value
CREATE OR REPLACE FUNCTION public.increment_metric(p_metric_name TEXT, p_increment BIGINT DEFAULT 1)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO public.bot_metrics (metric_name, metric_value, updated_at)
    VALUES (p_metric_name, p_increment, CURRENT_TIMESTAMP)
    ON CONFLICT (metric_name) 
    DO UPDATE SET 
        metric_value = metric_value + p_increment,
        updated_at = CURRENT_TIMESTAMP;
END;
$$;