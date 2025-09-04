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

CREATE TABLE public.messages (
    id SERIAL NOT NULL,
    user_id BIGINT NOT NULL,
    role TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT messages_pkey PRIMARY KEY (id),
    CONSTRAINT messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);
CREATE INDEX idx_messages_user_id_created_at ON public.messages USING btree (user_id, created_at DESC);

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