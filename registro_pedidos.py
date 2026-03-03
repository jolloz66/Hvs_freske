import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# =====================================
# CONFIGURACIÓN SUPABASE
# =====================================

SUPABASE_URL = "https://fhhetpvgxcoraicfryjf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZoaGV0cHZneGNvcmFpY2ZyeWpmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIyODA2NDMsImV4cCI6MjA4Nzg1NjY0M30.xF7Makb-cQhrhnV7EomOQVzbxt6wSpsct5Wv7KOyb3c"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")
st.title("📦 Sistema Comercial - Huevos")

# =====================================
# LISTAS FIJAS
# =====================================

VENDEDORES = ["01","02","03","06","08","10","11","12","14","15","16","18","24","25","26","23"]
REFERENCIAS = ["A","AA","AAA","B","C","JUMBO"]
COLORES = ["rojo","blanco"]
EMPAQUES = ["petx6","petx30","x15","x30","x10","estuche x12","estuchex4","x11","x12","x20","x22","x45","x60","x75","Granel"]
CANALES = ["horeca","retail","supermercado","tienda a tienda","institucional","autoservicios"]
FORMAS_PAGO = ["credito","contado"]
PLACAS = ["FBV679", "LKN999", "USB391", "UPQ214", "YAO09F"]
CONDUCTORES = ["Carlos Mario", "Diony", "Francisco", "Gregorio Morelos"]

TIPO_ETIQUETA = [
    "Marca propia",
    "Marca propia del cliente",
    "Sin etiqueta"
]

TIPO_LIMPIEZA = [
    "Limpieza estándar",
    "Limpieza al 100%"
]

DETALLE_CARTERA = [
    "Al día a la toma del pedido y a la fecha de despacho",
    "Al día a la toma del pedido, requiere verificación a la fecha de despacho",
    "No se encuentra al día, despacho sujeto a aprobación"
]

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛒 Nuevo Pedido",
    "🚚 Gestión Despachos",
    "📊 Dashboard",
    "🧾 Detalle Facturación",
    "🚛 Despachos"
])

# =====================================
# 🛒 NUEVO PEDIDO
# =====================================

