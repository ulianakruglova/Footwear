--
-- PostgreSQL database dump
--

\restrict WbyesiQNqhqOdRhcvNR0B02WcKsKSObSt6a1GLSfkNgecCTSr2z7CfxLWy6nlB8

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    category_id integer NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- Name: categories_category_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_category_id_seq OWNER TO postgres;

--
-- Name: categories_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_category_id_seq OWNED BY public.categories.category_id;


--
-- Name: manufacturers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.manufacturers (
    manufacturer_id integer NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.manufacturers OWNER TO postgres;

--
-- Name: manufacturers_manufacturer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.manufacturers_manufacturer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.manufacturers_manufacturer_id_seq OWNER TO postgres;

--
-- Name: manufacturers_manufacturer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.manufacturers_manufacturer_id_seq OWNED BY public.manufacturers.manufacturer_id;


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_items (
    order_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL,
    CONSTRAINT order_items_quantity_check CHECK ((quantity > 0))
);


ALTER TABLE public.order_items OWNER TO postgres;

--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    order_id integer NOT NULL,
    order_date date NOT NULL,
    delivery_date date,
    pickup_code character varying(20) NOT NULL,
    status character varying(50) NOT NULL,
    user_id integer NOT NULL,
    pickup_point_id integer NOT NULL,
    CONSTRAINT orders_status_check CHECK (((status)::text = ANY ((ARRAY['Новый'::character varying, 'В обработке'::character varying, 'Доставлен'::character varying, 'Завершен'::character varying])::text[])))
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- Name: orders_order_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orders_order_id_seq OWNER TO postgres;

--
-- Name: orders_order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_order_id_seq OWNED BY public.orders.order_id;


--
-- Name: pickup_points; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pickup_points (
    point_id integer NOT NULL,
    address text NOT NULL
);


ALTER TABLE public.pickup_points OWNER TO postgres;

--
-- Name: pickup_points_point_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pickup_points_point_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pickup_points_point_id_seq OWNER TO postgres;

--
-- Name: pickup_points_point_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pickup_points_point_id_seq OWNED BY public.pickup_points.point_id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    product_id integer NOT NULL,
    article character varying(20) NOT NULL,
    name character varying(255) NOT NULL,
    unit character varying(20) DEFAULT 'шт.'::character varying,
    price numeric(10,2) NOT NULL,
    stock_quantity integer DEFAULT 0,
    discount integer DEFAULT 0,
    description text,
    photo character varying(255),
    category_id integer,
    manufacturer_id integer,
    supplier_id integer
);


ALTER TABLE public.products OWNER TO postgres;

--
-- Name: products_product_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_product_id_seq OWNER TO postgres;

--
-- Name: products_product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_product_id_seq OWNED BY public.products.product_id;


