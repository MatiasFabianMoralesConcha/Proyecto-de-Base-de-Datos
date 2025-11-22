#Semana 7:  Proyecto de Bases de datos
#Millaray Olivares - Valentin latu - Martina Vargas - Matias Morales

import streamlit as st
import sqlite3
import pandas as pd
import re
from datetime import datetime



#CONFIGURACIÓN RUTA DE LA BASE#
DB_PATH = "test1.db"  #Ajustar el nombre de la base de datos



#CONFIGURACIÓN LOGIN DEL ADMIN#
ADMIN_USER = "admin"
ADMIN_PASS = "12345"


#Título en grande#
st.set_page_config(page_title="Colegio - Sistema", layout="wide")



#CSS para centrar tablas y encabezados y alinear formularios#
st.markdown(
    """
    <style>
    h1, h2, h3 { text-align: center; }
    [data-testid="stDataFrame"] table th { text-align: center !important; }
    [data-testid="stDataFrame"] table td { text-align: center !important; }
    .css-18e3th9 { align-items: center; }
    </style>
    """,
    unsafe_allow_html=True
)


#CONEXIÓN Y EJECUCIONES#
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def run_query_df(query, params=()):
    conn = get_conn()
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        conn.close()
        if cols:
            return pd.DataFrame(rows, columns=cols)
        return pd.DataFrame()