with tab1:

    st.header("Registro de Pedido")

    if "carrito" not in st.session_state:
        st.session_state.carrito = pd.DataFrame(columns=[
            "referencia","color","empaque",
            "precio_huevo","precio_logistico",
            "cantidad","subtotal"
        ])

    vendedor = st.selectbox("Vendedor", VENDEDORES)
    cliente = st.text_input("Nombre del Cliente")
    canal = st.selectbox("Canal Comercial", CANALES)
    forma_pago = st.selectbox("Forma de Pago", FORMAS_PAGO)
    fecha_despacho = st.date_input("Fecha Despacho")
    observaciones = st.text_area("Observaciones")

    ficha_trazabilidad = st.radio(
        "¿Tiene ficha de trazabilidad?",
        ["Sí", "No"]
    )

    st.divider()

    # ===== NUEVOS CAMPOS =====
    colX, colY, colZ = st.columns(3)

    with colX:
        tipo_etiqueta = st.selectbox("Tipo de etiqueta", TIPO_ETIQUETA)

    with colY:
        tipo_limpieza = st.selectbox("Tipo de limpieza", TIPO_LIMPIEZA)

    with colZ:
        detalle_cartera = st.selectbox("Estado de cartera", DETALLE_CARTERA)

    st.divider()

    # ===== PRODUCTO =====
    col1, col2, col3 = st.columns(3)

    with col1:
        referencia = st.selectbox("Referencia", REFERENCIAS)
        precio_huevo = st.number_input("Precio Huevo", min_value=0.0)

    with col2:
        color = st.selectbox("Color", COLORES)
        precio_logistico = st.number_input("Precio Logístico", min_value=0.0)

    with col3:
        empaque = st.selectbox("Empaque", EMPAQUES)
        cantidad = st.number_input("Cantidad", min_value=1)

    if st.button("Agregar al carrito"):

        subtotal = cantidad * (precio_huevo + precio_logistico)

        nuevo_producto = {
            "referencia": referencia,
            "color": color,
            "empaque": empaque,
            "precio_huevo": precio_huevo,
            "precio_logistico": precio_logistico,
            "cantidad": cantidad,
            "subtotal": subtotal
        }

        st.session_state.carrito = pd.concat(
            [st.session_state.carrito, pd.DataFrame([nuevo_producto])],
            ignore_index=True
        )

    st.subheader("Carrito")
    st.dataframe(st.session_state.carrito, use_container_width=True)

    total_pedido = st.session_state.carrito["subtotal"].sum()
    st.markdown(f"### 💰 Total Pedido: ${total_pedido:,.2f}")

    # -----------------------------
    # CREAR O BUSCAR CLIENTE
    # -----------------------------

    def obtener_o_crear_cliente(nombre, canal, forma_pago):
        response = supabase.table("clientes").select("*").eq("nombre", nombre).execute()

        if response.data:
            return response.data[0]["id_cliente"]

        nuevo_cliente = {
            "nombre": nombre,
            "canal_comercial": canal,
            "forma_de_pago": forma_pago
        }

        insert = supabase.table("clientes").insert(nuevo_cliente).execute()
        return insert.data[0]["id_cliente"]

    # -----------------------------
    # GUARDAR PEDIDO
    # -----------------------------

    if st.button("Guardar Pedido Completo"):

        if cliente.strip() == "":
            st.error("El cliente es obligatorio.")
        elif st.session_state.carrito.empty:
            st.error("El carrito está vacío.")
        else:

            id_cliente = obtener_o_crear_cliente(cliente, canal, forma_pago)

            pedido_data = {
                "id_cliente": id_cliente,
                "vendedor": vendedor,
                "fecha_despacho": fecha_despacho.isoformat(),
                "total_cobrado": total_pedido,
                "observaciones": observaciones,
                "estado": "No despachado",
                "ficha_de_trazabilidad": True if ficha_trazabilidad == "Sí" else False,
                "facturado": False,
                "tipo_etiqueta": tipo_etiqueta,
                "tipo_limpieza": tipo_limpieza,
                "detalle_cartera": detalle_cartera
            }

            pedido_resp = supabase.table("pedidos").insert(pedido_data).execute()
            id_pedido = pedido_resp.data[0]["id_pedido"]

            detalles = []

            for _, row in st.session_state.carrito.iterrows():
                detalles.append({
                    "id_pedido": id_pedido,
                    "referencia": row["referencia"],
                    "color": row["color"],
                    "empaque": row["empaque"],
                    "precio_huevo": row["precio_huevo"],
                    "precio_logistico": row["precio_logistico"],
                    "cantidad": row["cantidad"]
                })

            supabase.table("detalle_pedido").insert(detalles).execute()

            st.session_state.carrito = st.session_state.carrito.iloc[0:0]

            st.success(f"✅ Pedido guardado correctamente. Código: {id_pedido}")
            st.rerun()

# =====================================
# 🚚 GESTIÓN DESPACHOS
# =====================================

