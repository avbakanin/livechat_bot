CREATE TABLE public.users (
    id BIGINT NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    gender_preference TEXT DEFAULT 'female',
    subscription_status TEXT DEFAULT 'free',
	consent_given BOOLEAN DEFAULT FALSE,
	subscription_expires_at TIMESTAMP,
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