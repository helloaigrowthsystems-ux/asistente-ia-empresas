# auth.py
# Gestión de autenticación y planes con Supabase

import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv(override=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# Límites por plan
LIMITES_PLAN = {
    "gratuito": 3,   # usos por día
    "pro":      999, # ilimitado
}

@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ─── Login / Registro ──────────────────────────────────────────────────────────

def mostrar_login():
    """Muestra la pantalla de login/registro y gestiona la sesión."""
    st.markdown("""
        <div style='text-align:center; padding: 2rem 0 1rem'>
            <h1>🤖 Asistente IA para Empresas</h1>
            <p style='color: gray'>Accede o crea tu cuenta gratuita para empezar</p>
        </div>
    """, unsafe_allow_html=True)

    col_izq, col_centro, col_der = st.columns([1, 1.5, 1])
    with col_centro:
        tab_login, tab_registro = st.tabs(["Iniciar sesión", "Crear cuenta"])

        with tab_login:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Contraseña", type="password", key="login_pass")
            if st.button("Entrar", use_container_width=True, type="primary"):
                _hacer_login(email, password)

        with tab_registro:
            email_r = st.text_input("Email", key="reg_email")
            password_r = st.text_input("Contraseña (mín. 6 caracteres)", type="password", key="reg_pass")
            nombre_r = st.text_input("Nombre o empresa", key="reg_nombre")
            if st.button("Crear cuenta gratis", use_container_width=True, type="primary"):
                _hacer_registro(email_r, password_r, nombre_r)

        st.markdown("""
            <div style='text-align:center; margin-top:1rem; font-size:0.8rem; color:gray'>
                Plan gratuito: 3 usos/día · Sin tarjeta de crédito
            </div>
        """, unsafe_allow_html=True)


def _hacer_login(email: str, password: str):
    if not email or not password:
        st.warning("Rellena email y contraseña.")
        return
    try:
        supabase = get_supabase()
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state["usuario"] = res.user
        st.session_state["token"]   = res.session.access_token
        st.rerun()
    except Exception as e:
        st.error(f"Error al iniciar sesión: {e}")


def _hacer_registro(email: str, password: str, nombre: str):
    if not email or not password:
        st.warning("Rellena email y contraseña.")
        return
    if len(password) < 6:
        st.warning("La contraseña debe tener al menos 6 caracteres.")
        return
    try:
        supabase = get_supabase()
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"nombre": nombre}}
        })
        st.success("✅ Cuenta creada. Revisa tu email para confirmar.")
    except Exception as e:
        st.error(f"Error al registrarse: {e}")


def cerrar_sesion():
    try:
        get_supabase().auth.sign_out()
    except Exception:
        pass
    for key in ["usuario", "token"]:
        st.session_state.pop(key, None)
    st.experimental_rerun()


# ─── Control de usos ──────────────────────────────────────────────────────────

def obtener_perfil() -> dict:
    """Devuelve el perfil del usuario desde Supabase."""
    try:
        supabase = get_supabase()
        uid = st.session_state["usuario"].id
        res = supabase.table("usuarios").select("*").eq("id", uid).single().execute()
        return res.data or {}
    except Exception:
        return {}


def puede_usar() -> tuple[bool, str]:
    """
    Comprueba si el usuario puede hacer una acción según su plan y usos del día.
    Devuelve (True/False, mensaje).
    """
    perfil = obtener_perfil()
    if not perfil:
        return False, "No se pudo cargar tu perfil."

    plan = perfil.get("plan", "gratuito")
    limite = LIMITES_PLAN.get(plan, 3)

    if plan == "pro":
        return True, ""

    # Reiniciar contador si es un nuevo día
    hoy = str(date.today())
    usos = perfil.get("usos_hoy", 0)
    if perfil.get("fecha_usos") != hoy:
        usos = 0

    if usos >= limite:
        return False, (
            f"Has alcanzado el límite de {limite} usos diarios del plan gratuito. "
            "Actualiza a Pro para usos ilimitados."
        )
    return True, ""


def registrar_uso():
    """Suma 1 al contador de usos del día."""
    try:
        supabase = get_supabase()
        uid  = st.session_state["usuario"].id
        hoy  = str(date.today())
        perfil = obtener_perfil()

        usos_hoy   = perfil.get("usos_hoy", 0)
        fecha_usos = perfil.get("fecha_usos", "")

        nuevo_usos = (usos_hoy + 1) if fecha_usos == hoy else 1

        supabase.table("usuarios").update({
            "usos_hoy":   nuevo_usos,
            "fecha_usos": hoy,
        }).eq("id", uid).execute()
    except Exception:
        pass


def mostrar_uso_sidebar():
    """Muestra en el sidebar el plan y usos restantes."""
    perfil = obtener_perfil()
    plan   = perfil.get("plan", "gratuito")
    hoy    = str(date.today())
    usos   = perfil.get("usos_hoy", 0) if perfil.get("fecha_usos") == hoy else 0
    limite = LIMITES_PLAN.get(plan, 3)
    nombre = perfil.get("nombre", perfil.get("email", "Usuario"))

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"👤 **{nombre}**")

    if plan == "pro":
        st.sidebar.success("⭐ Plan Pro — usos ilimitados")
    else:
        restantes = max(0, limite - usos)
        color = "green" if restantes > 1 else "orange" if restantes == 1 else "red"
        st.sidebar.markdown(
            f"<span style='color:{color}'>🔢 {restantes}/{limite} usos hoy</span>",
            unsafe_allow_html=True
        )
        if restantes == 0:
            st.sidebar.error("Límite alcanzado")
            st.sidebar.markdown("[⭐ Actualizar a Pro](#)", unsafe_allow_html=True)

    if st.sidebar.button("🚪 Cerrar sesión"):
        cerrar_sesion()