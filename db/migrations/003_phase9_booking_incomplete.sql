-- Клієнт почав флоу запису («📅 Записатись»), але не завершив його того ж дня —
-- о 18:00 (Київ) адмінам летить сповіщення з іменем і телефоном клієнта, щоб передзвонити.
-- Виконати в Supabase SQL Editor після schema.sql і попередніх міграцій.

alter table notifications drop constraint if exists notifications_type_check;

alter table notifications add constraint notifications_type_check check (
    type in ('reminder_2h', 'thanks_rating', 'rebook_nudge', 'birthday', 'vaccine', 'form_incomplete', 'booking_incomplete', 'custom')
);