-- Зберігаємо майстра запису, щоб «Повторити останній запис» пропонував
-- того самого грумера, а не будь-якого вільного.
-- Виконати в Supabase SQL Editor після 002_phase3_tracked_records_slot_fields.sql.

alter table tracked_records add column if not exists staff_id bigint;
