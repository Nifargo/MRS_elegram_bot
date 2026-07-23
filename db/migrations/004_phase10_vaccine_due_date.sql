-- Фаза 10: дата закінчення дії вакцинації, синхронізована з коментаря клієнта Altegio
-- (адмін вручну пише дату в коментар картки клієнта — див. services/vaccine_sync.py).
-- Виконати в Supabase SQL Editor після schema.sql і попередніх міграцій.

alter table clients add column if not exists vaccine_due_date date;

-- Позначка останнього запуску щоденних (не 10-хвилинних) cron-задач: диспетчер
-- виконує їх раз на добу, при першому виклику /cron після заданої години.
create table if not exists cron_state (
    key            text primary key,
    last_run_date  date
);

alter table cron_state enable row level security;
