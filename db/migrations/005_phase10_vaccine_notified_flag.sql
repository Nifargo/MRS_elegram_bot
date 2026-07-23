-- Фаза 10: флаг "нагадування про вакцинацію вже надіслано для цієї дати" —
-- захищає від повторного нагадування, поки адмін не впише нову дату вакцинації.
-- Виконати в Supabase SQL Editor після 004_phase10_vaccine_due_date.sql.

alter table clients add column if not exists vaccine_notified_due_date date;
