-- ============================================
-- RESET COMPLETO DE TABLAS - Supabase
-- Ejecutar en: Supabase Dashboard > SQL Editor
-- ============================================

-- 1. Truncar todas las tablas en orden correcto
TRUNCATE TABLE savings_savinggoalparticipant CASCADE;
TRUNCATE TABLE savings_savingmovement CASCADE;
TRUNCATE TABLE savings_savinggoal CASCADE;
TRUNCATE TABLE expenses_expense CASCADE;
TRUNCATE TABLE authentication_accesskey CASCADE;
TRUNCATE TABLE authentication_user CASCADE;

-- 2. Reinsertar llaves de activacion
INSERT INTO authentication_accesskey (key, used, created_at) VALUES
('FINANZAS-2026-USUARIO-1', false, NOW()),
('FINANZAS-2026-USUARIO-2', false, NOW());

-- 3. Verificar resultado
SELECT 'authentication_user' as tabla, COUNT(*) as registros FROM authentication_user
UNION ALL
SELECT 'authentication_accesskey', COUNT(*) FROM authentication_accesskey
UNION ALL
SELECT 'expenses_expense', COUNT(*) FROM expenses_expense
UNION ALL
SELECT 'savings_savinggoal', COUNT(*) FROM savings_savinggoal
UNION ALL
SELECT 'savings_savingmovement', COUNT(*) FROM savings_savingmovement
UNION ALL
SELECT 'savings_savinggoalparticipant', COUNT(*) FROM savings_savinggoalparticipant;