def run_command(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()



#COLUMNA CONTRASEÑA
def ensure_password_columns():
    conn = get_conn()
    cur = conn.cursor()
    tables = ["alumno", "apoderado", "profesor"]
    for t in tables:
        try:
            cur.execute(f"PRAGMA table_info({t});")
        except Exception:
            continue
        cols = [r[1] for r in cur.fetchall()]
        if "contraseña" not in cols and "password" not in cols:
            cur.execute(f"ALTER TABLE {t} ADD COLUMN contraseña TEXT;")
    conn.commit()
    conn.close()

#Ejecutar 
try:
    ensure_password_columns()
except Exception as e:
    st.warning(f"Advertencia migración: {e}")



# VALIDACIONES Y FORMATOS#
def validate_rut(rut: str) -> bool:
    return bool(re.match(r"^\d{7,8}-[\dkK]$", str(rut).strip()))

def validate_email(email: str) -> bool:
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", str(email).strip()))

def validate_phone(phone: str) -> bool:
    return bool(re.match(r"^\d{8,9}$", str(phone).strip()))

def parse_date_ddmmyyyy_to_yyyy_mm_dd(fecha_ddmmyyyy: str):
    if fecha_ddmmyyyy is None:
        return None
    s = str(fecha_ddmmyyyy).strip()
    if s == "":
        return None
    try:
        d = datetime.strptime(s, "%d/%m/%Y")
        return d.strftime("%Y-%m-%d")
    except Exception:
        return None

def format_date_yyyy_mm_dd_to_ddmmyyyy(fecha_yyyy_mm_dd: str):
    if fecha_yyyy_mm_dd is None or str(fecha_yyyy_mm_dd).strip() == "":
        return ""
    try:
        d = datetime.strptime(str(fecha_yyyy_mm_dd).strip(), "%Y-%m-%d")
        return d.strftime("%d/%m/%Y")
    except Exception:
        return ""


#METADATOS TABLAS (campos y requerimientos)#
TABLES = {
    "apoderado": {
        "pk": "id_apoderado",
        "cols": [
            ("rut", "Rut: 11111111-1"),
            ("nombre", "Nombre"),
            ("apellido", "Apellido"),
            ("correo", "Correo: ejemplo@gmail.com"),
            ("telefono", "Teléfono: 8-9 dígitos"),
            ("fecha_nacimiento", "Fecha de nacimiento (DD/MM/YYYY)"),
            ("contraseña", "Contraseña: Con letras, números y símbolos combinados.")
        ],
        "required": ["rut", "nombre", "apellido", "correo", "telefono", "fecha_nacimiento", "contraseña"]
    },

    "profesor": {
        "pk": "id_profesor",
        "cols": [
            ("rut", "Rut: 11111111-1"),
            ("nombre", "Nombre"),
            ("apellido", "Apellido"),
            ("correo", "Correo: ejemplo@gmail.com"),
            ("telefono", "Teléfono: 8-9 dígitos"),
            ("fecha_nacimiento", "Fecha de nacimiento (DD/MM/YYYY)"),
            ("contraseña", "Contraseña: Con letras, números y símbolos combinados.")
        ],
        "required": ["rut", "nombre", "apellido", "correo", "telefono", "fecha_nacimiento", "contraseña"]
    },

    "curso": {
        "pk": "id_curso",
        "cols": [
            ("nombre", "Nombre del curso"),
            ("id_profesor_jefe", "ID profesor jefe (ej: 1)")
        ],
        "required": ["nombre"]
    },

    "alumno": {
        "pk": "id_alumno",
        "cols": [
            ("rut", "Rut: 11111111-1"),
            ("nombre", "Nombre"),
            ("apellido", "Apellido"),
            ("correo", "Correo: ejemplo@gmail.com"),
            ("fecha_nacimiento", "Fecha de nacimiento (DD/MM/YYYY)"),
            ("id_apoderado", "ID apoderado"),
            ("id_curso", "ID curso"),
            ("contraseña", "Contraseña: Con letras, números y símbolos combinados.")
        ],
        "required": ["rut", "nombre", "apellido", "correo", "fecha_nacimiento", "id_apoderado", "id_curso", "contraseña"]
    },

    "asignatura": {
        "pk": "id_asignatura",
        "cols": [
            ("nombre_asignatura", "Nombre de la asignatura"),
            ("id_profesor_jefe", "ID profesor jefe")
        ],
        "required": ["nombre_asignatura"]
    },

    "nota": {
        "pk": "id_nota",
        "cols": [
            ("id_alumno", "ID alumno"),
            ("id_asignatura", "ID asignatura"),
            ("fecha", "Fecha (DD/MM/YYYY)"),
            ("nota", "Nota (1.0 a 7.0)")
        ],
        "required": ["id_alumno", "id_asignatura", "fecha", "nota"]
    },

    "asistencia": {
        "pk": "id_asistencia",
        "cols": [
            ("id_alumno", "ID alumno"),
            ("fecha", "Fecha (DD/MM/YYYY)"),
            ("presente", "1=Presente / 0=Ausente")
        ],
        "required": ["id_alumno", "fecha", "presente"]
    },

    "comunicacion": {
        "pk": "id_comunicacion",
        "cols": [
            ("id_profesor", "ID profesor"),
            ("id_alumno", "ID alumno"),
            ("fecha", "Fecha (DD/MM/YYYY)"),
            ("mensaje", "Mensaje")
        ],
        "required": ["id_profesor", "id_alumno", "fecha", "mensaje"]
    }
}



#HELPERS CRUD#
def insert_record(table, values):
    vals = values.copy()
    if table == "alumno" and "fecha_nacimiento" in vals:
        vals["fecha_nacimiento"] = parse_date_ddmmyyyy_to_yyyy_mm_dd(vals.get("fecha_nacimiento"))
    if table in ("nota","asistencia","comunicacion") and "fecha" in vals:
        vals["fecha"] = parse_date_ddmmyyyy_to_yyyy_mm_dd(vals.get("fecha"))
    cols = ", ".join(vals.keys())
    placeholders = ", ".join(["?"]*len(vals))
    sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
    run_command(sql, tuple(vals.values()))

def get_record_by_pk(table, pk_value):
    pk = TABLES[table]["pk"]
    return run_query_df(f"SELECT * FROM {table} WHERE {pk} = ?", (pk_value,))

def update_record(table, pk_value, values):
    vals = values.copy()
    if "fecha_nacimiento" in vals:
        vals["fecha_nacimiento"] = parse_date_ddmmyyyy_to_yyyy_mm_dd(vals.get("fecha_nacimiento"))

    if table in ("nota","asistencia","comunicacion") and "fecha" in vals:
        vals["fecha"] = parse_date_ddmmyyyy_to_yyyy_mm_dd(vals.get("fecha"))
    pk = TABLES[table]["pk"]
    set_clause = ", ".join([f"{k} = ?" for k in vals.keys()])
    params = tuple(vals.values()) + (pk_value,)
    run_command(f"UPDATE {table} SET {set_clause} WHERE {pk} = ?", params)

def delete_record(table, pk_value):
    pk = TABLES[table]["pk"]
    run_command(f"DELETE FROM {table} WHERE {pk} = ?", (pk_value,))



#VALIDACIONES PRE-INSERT/UPDATE#
def validate_inputs(table, data):
    errors = []
    for r in TABLES[table]["required"]:
        if str(data.get(r, "")).strip() == "":
            errors.append(f"Campo requerido vacío: {r}")

    if "rut" in data and data.get("rut") and not validate_rut(data.get("rut")):
        errors.append("Formato RUT inválido (ej: 11111111-1)")

    if "correo" in data and data.get("correo") and not validate_email(data.get("correo")):
        errors.append("Formato correo inválido")

    if "telefono" in data and data.get("telefono") and not validate_phone(data.get("telefono")):
        errors.append("Teléfono inválido (8-9 dígitos)")

    if "fecha_nacimiento" in data and data.get("fecha_nacimiento"):
        if parse_date_ddmmyyyy_to_yyyy_mm_dd(data.get("fecha_nacimiento")) is None:
            errors.append("Fecha de nacimiento inválida (usar DD/MM/YYYY)")

    if "fecha" in data and data.get("fecha"):
        if parse_date_ddmmyyyy_to_yyyy_mm_dd(data.get("fecha")) is None:
            errors.append("Fecha inválida (usar DD/MM/YYYY)")

    if "nota" in data and data.get("nota"):
        try:
            v = float(data.get("nota"))
            if v < 1.0 or v > 7.0:
                errors.append("La nota debe estar entre 1.0 y 7.0")
        except Exception:
            errors.append("La nota debe ser numérica")

    #Validación asistencia: solo 1 o 0
    if "presente" in data:
        val = str(data.get("presente")).strip()
        if val not in ("1", "0"):
            errors.append("El campo 'Presente' solo acepta 1 = Presente o 0 = Ausente.")

    fk_map = {
        "alumno": [("id_apoderado","apoderado"), ("id_curso","curso")],
        "curso": [("id_profesor_jefe","profesor")],
        "asignatura": [("id_profesor_jefe","profesor")],
        "nota": [("id_alumno","alumno"), ("id_asignatura","asignatura")],
        "asistencia": [("id_alumno","alumno")],
        "comunicacion": [("id_profesor","profesor"), ("id_alumno","alumno")]
    }

    if table in fk_map:
        for col, ref in fk_map[table]:
            val = data.get(col, None)
            if val is not None and str(val).strip() != "":
                df = run_query_df(f"SELECT 1 FROM {ref} WHERE {TABLES[ref]['pk']} = ? LIMIT 1", (val,))
                if df.empty:
                    errors.append(f"FK inválida: {col}={val} no existe en {ref}")
    return errors



#AUTENTICACIÓN#
def authenticate(username, password):
    u = str(username).strip()
    p = str(password).strip()
    if u == ADMIN_USER and p == ADMIN_PASS:
        return "admin", {"usuario": ADMIN_USER, "nombre": "Administrador", "apellido": ""}
    df = run_query_df("SELECT * FROM profesor WHERE rut = ? AND contraseña = ? LIMIT 1", (u, p))
    if not df.empty:
        rec = df.iloc[0].to_dict()
        rec.setdefault("nombre", "")
        rec.setdefault("apellido", "")
        return "profesor", rec
    df = run_query_df("SELECT * FROM apoderado WHERE rut = ? AND contraseña = ? LIMIT 1", (u, p))
    if not df.empty:
        rec = df.iloc[0].to_dict()
        rec.setdefault("nombre", "")
        rec.setdefault("apellido", "")
        return "apoderado", rec
    df = run_query_df("SELECT * FROM alumno WHERE rut = ? AND contraseña = ? LIMIT 1", (u, p))
    if not df.empty:
        rec = df.iloc[0].to_dict()
        rec.setdefault("nombre", "")
        rec.setdefault("apellido", "")
        return "alumno", rec
    return None, None



#MOSTRAR DATAFRAME#
def show_dataframe(df, role=None):
    """
    Muestra un dataframe en la UI.
    - Convierte fechas a DD/MM/YYYY
    - Si role == 'alumno' o 'apoderado' convierte 'presente' 1/0 a Presente/Ausente
    - Si role == 'admin' deja los valores crudos (1/0)
    """
    if df is None or df.empty:
        st.info("No hay registros.")
        return
    #Clonar para no modificar original en memoria
    df2 = df.copy()
    for c in df2.columns:
        if "fecha" in c:
            df2[c] = df2[c].apply(format_date_yyyy_mm_dd_to_ddmmyyyy)
    if role in ("alumno", "apoderado"):
        if "presente" in df2.columns:
            # Acepta"0"/"1"
            def map_pres(x):
                try:
                    xi = int(x)
                except:
                    xi = 1 if str(x).strip().lower() in ("true","t","yes","y") else 0
                return "Presente" if xi == 1 else "Ausente"
            df2["presente"] = df2["presente"].apply(map_pres)
    st.dataframe(df2, use_container_width=True)


#CARGAR EN BASE AL LOGIN#
if "logged" not in st.session_state:
    st.session_state["logged"] = False
    st.session_state["rol"] = None
    st.session_state["user"] = None

if "action" not in st.session_state:
    st.session_state["action"] = None

if "last_table" not in st.session_state:
    st.session_state["last_table"] = None

if "loaded_row" not in st.session_state:
    st.session_state["loaded_row"] = None



#PANTALLA DE LOGIN#
st.title("Sistema de Gestión - Colegio")
if not st.session_state["logged"]:
    with st.form("login_form"):
        usuario = st.text_input("Usuario (Rut)", placeholder="11111111-1")
        contraseña = st.text_input("Contraseña", type="password", placeholder="*********", help="Con letras, números y símbolos combinados.")
        submit_login = st.form_submit_button("Ingresar")
    if submit_login:
        rol, user_rec = authenticate(usuario, contraseña)
        if rol:
            st.session_state["logged"] = True
            st.session_state["rol"] = rol
            st.session_state["user"] = user_rec
            st.success("Acceso correcto.")
            st.rerun()
        else:
            st.error("Datos inválidos.")
    st.stop()


col_a, col_b = st.columns([4,1]) #No hace nada, es por comodidad del boton de cerrar sesión
with col_b:
    if st.button("Cerrar sesión"): #Boton de cerrar sesión
        st.session_state["logged"] = False
        st.session_state["rol"] = None
        st.session_state["user"] = None
        st.session_state["action"] = None
        st.session_state["loaded_row"] = None
        st.rerun()



#VISTA DE ADMIN (CRUD COMPLETO)#
def view_admin():
    st.header("Vista de Administrador")
    st.markdown("Gestionar datos de:")

    table_choice = st.selectbox("Seleccione una tabla", list(TABLES.keys()), index=0)

    if st.session_state["last_table"] != table_choice:
        st.session_state["action"] = None
        st.session_state["loaded_row"] = None
        st.session_state["last_table"] = table_choice

    #Ejemplos y formatos
    with st.expander("Ejemplos y formatos"):
        meta = TABLES[table_choice]

        #Mostrar campos principales por tabla
        for col, hint in meta["cols"]:
            label = col.capitalize()
            if col == "rut":
                st.write("Rut: RUT (ej: 11111111-1)")
            elif col == "nombre":
                st.write("Nombre: Nombre")
            elif col == "apellido":
                st.write("Apellido: Apellido")
            elif col == "correo":
                st.write("Correo: ejemplo@gmail.com")
            elif col == "telefono":
                st.write("Teléfono: 8-9 dígitos")
            elif col == "fecha_nacimiento" or ("fecha" in col and "nacimiento" in col):
                st.write("Fecha de nacimiento: DD/MM/YYYY")
            elif "fecha" in col:
                st.write("Fecha: DD/MM/YYYY")
            elif col == "contraseña":
                st.write("Contraseña: Con letras, números y símbolos combinados.")
            elif col == "presente":
                st.write("Asistencia: 1 = Presente, 0 = Ausente")
            else:
                #Si es un id o campo genérico, mostrar el hint simplificado
                st.write(f"{label}: {hint}")

        #Mensajes finales según corresponda
        if any("fecha" in c[0] for c in meta["cols"]):
            st.write("\nFechas: DD/MM/YYYY.")
        if any(c[0] == "contraseña" for c in meta["cols"]):
            st.write("\nContraseña: Con letras, números y símbolos combinados.")



#FORMULARIO# 
def form_inputs(table, loaded=None):
    meta = TABLES[table]
    inputs = {}
    for col, hint in meta["cols"]:
        label = col.capitalize()
        default = "" if loaded is None else str(loaded.get(col, "") or "")

        if col == "contraseña":
            inputs[col] = st.text_input(
                "Contraseña",
                value=default,
                type="password",
                placeholder="*********",
                help="Con letras, números y símbolos combinados."
            )
        elif "fecha" in col:
            inputs[col] = st.text_input(
                label,
                value=default if "/" in default else "",
                placeholder="DD/MM/YYYY"
            )
        else:
            inputs[col] = st.text_input(label, value=default, placeholder=hint)
    return inputs



#BOTONES#
def crud_section(table):
    st.subheader(f"Tabla: {table.capitalize()}")

    action = st.radio("Acción", ["Crear", "Leer", "Actualizar", "Eliminar", "Mostrar Todo"], horizontal=True)

    #CREAR
    if action == "Crear":
        st.write("### Crear registro")
        data = form_inputs(table)

        if st.button("Confirmar creación"):
            errors = validate_inputs(table, data)
            if errors:
                for e in errors:
                    st.error(e)
            else:
                insert_record(table, data)
                st.success("Registro creado correctamente.")

    #LEER
    elif action == "Leer":
        st.write("### Leer registro por ID")

        pk = TABLES[table]["pk"]
        pk_value = st.text_input(f"Ingrese {pk}")

        if st.button("Buscar"):
            if pk_value.strip() == "":
                st.warning("Ingrese un ID.")
            else:
                df = get_record_by_pk(table, pk_value)
                show_dataframe(df, role=st.session_state["rol"])

    #ACTUALIZAR
    elif action == "Actualizar":
        st.write("### Actualizar registro")

        pk = TABLES[table]["pk"]
        pk_value = st.text_input(f"Ingrese {pk} a actualizar")

        if st.button("Cargar datos"):
            df = get_record_by_pk(table, pk_value)
            if df.empty:
                st.error("ID no encontrado.")
            else:
                st.session_state["loaded_row"] = df.iloc[0].to_dict()

        if st.session_state["loaded_row"]:
            st.write("### Datos actuales:")
            show_dataframe(pd.DataFrame([st.session_state["loaded_row"]]))

            st.write("### Modificar:")
            new_data = form_inputs(table, st.session_state["loaded_row"])

            if st.button("Confirmar actualización"):
                errors = validate_inputs(table, new_data)
                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    update_record(table, pk_value, new_data)
                    st.success("Registro actualizado correctamente.")


    #ELIMINAR
    elif action == "Eliminar":
        st.write("### Eliminar registro")

        pk = TABLES[table]["pk"]
        pk_value = st.text_input(f"Ingrese {pk} a eliminar")

        if st.button("Eliminar"):
            delete_record(table, pk_value)
            st.success("Registro eliminado correctamente.")


    #MOSTRAR TODO
    elif action == "Mostrar Todo":
        df = run_query_df(f"SELECT * FROM {table}")
        show_dataframe(df, role=st.session_state["rol"])



#VISTA ADMIN#
def view_admin():
    st.header("Vista de Administrador")
    st.markdown("Gestionar datos de:")

    table_choice = st.selectbox("Seleccione una tabla", list(TABLES.keys()))

    if st.session_state["last_table"] != table_choice:
        st.session_state["action"] = None
        st.session_state["loaded_row"] = None
        st.session_state["last_table"] = table_choice

    #Ejemplos y formatos
    with st.expander("Ejemplos y formatos"):
        meta = TABLES[table_choice]
        for col, hint in meta["cols"]:
            col_n = col.capitalize()
            if col == "rut":
                st.write("Rut: RUT (ej: 11111111-1)")
            elif col == "correo":
                st.write("Correo: ejemplo@gmail.com")
            elif col == "telefono":
                st.write("Teléfono: 8-9 dígitos")
            elif "fecha" in col:
                st.write("Fecha: DD/MM/YYYY")
            elif col == "contraseña":
                st.write("Contraseña: Con letras, números y símbolos combinados.")
            elif col == "presente":
                st.write("Presente: 1 = Presente / 0 = Ausente")
            else:
                st.write(f"{col_n}: {hint}")

    crud_section(table_choice)



#VISTA PROFESOR#
def view_profesor():
    st.header("Vista de Profesor")

    st.write("Aquí puede ver los cursos, alumnos, asignaturas, notas, asistencia y comunicaciones asignadas.")

    #Profesor puede ver todo menos modificar alumnos/apoderados
    options = ["curso", "asignatura", "nota", "asistencia", "comunicacion"]
    table_choice = st.selectbox("Seleccione tabla a visualizar", options)

    df = run_query_df(f"SELECT * FROM {table_choice}")
    show_dataframe(df, role="profesor")



#VISTA APODERADO#
def view_apoderado():
    usr = st.session_state["user"]
    id_apo = usr["id_apoderado"]

    st.header(f"Vista de Apoderado: {usr['nombre']} {usr['apellido']}")

    #Obtener sus alumnos
    alumnos = run_query_df("SELECT * FROM alumno WHERE id_apoderado = ?", (id_apo,))

    if alumnos.empty:
        st.warning("No hay alumnos asociados.")
        return

    st.write("### Sus alumnos:")
    show_dataframe(alumnos, role="apoderado")

    alumno_ids = alumnos["id_alumno"].tolist()

    #Notas
    notas = run_query_df(
        f"SELECT * FROM nota WHERE id_alumno IN ({','.join(['?']*len(alumno_ids))})",
        alumno_ids
    )
    st.write("### Notas:")
    show_dataframe(notas, role="apoderado")

    #Asistencia
    asistencia = run_query_df(
        f"SELECT * FROM asistencia WHERE id_alumno IN ({','.join(['?']*len(alumno_ids))})",
        alumno_ids
    )
    st.write("### Asistencia:")
    show_dataframe(asistencia, role="apoderado")

    #Comunicaciones
    comunic = run_query_df(
        f"SELECT * FROM comunicacion WHERE id_alumno IN ({','.join(['?']*len(alumno_ids))})",
        alumno_ids
    )
    st.write("### Comunicaciones:")
    show_dataframe(comunic, role="apoderado")



#VISTA ALUMNO#
def view_alumno():
    usr = st.session_state["user"]
    id_al = usr["id_alumno"]

    st.header(f"Vista de Alumno: {usr['nombre']} {usr['apellido']}")

    #Datos personales
    datos = run_query_df("SELECT * FROM alumno WHERE id_alumno = ?", (id_al,))
    st.write("### Datos personales")
    show_dataframe(datos, role="alumno")

    #Notas
    notas = run_query_df("SELECT * FROM nota WHERE id_alumno = ?", (id_al,))
    st.write("### Notas")
    show_dataframe(notas, role="alumno")

    #Asistencia
    asistencia = run_query_df("SELECT * FROM asistencia WHERE id_alumno = ?", (id_al,))
    st.write("### Asistencia")
    show_dataframe(asistencia, role="alumno")

    #Comunicaciones
    comunic = run_query_df("SELECT * FROM comunicacion WHERE id_alumno = ?", (id_al,))
    st.write("### Comunicaciones")
    show_dataframe(comunic, role="alumno")



#RENDER PRINCIPAL SEGÚN ROL#
rol = st.session_state["rol"]

if rol == "admin":
    view_admin()
elif rol == "profesor":
    view_profesor()
elif rol == "apoderado":
    view_apoderado()
elif rol == "alumno":
    view_alumno()
else:
    st.error("Rol desconocido.")