--
-- Name: suppliers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.suppliers (
    supplier_id integer NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.suppliers OWNER TO postgres;

--
-- Name: suppliers_supplier_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.suppliers_supplier_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.suppliers_supplier_id_seq OWNER TO postgres;

--
-- Name: suppliers_supplier_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.suppliers_supplier_id_seq OWNED BY public.suppliers.supplier_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    full_name character varying(255) NOT NULL,
    login character varying(255) NOT NULL,
    password character varying(255) NOT NULL,
    role character varying(50) NOT NULL,
    CONSTRAINT users_role_check CHECK (((role)::text = ANY ((ARRAY['Администратор'::character varying, 'Менеджер'::character varying, 'Авторизированный клиент'::character varying])::text[])))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: categories category_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN category_id SET DEFAULT nextval('public.categories_category_id_seq'::regclass);


--
-- Name: manufacturers manufacturer_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manufacturers ALTER COLUMN manufacturer_id SET DEFAULT nextval('public.manufacturers_manufacturer_id_seq'::regclass);


--
-- Name: orders order_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders ALTER COLUMN order_id SET DEFAULT nextval('public.orders_order_id_seq'::regclass);


--
-- Name: pickup_points point_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pickup_points ALTER COLUMN point_id SET DEFAULT nextval('public.pickup_points_point_id_seq'::regclass);


--
-- Name: products product_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN product_id SET DEFAULT nextval('public.products_product_id_seq'::regclass);


--
-- Name: suppliers supplier_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers ALTER COLUMN supplier_id SET DEFAULT nextval('public.suppliers_supplier_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categories (category_id, name) FROM stdin;
1	Женская обувь
2	Мужская обувь
\.


--
-- Data for Name: manufacturers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.manufacturers (manufacturer_id, name) FROM stdin;
1	Kari
2	Marco Tozzi
3	Рос
4	Rieker
5	Alessio Nesca
6	CROSBY
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_items (order_id, product_id, quantity) FROM stdin;
1	1	2
1	2	2
2	3	1
2	4	1
3	5	10
3	6	10
4	7	5
4	8	4
5	1	2
5	2	2
6	3	1
6	4	1
7	5	10
7	6	10
8	7	5
8	8	4
9	9	5
9	10	1
10	11	5
10	12	5
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (order_id, order_date, delivery_date, pickup_code, status, user_id, pickup_point_id) FROM stdin;
1	2025-02-27	2025-04-20	901	Завершен	4	1
2	2022-09-28	2025-04-21	902	Завершен	1	2
3	2025-03-21	2025-04-22	903	Завершен	2	3
4	2025-02-20	2025-04-23	904	Завершен	3	2
5	2025-03-17	2025-04-24	905	Завершен	4	3
6	2025-03-01	2025-04-25	906	Завершен	1	15
7	2025-02-28	2025-04-26	907	Завершен	2	4
8	2025-03-31	2025-04-27	908	Новый	3	19
9	2025-04-02	2025-04-28	909	Новый	4	1
10	2025-04-03	2025-04-29	910	Новый	4	19
\.


--
-- Data for Name: pickup_points; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pickup_points (point_id, address) FROM stdin;
1	420151, г. Лесной, ул. Вишневая, 32
2	125061, г. Лесной, ул. Подгорная, 8
3	630370, г. Лесной, ул. Шоссейная, 24
4	400562, г. Лесной, ул. Зеленая, 32
5	614510, г. Лесной, ул. Маяковского, 47
6	410542, г. Лесной, ул. Светлая, 46
7	620839, г. Лесной, ул. Цветочная, 8
8	443890, г. Лесной, ул. Коммунистическая, 1
9	603379, г. Лесной, ул. Спортивная, 46
10	603721, г. Лесной, ул. Гоголя, 41
11	410172, г. Лесной, ул. Северная, 13
12	614611, г. Лесной, ул. Молодежная, 50
13	454311, г.Лесной, ул. Новая, 19
14	660007, г.Лесной, ул. Октябрьская, 19
15	603036, г. Лесной, ул. Садовая, 4
16	394060, г.Лесной, ул. Фрунзе, 43
17	410661, г. Лесной, ул. Школьная, 50
18	625590, г. Лесной, ул. Коммунистическая, 20
19	625683, г. Лесной, ул. 8 Марта
20	450983, г.Лесной, ул. Комсомольская, 26
21	394782, г. Лесной, ул. Чехова, 3
22	603002, г. Лесной, ул. Дзержинского, 28
23	450558, г. Лесной, ул. Набережная, 30
24	344288, г. Лесной, ул. Чехова, 1
25	614164, г.Лесной,  ул. Степная, 30
26	394242, г. Лесной, ул. Коммунистическая, 43
27	660540, г. Лесной, ул. Солнечная, 25
28	125837, г. Лесной, ул. Шоссейная, 40
29	125703, г. Лесной, ул. Партизанская, 49
30	625283, г. Лесной, ул. Победы, 46
31	614753, г. Лесной, ул. Полевая, 35
32	426030, г. Лесной, ул. Маяковского, 44
33	450375, г. Лесной ул. Клубная, 44
34	625560, г. Лесной, ул. Некрасова, 12
35	630201, г. Лесной, ул. Комсомольская, 17
36	190949, г. Лесной, ул. Мичурина, 26
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (product_id, article, name, unit, price, stock_quantity, discount, description, photo, category_id, manufacturer_id, supplier_id) FROM stdin;
1	А112Т4	Ботинки	шт.	4990.00	6	3	Женские Ботинки демисезонные kari	1.jpg	1	1	1
2	F635R4	Ботинки	шт.	3244.00	13	2	Ботинки Marco Tozzi женские демисезонные, размер 39, цвет бежевый	2.jpg	1	2	2
3	H782T5	Туфли	шт.	4499.00	5	4	Туфли kari мужские классика MYZ21AW-450A, размер 43, цвет: черный	3.jpg	2	1	1
4	G783F5	Ботинки	шт.	5900.00	8	2	Мужские ботинки Рос-Обувь кожаные с натуральным мехом	4.jpg	2	3	1
5	J384T6	Ботинки	шт.	3800.00	16	2	B3430/14 Полуботинки мужские Rieker	5.jpg	2	4	2
6	D572U8	Кроссовки	шт.	4100.00	6	3	129615-4 Кроссовки мужские	6.jpg	2	3	2
7	F572H7	Туфли	шт.	2700.00	14	2	Туфли Marco Tozzi женские летние, размер 39, цвет черный	7.jpg	1	2	1
8	D329H3	Полуботинки	шт.	1890.00	4	4	Полуботинки Alessio Nesca женские 3-30797-47, размер 37, цвет: бордовый	8.jpg	1	5	2
9	B320R5	Туфли	шт.	4300.00	6	2	Туфли Rieker женские демисезонные, размер 41, цвет коричневый	9.jpg	1	4	1
10	G432E4	Туфли	шт.	2800.00	15	3	Туфли kari женские TR-YR-413017, размер 37, цвет: черный	10.jpg	1	1	1
11	S213E3	Полуботинки	шт.	2156.00	6	3	407700/01-01 Полуботинки мужские CROSBY	\N	2	6	2
12	E482R4	Полуботинки	шт.	1800.00	14	2	Полуботинки kari женские MYZ20S-149, размер 41, цвет: черный	\N	1	1	1
13	S634B5	Кеды	шт.	5500.00	0	3	Кеды Caprice мужские демисезонные, размер 42, цвет черный	\N	2	6	2
14	K345R4	Полуботинки	шт.	2100.00	3	2	407700/01-02 Полуботинки мужские CROSBY	\N	2	6	2
15	O754F4	Туфли	шт.	5400.00	18	4	Туфли женские демисезонные Rieker артикул 55073-68/37	\N	1	4	2
16	G531F4	Ботинки	шт.	6600.00	9	12	Ботинки женские зимние ROMER арт. 893167-01 Черный	\N	1	1	1
17	J542F5	Тапочки	шт.	500.00	0	13	Тапочки мужские Арт.70701-55-67син р.41	\N	2	1	1
18	B431R5	Ботинки	шт.	2700.00	5	2	Мужские кожаные ботинки/мужские ботинки	\N	2	4	2
19	P764G4	Туфли	шт.	6800.00	15	15	Туфли женские, ARGO, размер 38	\N	1	6	1
20	C436G5	Ботинки	шт.	10200.00	9	15	Ботинки женские, ARGO, размер 40	\N	1	5	1
21	F427R5	Ботинки	шт.	11800.00	11	15	Ботинки на молнии с декоративной пряжкой FRAU	\N	1	4	2
22	N457T5	Полуботинки	шт.	4600.00	13	3	Полуботинки Ботинки черные зимние, мех	\N	1	6	1
23	D364R4	Туфли	шт.	12400.00	5	16	Туфли Luiza Belly женские Kate-lazo черные из натуральной замши	\N	1	1	1
24	S326R5	Тапочки	шт.	9900.00	15	17	Мужские кожаные тапочки "Профиль С.Дали"	\N	2	6	2
25	L754R4	Полуботинки	шт.	1700.00	7	2	Полуботинки kari женские WB2020SS-26, размер 38, цвет: черный	\N	1	1	1
26	M542T5	Кроссовки	шт.	2800.00	3	18	Кроссовки мужские TOFA	\N	2	4	2
27	D268G5	Туфли	шт.	4399.00	12	3	Туфли Rieker женские демисезонные, размер 36, цвет коричневый	\N	1	4	2
28	T324F5	Сапоги	шт.	4699.00	5	2	Сапоги замша Цвет: синий	\N	1	6	1
29	K358H6	Тапочки	шт.	599.00	2	20	Тапочки мужские син р.41	\N	2	4	1
30	H535R5	Ботинки	шт.	2300.00	7	2	Женские Ботинки демисезонные	\N	1	4	2
\.


--
-- Data for Name: suppliers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.suppliers (supplier_id, name) FROM stdin;
1	Kari
2	Обувь для вас
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (user_id, full_name, login, password, role) FROM stdin;
1	Никифорова Весения Николаевна	94d5ous@gmail.com	uzWC67	Администратор
2	Сазонов Руслан Германович	uth4iz@mail.com	2L6KZG	Администратор
3	Одинцов Серафим Артёмович	yzls62@outlook.com	JlFRCZ	Администратор
4	Степанов Михаил Артёмович	1diph5e@tutanota.com	8ntwUp	Менеджер
5	Ворсин Петр Евгеньевич	tjde7c@yahoo.com	YOyhfR	Менеджер
6	Старикова Елена Павловна	wpmrc3do@tutanota.com	RSbvHv	Менеджер
7	Михайлюк Анна Вячеславовна	5d4zbu@tutanota.com	rwVDh9	Авторизированный клиент
8	Ситдикова Елена Анатольевна	ptec8ym@yahoo.com	LdNyos	Авторизированный клиент
9	Ворсин Петр Евгеньевич	1qz4kw@mail.com	gynQMT	Авторизированный клиент
10	Старикова Елена Павловна	4np6se@mail.com	AtnDjr	Авторизированный клиент
\.


--
-- Name: categories_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_category_id_seq', 2, true);


--
-- Name: manufacturers_manufacturer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.manufacturers_manufacturer_id_seq', 6, true);


--
-- Name: orders_order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.orders_order_id_seq', 10, true);


--
-- Name: pickup_points_point_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pickup_points_point_id_seq', 36, true);


--
-- Name: products_product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_product_id_seq', 30, true);


--
-- Name: suppliers_supplier_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.suppliers_supplier_id_seq', 2, true);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_user_id_seq', 10, true);


--
-- Name: categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);


