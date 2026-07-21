-- Фаза 3: перенос/скасування записів потребують company_id і service_id
-- кожного запису, щоб звертатись до Altegio (move_record/cancel_record).
-- Виконати в Supabase SQL Editor після schema.sql і 001_*.sql.

alter table tracked_records
    add column if not exists company_id text,
    add column if not exists altegio_service_id bigint;
