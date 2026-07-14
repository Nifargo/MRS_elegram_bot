-- Mr.Snoopy Grooming Bot — Supabase schema
-- Виконати повністю в Supabase SQL Editor (Project → SQL Editor → New query).
-- Зберігає лише те, чого немає в Altegio (записи/послуги/ціни/бонуси лишаються там).

create table if not exists clients (
    id                bigint generated always as identity primary key,
    tg_user_id         bigint not null unique,
    altegio_client_id  bigint,
    phone              text,
    name               text,
    registration_done  boolean not null default false,
    draft_json         jsonb,
    last_promo_at      timestamptz,
    created_at         timestamptz not null default now()
);

create table if not exists pets (
    id                     bigint generated always as identity primary key,
    client_id              bigint not null references clients (id) on delete cascade,
    altegio_pet_id         bigint,
    name                   text not null,
    breed                  text,
    birth_date             date,
    weight                 numeric,
    allergies              text,
    behavior_notes         text,
    photo_file_id          text,
    rabies_vaccine_date    date,
    vaccine_photo_file_ids jsonb not null default '[]'::jsonb,
    created_at             timestamptz not null default now()
);

create table if not exists tracked_records (
    id                bigint generated always as identity primary key,
    altegio_record_id bigint not null unique,
    client_id          bigint references clients (id) on delete set null,
    pet_id             bigint references pets (id) on delete set null,
    starts_at          timestamptz not null,
    service_title      text,
    location_title     text,
    status             text not null default 'active',
    raw_json           jsonb,
    created_at         timestamptz not null default now(),
    updated_at         timestamptz not null default now()
);

create table if not exists visit_extras (
    id                       bigint generated always as identity primary key,
    altegio_record_id        bigint not null unique references tracked_records (altegio_record_id) on delete cascade,
    groomer_recommendations  text,
    next_visit_weeks         int,
    photo_before_ids         jsonb not null default '[]'::jsonb,
    photo_after_ids          jsonb not null default '[]'::jsonb,
    created_at               timestamptz not null default now()
);

create table if not exists ratings (
    id                bigint generated always as identity primary key,
    altegio_record_id bigint not null references tracked_records (altegio_record_id) on delete cascade,
    service_stars      smallint check (service_stars between 1 and 5),
    groomer_stars       smallint check (groomer_stars between 1 and 5),
    comment            text,
    created_at         timestamptz not null default now()
);

create table if not exists notifications (
    id           bigint generated always as identity primary key,
    client_id    bigint not null references clients (id) on delete cascade,
    type         text not null check (
        type in ('reminder_2h', 'thanks_rating', 'rebook_nudge', 'birthday', 'vaccine', 'form_incomplete', 'custom')
    ),
    payload_json jsonb,
    send_after   timestamptz not null,
    status       text not null default 'pending' check (status in ('pending', 'sent', 'failed')),
    sent_at      timestamptz,
    created_at   timestamptz not null default now()
);

create table if not exists chat_messages (
    id         bigint generated always as identity primary key,
    client_id  bigint not null references clients (id) on delete cascade,
    role       text not null check (role in ('user', 'assistant', 'system')),
    content    text not null,
    created_at timestamptz not null default now()
);

-- Індекси під найчастіші запити (cron-диспетчер, пошук клієнта, історія улюбленця)
create index if not exists idx_pets_client_id on pets (client_id);
create index if not exists idx_tracked_records_client_id on tracked_records (client_id);
create index if not exists idx_tracked_records_starts_at on tracked_records (starts_at);
create index if not exists idx_notifications_due on notifications (status, send_after);
create index if not exists idx_chat_messages_client_id on chat_messages (client_id, created_at);

-- RLS вмикаємо на всіх таблицях і НЕ додаємо policy для anon/authenticated —
-- це закриває публічний REST API повністю. Наш бекенд ходить через
-- service_role key, який завжди обходить RLS, тож для нього нічого не зміниться.
alter table clients enable row level security;
alter table pets enable row level security;
alter table tracked_records enable row level security;
alter table visit_extras enable row level security;
alter table ratings enable row level security;
alter table notifications enable row level security;
alter table chat_messages enable row level security;