-- ============================================================
-- Ejecuta esto en Supabase → SQL Editor → New query
-- ============================================================

-- Tabla de perfiles de usuario
CREATE TABLE IF NOT EXISTS public.usuarios (
    id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email       TEXT NOT NULL,
    nombre      TEXT,
    plan        TEXT NOT NULL DEFAULT 'gratuito',  -- 'gratuito' | 'pro'
    usos_hoy    INTEGER NOT NULL DEFAULT 0,
    fecha_usos  DATE,
    stripe_customer_id TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seguridad a nivel de fila (cada usuario solo ve su fila)
ALTER TABLE public.usuarios ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuario ve su propio perfil"
    ON public.usuarios FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Usuario actualiza su propio perfil"
    ON public.usuarios FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Usuario inserta su propio perfil"
    ON public.usuarios FOR INSERT
    WITH CHECK (auth.uid() = id);

-- ============================================================
-- OPCIONAL: Ver todos los usuarios desde el dashboard de Supabase
-- (solo para ti como admin, no expuesto al cliente)
-- ============================================================
-- SELECT u.email, u.nombre, u.plan, u.usos_hoy, u.created_at
-- FROM public.usuarios u
-- ORDER BY u.created_at DESC;