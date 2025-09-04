CREATE TABLE public.users (
	id int8 NOT NULL,
	username text NULL,
	first_name text NULL,
	last_name text NULL,
	CONSTRAINT users_pkey PRIMARY KEY (id)
);

CREATE TABLE public.messages (
	id serial4 NOT NULL,
	user_id int8 NOT NULL,
	"role" text NOT NULL,
	"text" text NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT messages_pkey PRIMARY KEY (id),
	CONSTRAINT messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);
CREATE INDEX idx_messages_user_id_created_at ON public.messages USING btree (user_id, created_at DESC);