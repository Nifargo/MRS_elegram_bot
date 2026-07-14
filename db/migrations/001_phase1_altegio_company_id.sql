-- Фаза 1: запам'ятовуємо, в якій філії (company_id) знайдено/створено картку клієнта в Altegio,
-- щоб синхронізувати туди дані улюбленців (коментар клієнта).
-- Виконати в Supabase SQL Editor, якщо схема вже була створена до Фази 1.

alter table clients add column if not exists altegio_company_id text;