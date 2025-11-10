--
-- PostgreSQL database dump
--

\set VERBOSITY terse

-- Dumped from database version 14.19 (Homebrew)
-- Dumped by pg_dump version 14.19 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: globalroletype; Type: TYPE; Schema: public; Owner: dev
--

CREATE TYPE public.globalroletype AS ENUM (
    'CLIENT',
    'WORKER'
);


ALTER TYPE public.globalroletype OWNER TO dev;

--
-- Name: listroletype; Type: TYPE; Schema: public; Owner: dev
--

CREATE TYPE public.listroletype AS ENUM (
    'CREATOR',
    'USER'
);


ALTER TYPE public.listroletype OWNER TO dev;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: users; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.users (
    id integer NOT NULL,
    external_id character varying NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);

ALTER TABLE public.users OWNER TO dev;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: dev
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE public.users_id_seq OWNER TO dev;

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;

--
-- Name: global_roles; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.global_roles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    role_type public.globalroletype NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.global_roles OWNER TO dev;

--
-- Name: global_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: dev
--

CREATE SEQUENCE public.global_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.global_roles_id_seq OWNER TO dev;

--
-- Name: global_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev
--

ALTER SEQUENCE public.global_roles_id_seq OWNED BY public.global_roles.id;


--
-- Name: items; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.items (
    id integer NOT NULL,
    name character varying NOT NULL,
    description character varying,
    category character varying,
    quantity integer,
    price double precision,
    list_id integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.items OWNER TO dev;

--
-- Name: items_id_seq; Type: SEQUENCE; Schema: public; Owner: dev
--

CREATE SEQUENCE public.items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.items_id_seq OWNER TO dev;

--
-- Name: items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev
--

ALTER SEQUENCE public.items_id_seq OWNED BY public.items.id;


--
-- Name: list_users; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.list_users (
    id integer NOT NULL,
    user_id integer NOT NULL,
    list_id integer NOT NULL,
    role_type public.listroletype NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.list_users OWNER TO dev;

--
-- Name: list_users_id_seq; Type: SEQUENCE; Schema: public; Owner: dev
--

CREATE SEQUENCE public.list_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.list_users_id_seq OWNER TO dev;

--
-- Name: list_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev
--

ALTER SEQUENCE public.list_users_id_seq OWNED BY public.list_users.id;


--
-- Name: lists; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.lists (
    id integer NOT NULL,
    name character varying NOT NULL,
    description character varying,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.lists OWNER TO dev;

--
-- Name: lists_id_seq; Type: SEQUENCE; Schema: public; Owner: dev
--

CREATE SEQUENCE public.lists_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lists_id_seq OWNER TO dev;

--
-- Name: lists_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev
--

ALTER SEQUENCE public.lists_id_seq OWNED BY public.lists.id;


--
-- Name: locks; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.locks (
    id integer NOT NULL,
    list_id integer NOT NULL,
    holder_id integer NOT NULL,
    acquired_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.locks OWNER TO dev;

--
-- Name: locks_id_seq; Type: SEQUENCE; Schema: public; Owner: dev
--

CREATE SEQUENCE public.locks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.locks_id_seq OWNER TO dev;

--
-- Name: locks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev
--

ALTER SEQUENCE public.locks_id_seq OWNED BY public.locks.id;

--
-- Name: list_roles; Type: TABLE; Schema: public; Owner: dev
--

CREATE TABLE public.list_roles (
    id integer NOT NULL,
    role_type public.listroletype NOT NULL,
    description character varying,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.list_roles OWNER TO dev;

--
-- Name: list_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: dev
--

CREATE SEQUENCE public.list_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.list_roles_id_seq OWNER TO dev;

--
-- Name: list_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev
--

ALTER SEQUENCE public.list_roles_id_seq OWNED BY public.list_roles.id;

--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);

--
-- Name: global_roles id; Type: DEFAULT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.global_roles ALTER COLUMN id SET DEFAULT nextval('public.global_roles_id_seq'::regclass);


--
-- Name: items id; Type: DEFAULT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.items ALTER COLUMN id SET DEFAULT nextval('public.items_id_seq'::regclass);


--
-- Name: list_users id; Type: DEFAULT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.list_users ALTER COLUMN id SET DEFAULT nextval('public.list_users_id_seq'::regclass);


--
-- Name: lists id; Type: DEFAULT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.lists ALTER COLUMN id SET DEFAULT nextval('public.lists_id_seq'::regclass);


--
-- Name: locks id; Type: DEFAULT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.locks ALTER COLUMN id SET DEFAULT nextval('public.locks_id_seq'::regclass);

--
-- Name: list_roles id; Type: DEFAULT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.list_roles ALTER COLUMN id SET DEFAULT nextval('public.list_roles_id_seq'::regclass);

--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

--
-- Name: users users_external_id_key; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_external_id_key UNIQUE (external_id);

--
-- Name: global_roles global_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.global_roles
    ADD CONSTRAINT global_roles_pkey PRIMARY KEY (id);

--
-- Name: global_roles global_roles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.global_roles
    ADD CONSTRAINT global_roles_user_id_key UNIQUE (user_id);

--
-- Name: items items_pkey; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (id);


--
-- Name: list_users list_users_pkey; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.list_users
    ADD CONSTRAINT list_users_pkey PRIMARY KEY (id);


--
-- Name: lists lists_pkey; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.lists
    ADD CONSTRAINT lists_pkey PRIMARY KEY (id);


--
-- Name: locks locks_list_id_key; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.locks
    ADD CONSTRAINT locks_list_id_key UNIQUE (list_id);


--
-- Name: locks locks_pkey; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.locks
    ADD CONSTRAINT locks_pkey PRIMARY KEY (id);


--
-- Name: list_users unique_user_list; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.list_users
    ADD CONSTRAINT unique_user_list UNIQUE (user_id, list_id);

--
-- Name: list_roles list_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.list_roles
    ADD CONSTRAINT list_roles_pkey PRIMARY KEY (id);

--
-- Name: list_roles list_roles_role_type_key; Type: CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.list_roles
    ADD CONSTRAINT list_roles_role_type_key UNIQUE (role_type);

--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: dev
--

CREATE INDEX ix_users_id ON public.users USING btree (id);

--
-- Name: ix_users_external_id; Type: INDEX; Schema: public; Owner: dev
--

CREATE INDEX ix_users_external_id ON public.users USING btree (external_id);

--
-- Name: ix_list_users_id; Type: INDEX; Schema: public; Owner: dev
--

CREATE INDEX ix_list_users_id ON public.list_users USING btree (id);


--
-- Name: ix_locks_id; Type: INDEX; Schema: public; Owner: dev
--

CREATE INDEX ix_locks_id ON public.locks USING btree (id);

--
-- Name: ix_list_roles_id; Type: INDEX; Schema: public; Owner: dev
--

CREATE INDEX ix_list_roles_id ON public.list_roles USING btree (id);

--
-- Name: global_roles global_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.global_roles
    ADD CONSTRAINT global_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);

--
-- Name: items items_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_list_id_fkey FOREIGN KEY (list_id) REFERENCES public.lists(id);


--
-- Name: list_users list_users_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.list_users
    ADD CONSTRAINT list_users_list_id_fkey FOREIGN KEY (list_id) REFERENCES public.lists(id);


--
-- Name: list_users list_users_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.list_users
    ADD CONSTRAINT list_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: locks locks_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.locks
    ADD CONSTRAINT locks_list_id_fkey FOREIGN KEY (list_id) REFERENCES public.lists(id);


--
-- Name: locks locks_holder_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev
--

ALTER TABLE ONLY public.locks
    ADD CONSTRAINT locks_holder_id_fkey FOREIGN KEY (holder_id) REFERENCES public.users(id);

--
-- Data for Name: list_roles; Type: TABLE DATA; Schema: public; Owner: dev
--

INSERT INTO public.list_roles (role_type, description) VALUES ('CREATOR', 'Creator of a list');
INSERT INTO public.list_roles (role_type, description) VALUES ('USER', 'User of a list');

--
-- PostgreSQL database dump complete
--

\set VERBOSITY default
