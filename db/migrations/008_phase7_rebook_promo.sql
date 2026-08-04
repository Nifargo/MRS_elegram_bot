-- Фаза 7, п.3: "Маємо вікно завтра" - явне "Скасувати нагадування" глушить
-- промо для конкретного простроченого візиту (altegio_record_id), доки клієнт
-- не запишеться знову (тоді "останній візит" зміниться і 6-тижневий відлік
-- стартує заново). Виконати в Supabase SQL Editor після schema.sql і
-- попередніх міграцій.

alter table clients add column if not exists rebook_promo_dismissed_record_id bigint;