with tab2:

    st.header("Gestión Logística")

    # ===== FILTRO FECHA =====
    fecha_filtro = st.date_input("Filtrar por fecha de despacho")

    pedidos = supabase.table("pedidos") \
        .select("*, clientes(nombre)") \
        .eq("fecha_despacho", fecha_filtro.isoformat()) \
        .order("id_pedido", desc=True) \
        .execute().data

    df = pd.DataFrame(pedidos)

    if df.empty:
        st.warning("No hay pedidos para esa fecha.")
    else:

        for _, row in df.iterrows():

            cliente_nombre = row["clientes"]["nombre"] if row.get("clientes") else ""

            st.subheader(f"Pedido #{row['id_pedido']} — {cliente_nombre}")

            # ===== INFO GENERAL =====
            col1, col2, col3 = st.columns(3)
            col1.write(f"💰 Total: ${row['total_cobrado']:,.0f}")
            col2.write(f"📅 Fecha despacho: {row['fecha_despacho']}")
            col3.write(f"📦 Estado: {row['estado']}")

            st.divider()

            # ===== DATOS LOGISTICOS =====
            colA, colB = st.columns(2)

            placa_actual = row.get("placa_vehiculo")
            conductor_actual = row.get("conductor")

            placa = colA.selectbox(
                "Placa del vehículo",
                PLACAS,
                index=PLACAS.index(placa_actual) if placa_actual in PLACAS else 0,
                key=f"placa_{row['id_pedido']}"
            )

            conductor = colB.selectbox(
                "Conductor",
                CONDUCTORES,
                index=CONDUCTORES.index(conductor_actual) if conductor_actual in CONDUCTORES else 0,
                key=f"conductor_{row['id_pedido']}"
            )

            nuevo_estado = st.selectbox(
                "Estado del despacho",
                ["No despachado", "En proceso", "Despachado"],
                index=["No despachado", "En proceso", "Despachado"].index(row["estado"]),
                key=f"estado_{row['id_pedido']}"
            )

            # ===== GUARDAR =====
            if st.button("Guardar logística", key=f"btn_{row['id_pedido']}"):

                supabase.table("pedidos") \
                    .update({
                        "placa_vehiculo": placa,
                        "conductor": conductor,
                        "estado": nuevo_estado
                    }) \
                    .eq("id_pedido", row["id_pedido"]) \
                    .execute()

                st.success("Logística actualizada")
                st.rerun()

            st.divider()
# =====================================
# 📊 DASHBOARD UNIDADES POR REFERENCIA
# =====================================

with tab3:

    import math
    import streamlit as st
    import pandas as pd

    st.header("📊 Producción y Consumo de Materiales")

    # ==========================
    # FILTRO RANGO FECHAS
    # ==========================
    col1, col2 = st.columns(2)

    fecha_inicio = col1.date_input("Desde", key="dash_desde")
    fecha_fin = col2.date_input("Hasta", key="dash_hasta")

    # ==========================
    # TRAER PEDIDOS
    # ==========================
    pedidos = supabase.table("pedidos") \
        .select("id_pedido, fecha_despacho") \
        .gte("fecha_despacho", fecha_inicio.isoformat()) \
        .lte("fecha_despacho", fecha_fin.isoformat()) \
        .execute().data

    if not pedidos:
        st.warning("No hay pedidos en el rango seleccionado")
        st.stop()

    df_ped = pd.DataFrame(pedidos)

    detalles_total = []

    for idp in df_ped["id_pedido"]:
        det = supabase.table("detalle_pedido") \
            .select("id_pedido, referencia, color, empaque, cantidad") \
            .eq("id_pedido", idp) \
            .execute().data

        detalles_total.extend(det)

    df = pd.DataFrame(detalles_total)

    # Unir fecha
    df = df.merge(df_ped, on="id_pedido")

    # ==========================
    # FUNCIÓN CÁLCULO MATERIALES
    # ==========================
    def calcular_materiales(row):

        emp = str(row["empaque"]).lower()
        huevos = row["cantidad"]

        numeros = ''.join(filter(str.isdigit, emp))

        if not numeros:
            return 0

        capacidad = int(numeros)

        # PET o ESTUCHE
        if "pet" in emp or "estuche" in emp:
            return math.ceil(huevos / capacidad)

        # CUBETAS NORMALES
        if emp.startswith("x"):
            return math.ceil(huevos / 30)

        return 0

    df["consumo_material"] = df.apply(calcular_materiales, axis=1)

    # ==========================
    # 1️⃣ UNIDADES POR REFERENCIA
    # ==========================
    st.subheader("📦 Unidades por Referencia y Color")

    resumen_ref = df.groupby(
        ["fecha_despacho", "referencia", "color"]
    )["cantidad"].sum().reset_index()

    st.dataframe(resumen_ref, use_container_width=True)

    graf_ref = resumen_ref.groupby("fecha_despacho")["cantidad"].sum()
    st.line_chart(graf_ref)

    # ==========================
    # 2️⃣ CONSUMO TOTAL MATERIALES
    # ==========================
    st.subheader("📦 Consumo Total Materiales")

    consumo_total = df.groupby("fecha_despacho")["consumo_material"].sum()

    st.metric("Total materiales usados", f"{consumo_total.sum():,.0f}")

    st.line_chart(consumo_total)

    # ==========================
    # 3️⃣ CONSUMO POR TIPO EMPAQUE
    # ==========================
    st.subheader("📦 Consumo por Tipo de Empaque")

    consumo_emp = df.groupby(
        ["fecha_despacho", "empaque"]
    )["consumo_material"].sum().reset_index()

    st.dataframe(consumo_emp, use_container_width=True)

    if not consumo_emp.empty:
        graf_emp = consumo_emp.pivot(
            index="fecha_despacho",
            columns="empaque",
            values="consumo_material"
        ).fillna(0)

        st.line_chart(graf_emp)



