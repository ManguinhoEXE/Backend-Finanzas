-- ============================================
-- ESTRUCTURA FINAL DE LA BASE DE DATOS
-- Proyecto: Finanzas - Gestor de Gastos Personales
-- Motor: PostgreSQL (Supabase)
-- ============================================
-- Este script documenta la estructura completa
-- de todas las tablas del proyecto.
-- ============================================

-- ============================================
-- TABLA: authentication_user
-- DESCRIPCIÓN: Almacena los usuarios de la aplicación
-- ============================================
CREATE TABLE IF NOT EXISTS authentication_user (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE NULL,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Comentario de la tabla
COMMENT ON TABLE authentication_user IS 'Tabla de usuarios de la aplicación';

-- Comentarios de las columnas
COMMENT ON COLUMN authentication_user.id IS 'Identificador único del usuario';
COMMENT ON COLUMN authentication_user.password IS 'Contraseña hasheada (requerida por Django)';
COMMENT ON COLUMN authentication_user.last_login IS 'Última fecha y hora de acceso';
COMMENT ON COLUMN authentication_user.name IS 'Nombre completo del usuario';
COMMENT ON COLUMN authentication_user.created_at IS 'Fecha y hora de creación del registro';

-- ============================================
-- TABLA: authentication_accesskey
-- DESCRIPCIÓN: Almacena las llaves de acceso únicas
-- ============================================
CREATE TABLE IF NOT EXISTS authentication_accesskey (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(255) NOT NULL UNIQUE,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Comentario de la tabla
COMMENT ON TABLE authentication_accesskey IS 'Tabla de llaves de acceso únicas';

-- Comentarios de las columnas
COMMENT ON COLUMN authentication_accesskey.id IS 'Identificador único de la llave';
COMMENT ON COLUMN authentication_accesskey.key IS 'Llave de acceso única';
COMMENT ON COLUMN authentication_accesskey.used IS 'Indica si la llave fue utilizada';
COMMENT ON COLUMN authentication_accesskey.used_at IS 'Fecha y hora en que se utilizó la llave';
COMMENT ON COLUMN authentication_accesskey.created_at IS 'Fecha y hora de creación del registro';

-- ============================================
-- TABLA: expenses_expense
-- DESCRIPCIÓN: Almacena los gastos personales
-- ============================================
CREATE TABLE IF NOT EXISTS expenses_expense (
    id BIGSERIAL PRIMARY KEY,
    usuario_id BIGINT NOT NULL REFERENCES authentication_user(id) ON DELETE CASCADE,
    categoria VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    valor DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Comentario de la tabla
COMMENT ON TABLE expenses_expense IS 'Tabla de gastos personales';

-- Comentarios de las columnas
COMMENT ON COLUMN expenses_expense.id IS 'Identificador único del gasto';
COMMENT ON COLUMN expenses_expense.usuario_id IS 'Referencia al usuario dueño del gasto';
COMMENT ON COLUMN expenses_expense.categoria IS 'Categoría del gasto';
COMMENT ON COLUMN expenses_expense.fecha IS 'Fecha en que se realizó el gasto';
COMMENT ON COLUMN expenses_expense.descripcion IS 'Descripción o detalle del gasto';
COMMENT ON COLUMN expenses_expense.valor IS 'Valor monetario del gasto';
COMMENT ON COLUMN expenses_expense.created_at IS 'Fecha y hora de creación del registro';

-- ============================================
-- ÍNDICES PARA MEJORAR EL RENDIMIENTO
-- ============================================

-- Índice para buscar gastos por usuario rápidamente
CREATE INDEX IF NOT EXISTS idx_expense_usuario ON expenses_expense(usuario_id);

-- Índice para buscar gastos por fecha
CREATE INDEX IF NOT EXISTS idx_expense_fecha ON expenses_expense(fecha);

-- Índice para buscar gastos por categoría
CREATE INDEX IF NOT EXISTS idx_expense_categoria ON expenses_expense(categoria);

-- Índice para buscar llaves por key rápidamente
CREATE INDEX IF NOT EXISTS idx_accesskey_key ON authentication_accesskey(key);

-- ============================================
-- VERIFICACIÓN FINAL
-- ============================================
-- Ejecutar esta consulta para ver el resumen:
-- SELECT
--     'authentication_user' AS tabla,
--     COUNT(*) AS registros
-- FROM authentication_user
-- UNION ALL
-- SELECT
--     'authentication_accesskey',
--     COUNT(*)
-- FROM authentication_accesskey
-- UNION ALL
-- SELECT
--     'expenses_expense',
--     COUNT(*)
-- FROM expenses_expense;
