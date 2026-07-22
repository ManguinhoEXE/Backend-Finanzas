-- ============================================
-- SCRIPT DE LLAVES DE ACCESO
-- Proyecto: Finanzas - Gestor de Gastos Personales
-- ============================================
-- Este script crea las dos llaves de acceso únicas
-- para los dos usuarios del sistema.
--
-- INSTRUCCIONES:
-- 1. Copiar este script
-- 2. Pegarlo en el SQL Editor de Supabase
-- 3. Ejecutar el script
-- ============================================

-- Crear las dos llaves de acceso
INSERT INTO authentication_accesskey (key, used, used_at, created_at)
VALUES
    ('FINANZAS-2026-USUARIO-1', FALSE, NULL, NOW()),
    ('FINANZAS-2026-USUARIO-2', FALSE, NULL, NOW());

-- ============================================
-- VERIFICACIÓN
-- ============================================
-- Ejecutar esta consulta para verificar que las llaves se crearon:
-- SELECT * FROM authentication_accesskey;
-- ============================================