# =====================================
# 🧾 FACTURACIÓN DETALLADA POR DÍA
# =====================================

with tab4:
    st.header("Facturación Detallada del Día")

    # Selección de fecha
    filtro_fecha = st.date_input("Selecciona la Fecha de Despacho")

    # 1. CONSULTA A SUPABASE
    # Traemos campos de 'pedidos' y campos específicos de la relación 'clientes'
    campos_query = (
        "*, "
        "clientes(nombre, forma_de_pago)"
    )

    try:
        resultado_pedidos = supabase.table("pedidos") \
            .select(campos_query) \
            .eq("fecha_despacho", filtro_fecha.isoformat()) \
            .execute()
        
        pedidos = resultado_pedidos.data
        df_pedidos = pd.DataFrame(pedidos)

        if df_pedidos.empty:
            st.warning(f"No hay pedidos programados para el {filtro_fecha}")
        else:
            todos_detalles = []

            for _, pedido in df_pedidos.iterrows():
                # Traer el detalle de cada pedido
                detalle = supabase.table("detalle_pedido") \
                    .select("*") \
                    .eq("id_pedido", pedido["id_pedido"]) \
                    .execute().data

                # Extraer datos del cliente (que vienen como un diccionario por el join)
                datos_cliente = pedido.get("clientes", {})
                nombre_cliente = datos_cliente.get("nombre", "N/A")
                forma_pago_cliente = datos_cliente.get("forma_de_pago", "No definida")

                for item in detalle:
                    # Cálculo de subtotal
                    precio_h = item.get("precio_huevo", 0)
                    precio_l = item.get("precio_logistico", 0)
                    cantidad = item.get("cantidad", 0)
                    subtotal = cantidad * (precio_h + precio_l)

                    # Construcción de la fila del reporte
                    todos_detalles.append({
                        "ID Pedido": pedido["id_pedido"],
                        "Cliente": nombre_cliente,
                        "Vendedor": pedido.get("vendedor"),
                        "Referencia": item.get("referencia"),
                        "Color": item.get("color"),
                        "Cantidad": cantidad,
                        "Empaque": item.get("empaque"),
                        "Precio Huevo": precio_h,
                        "Precio Log.": precio_l,
                        "Subtotal": subtotal,
                        "Facturado": "Sí" if pedido.get("facturado") else "No",
                        # --- NUEVAS VARIABLES AGREGADAS ---
                        "Forma de Pago": forma_pago_cliente,
                        "Observaciones": pedido.get("observaciones"),
                        "Trazabilidad": pedido.get("ficha_de_trazabilidad"),
                        "Etiqueta": pedido.get("tipo_etiqueta"),
                        "Limpieza": pedido.get("tipo_limpieza"),
                        "Detalle Cartera": pedido.get("detalle_cartera")
                    })

            df_final = pd.DataFrame(todos_detalles)

            # Mostrar tabla principal
            st.dataframe(df_final, use_container_width=True, hide_index=True)

            st.divider()

            # --- SECCIÓN DE RESUMEN ---
            total_dia = df_final["Subtotal"].sum()
            # Filtramos por el string "Sí" que definimos arriba
            total_facturado = df_final[df_final["Facturado"] == "Sí"]["Subtotal"].sum()
            total_pendiente = total_dia - total_facturado

            col1, col2, col3 = st.columns(3)
            col1.metric("Total del Día", f"$ {total_dia:,.0f}")
            col2.metric("Facturado", f"$ {total_facturado:,.0f}")
            col3.metric("Pendiente", f"$ {total_pendiente:,.0f}")

            st.divider()

            # --- GESTIÓN DE FACTURACIÓN ---
            st.subheader("Gestión de Facturación")
            
            # Solo mostrar los que no están facturados
            pedidos_pendientes = df_pedidos[df_pedidos["facturado"] == False]

            if not pedidos_pendientes.empty:
                # Creamos una lista amigable para el selectbox
                opciones_pedidos = {
                    f"ID: {p['id_pedido']} - {p['clientes']['nombre']}": p['id_pedido'] 
                    for _, p in pedidos_pendientes.iterrows()
                }
                
                pedido_sel_label = st.selectbox(
                    "Seleccionar pedido para marcar como COMPLETADO/FACTURADO",
                    options=opciones_pedidos.keys()
                )
                
                id_a_actualizar = opciones_pedidos[pedido_sel_label]

                if st.button("Confirmar: Marcar como Facturado", type="primary"):
                    supabase.table("pedidos") \
                        .update({"facturado": True}) \
                        .eq("id_pedido", id_a_actualizar) \
                        .execute()

                    st.success(f"¡Pedido {id_a_actualizar} actualizado con éxito!")
                    st.rerun()
            else:
                st.success("🎉 ¡Excelente! Todos los pedidos de este día ya están facturados.")

    except Exception as e:
        st.error(f"Ocurrió un error al cargar los datos: {e}")
