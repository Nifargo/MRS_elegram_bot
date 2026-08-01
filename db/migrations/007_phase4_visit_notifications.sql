-- Фаза 4: нагадування перед візитом (reminder_2h) і подяка після візиту
-- (thanks_rating). Точний час рахується від starts_at + тривалості запису
-- (seance_length з Altegio), без окремого поллінгу статусу відвідування.
-- Виконати в Supabase SQL Editor після schema.sql і попередніх міграцій.

alter table tracked_records add column if not exists ends_at timestamptz;

-- Прив'язка сповіщення до конкретного запису — на відміну від form_incomplete/
-- vaccine (де досить client_id), тут у клієнта може бути кілька активних
-- записів одночасно, і треба точково скасувати/перепланувати саме одне.
alter table notifications
    add column if not exists altegio_record_id bigint
        references tracked_records (altegio_record_id) on delete cascade;

create index if not exists idx_notifications_altegio_record_id
    on notifications (altegio_record_id);