--
-- Name: manufacturers manufacturers_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manufacturers
    ADD CONSTRAINT manufacturers_name_key UNIQUE (name);


--
-- Name: manufacturers manufacturers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manufacturers
    ADD CONSTRAINT manufacturers_pkey PRIMARY KEY (manufacturer_id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (order_id, product_id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (order_id);


--
-- Name: pickup_points pickup_points_address_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pickup_points
    ADD CONSTRAINT pickup_points_address_key UNIQUE (address);


--
-- Name: pickup_points pickup_points_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pickup_points
    ADD CONSTRAINT pickup_points_pkey PRIMARY KEY (point_id);


--
-- Name: products products_article_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_article_key UNIQUE (article);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);


--
-- Name: suppliers suppliers_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_name_key UNIQUE (name);


--
-- Name: suppliers suppliers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_pkey PRIMARY KEY (supplier_id);


--
-- Name: users users_login_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_login_key UNIQUE (login);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON DELETE CASCADE;


--
-- Name: order_items order_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id) ON DELETE CASCADE;


--
-- Name: orders orders_pickup_point_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pickup_point_id_fkey FOREIGN KEY (pickup_point_id) REFERENCES public.pickup_points(point_id) ON DELETE CASCADE;


--
-- Name: orders orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id) ON DELETE SET NULL;


--
-- Name: products products_manufacturer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_manufacturer_id_fkey FOREIGN KEY (manufacturer_id) REFERENCES public.manufacturers(manufacturer_id) ON DELETE SET NULL;


--
-- Name: products products_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(supplier_id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict WbyesiQNqhqOdRhcvNR0B02WcKsKSObSt6a1GLSfkNgecCTSr2z7CfxLWy6nlB8