# =====================================
# 🚛 DASHBOARD DESPACHOS
# =====================================

with tab5:

    st.header("Despachos por Fecha")

    fecha_filtro = st.date_input("Selecciona fecha de despacho")

    pedidos = supabase.table("pedidos") \
        .select("id_pedido, fecha_despacho, estado, placa_vehiculo, conductor, clientes(nombre)") \
        .eq("fecha_despacho", fecha_filtro.isoformat()) \
        .order("placa_vehiculo") \
        .execute().data

    df = pd.DataFrame(pedidos)

    if df.empty:
        st.warning("No hay despachos para esa fecha.")
    else:

        # Preparar columnas
        df["cliente"] = df["clientes"].apply(lambda x: x["nombre"] if x else "")
        df = df.drop(columns=["clientes"])

        st.subheader("Listado de Despachos")
        st.dataframe(
            df[[
                "id_pedido",
                "cliente",
                "placa_vehiculo",
                "conductor",
                "estado"
            ]],
            use_container_width=True
        )

        st.divider()

        # ===== RESUMEN =====
        total_despachos = len(df)
        despachados = len(df[df["estado"] == "Despachado"])
        en_proceso = len(df[df["estado"] == "En proceso"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Pedidos del día", total_despachos)
        col2.metric("Despachados", despachados)
        col3.metric("En proceso", en_proceso)

        st.divider()

        # ===== DESPACHOS POR VEHICULO =====
        st.subheader("Despachos por Vehículo")

        vehiculos = df.groupby("placa_vehiculo")["id_pedido"].count().reset_index()
        vehiculos.columns = ["placa_vehiculo", "pedidos"]

        st.dataframe(vehiculos, use_container_width=True)



