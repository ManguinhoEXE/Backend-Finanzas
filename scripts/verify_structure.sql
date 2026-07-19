-- ============================================
-- SCRIPT DE VERIFICACIÓN DE ESTRUCTURA
-- Proyecto: Finanzas - Gestor de Gastos Personales
-- ============================================
-- Este script muestra la estructura completa de la base de datos.
-- Ejecutar en el SQL Editor de Supabase para verificar.
-- ============================================

-- ============================================
-- 1. TABLA DE USUARIOS
-- ============================================
SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'authentication_user'
ORDER BY ordinal_position;

-- ============================================
-- 2. TABLA DE LLAVES DE ACCESO
-- ============================================
SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'authentication_accesskey'
ORDER BY ordinal_position;

-- ============================================
-- 3. TABLA DE GASTOS
-- ============================================
SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'expenses_expense'
ORDER BY ordinal_position;

-- ============================================
-- 4. RELACIONES (FOREIGN KEYS)
-- ============================================
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name IN ('authentication_user', 'authentication_accesskey', 'expenses_expense');

-- ============================================
-- 5. ÍNDICES
-- ============================================
SELECT
    indexname,
    tablename,
    indexdef
FROM pg_indexes
WHERE tablename IN ('authentication_user', 'authentication_accesskey', 'expenses_expense')
    AND indexname NOT LIKE '%_pkey';

-- ============================================
-- 6. CONTEO DE REGISTROS
-- ============================================
SELECT 'authentication_user' AS tabla, COUNT(*) AS total FROM authentication_user
UNION ALL
SELECT 'authentication_accesskey', COUNT(*) FROM authentication_accesskey
UNION ALL
SELECT 'expenses_expense', COUNT(*) FROM expenses_expense;
