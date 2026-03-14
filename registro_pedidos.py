import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date 
import numpy as np

# =====================================
# CONFIGURACIÓN SUPABASE
# =====================================

SUPABASE_URL = "https://fhhetpvgxcoraicfryjf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZoaGV0cHZneGNvcmFpY2ZyeWpmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIyODA2NDMsImV4cCI6MjA4Nzg1NjY0M30.xF7Makb-cQhrhnV7EomOQVzbxt6wSpsct5Wv7KOyb3c"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) 


st.set_page_config(layout="wide")

col1, col2 = st.columns([1,5])

with col2:
    st.title("Sistema de Gestión Logitica Huevos Freske")

st.title("📦 Sistema Comercial - Huevos")
# =====================================
# LISTAS FIJAS
# =====================================

VENDEDORES = ["01","02","03","06","08","10","11","12","14","15","16","18","24","25","26","23"]
REFERENCIAS = ["A","AA","AAA","B","C","JUMBO"]
COLORES = ["rojo","blanco"]
EMPAQUES = ["petx6","petx30","x15","x30","x10","estuche x12","estuchex4","x11","x12","x20","x22","x45","x60","x75","Granel","Canasta plastica"]
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

# 2. Diccionario de mapeo corregido
PRODUCTOS_MAP = {
    "0102": {"referencia": "C", "color": "rojo"},      # Corregido a C rojo
    "0151": {"referencia": "B", "color": "blanco"},
    "0202": {"referencia": "B", "color": "rojo"},
    "0251": {"referencia": "A", "color": "blanco"},
    "0203": {"referencia": "A", "color": "rojo"},
    "0351": {"referencia": "AA", "color": "blanco"},
    "0304": {"referencia": "AA", "color": "rojo"},
    "0451": {"referencia": "AAA", "color": "blanco"},
    "0405": {"referencia": "AAA", "color": "rojo"},
    "0506": {"referencia": "Jumbo", "color": "rojo"}, # J mayúscula, color minúscula
}


tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "🛒 Nuevo Pedido",
    "🚚 Gestión Despachos",
    "📊 Dashboard",
    "🧾 Detalle Facturación",
    "🚛 Despachos",
    "📦 Inventario",
    "📦 Inventario de Materiales", 
    "⚖️ Auditoría y conciliación final", 
    "🧮 Consumo Teórico de materiales",
    "🏷️ Inventario de Etiquetas"
])

# =====================================
# 🛒 NUEVO PEDIDO
# =====================================

with tab1:

    st.header("Registro de Pedido")

    # =========================
    # CONTROL LIMPIEZA FORMULARIO
    # =========================

    if "limpiar_formulario" not in st.session_state:
        st.session_state.limpiar_formulario = False

    if st.session_state.limpiar_formulario:

        st.session_state.cliente = ""
        st.session_state.observaciones = ""
        st.session_state.precio_huevo = 0.0
        st.session_state.precio_logistico = 0.0
        st.session_state.cantidad = 1

        st.session_state.limpiar_formulario = False

    # =========================
    # CARRITO
    # =========================

    if "carrito" not in st.session_state:
        st.session_state.carrito = pd.DataFrame(columns=[
            "referencia",
            "color",
            "empaque",
            "precio_huevo",
            "precio_logistico",
            "cantidad",
            "subtotal"
        ])

    # =========================
    # DATOS GENERALES
    # =========================

    vendedor = st.selectbox("Vendedor", VENDEDORES, key="vendedor")
    cliente = st.text_input("Nombre del Cliente", key="cliente")
    canal = st.selectbox("Canal Comercial", CANALES, key="canal")
    forma_pago = st.selectbox("Forma de Pago", FORMAS_PAGO, key="forma_pago")
    fecha_despacho = st.date_input("Fecha Despacho", key="fecha_despacho")
    observaciones = st.text_area("Observaciones", key="observaciones")

    ficha_trazabilidad = st.radio(
        "¿Tiene ficha de trazabilidad?",
        ["Sí", "No"],
        key="ficha_trazabilidad"
    )

    st.divider()

    # =========================
    # CAMPOS ADICIONALES
    # =========================

    colX, colY, colZ = st.columns(3)

    with colX:
        tipo_etiqueta = st.selectbox("Tipo de etiqueta", TIPO_ETIQUETA, key="tipo_etiqueta")

    with colY:
        tipo_limpieza = st.selectbox("Tipo de limpieza", TIPO_LIMPIEZA, key="tipo_limpieza")

    with colZ:
        detalle_cartera = st.selectbox("Estado de cartera", DETALLE_CARTERA, key="detalle_cartera")

    st.divider()

    # =========================
    # PRODUCTO
    # =========================

    col1, col2, col3 = st.columns(3)

    with col1:
        referencia = st.selectbox("Referencia", REFERENCIAS, key="referencia")
        precio_huevo = st.number_input("Precio Huevo", min_value=0.0, key="precio_huevo")

    with col2:
        color = st.selectbox("Color", COLORES, key="color")
        precio_logistico = st.number_input("Precio Logístico", min_value=0.0, key="precio_logistico")

    with col3:
        empaque = st.selectbox("Empaque", EMPAQUES, key="empaque")
        cantidad = st.number_input("Cantidad", min_value=1, key="cantidad")

    # =========================
    # AGREGAR PRODUCTO
    # =========================

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

        st.rerun()

    # =========================
    # CARRITO EDITABLE
    # =========================

    st.subheader("Carrito")

    if not st.session_state.carrito.empty:

        carrito_editado = st.data_editor(
            st.session_state.carrito,
            column_config={
                "referencia": st.column_config.Column(disabled=True),
                "color": st.column_config.Column(disabled=True),
                "empaque": st.column_config.Column(disabled=True),
                "subtotal": st.column_config.Column(disabled=True)
            },
            num_rows="dynamic",
            use_container_width=True,
            key="editor_carrito"
        )

        st.session_state.carrito = carrito_editado

        # recalcular subtotal
        st.session_state.carrito["subtotal"] = (
            (st.session_state.carrito["precio_huevo"] +
             st.session_state.carrito["precio_logistico"])
            * st.session_state.carrito["cantidad"]
        )

    else:
        st.info("El carrito está vacío")

    # =========================
    # TOTAL PEDIDO
    # =========================

    total_pedido = st.session_state.carrito["subtotal"].sum()

    st.markdown(f"### 💰 Total Pedido: ${total_pedido:,.2f}")

    # =========================
    # CREAR O BUSCAR CLIENTE
    # =========================

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

    # =========================
    # GUARDAR PEDIDO
    # =========================

    if st.button("Guardar Pedido Completo"):

        if cliente.strip() == "":
            st.error("El cliente es obligatorio")

        elif st.session_state.carrito.empty:
            st.error("El carrito está vacío")

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

            # limpiar carrito
            st.session_state.carrito = st.session_state.carrito.iloc[0:0]

            # limpiar formulario
            st.session_state.limpiar_formulario = True

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

        # CANASTA PLASTICA (30 huevos por canasta)
        if "canasta plastica" in emp:
            return math.ceil(huevos / 30)

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

# =====================================
# TAB 6: INVENTARIO CON HISTORIAL
# =====================================

with tab6:
    st.header("Control de Inventario")

    col_form, col_balance = st.columns([1, 2])

    # =====================================================
    # 📌 FORMULARIO DE REGISTRO
    # =====================================================

    with col_form:
        st.subheader("Registrar Movimiento")

        with st.form("form_registro_inventario"):

            tipo_mov = st.selectbox("Tipo de Movimiento", ["Entrada", "Salida"])
            cod_seleccionado = st.selectbox("Código de Producto", list(PRODUCTOS_MAP.keys()))

            info_prod = PRODUCTOS_MAP[cod_seleccionado]

            st.info(
                f"**Referencia:** {info_prod['referencia']}  \n"
                f"**Color:** {info_prod['color']}"
            )

            cantidad = st.number_input("Cantidad (Unidades)", min_value=1, step=1)
            documento = st.text_input("N° Documento (Factura/Remisión)")
            fecha_mov = st.date_input("Fecha", date.today())

            btn_inventario = st.form_submit_button(
                "Guardar Movimiento",
                use_container_width=True
            )

            if btn_inventario:

                datos_inv = {
                    "fecha": fecha_mov.isoformat(),
                    "tipo_movimiento": tipo_mov,
                    "codigo_huevo": cod_seleccionado,
                    "referencia": info_prod["referencia"],
                    "color": info_prod["color"],
                    "cantidad": cantidad,
                    "documento": documento
                }

                try:
                    supabase.table("inventario").insert(datos_inv).execute()
                    st.success("Movimiento registrado con éxito.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

    # =====================================================
    # 📊 BALANCE DE STOCK
    # =====================================================

    with col_balance:

        st.subheader("📦 Balance de Stock Actual")

        df_inv = pd.DataFrame()

        try:
            res_inv = supabase.table("inventario").select("*").execute()

            if res_inv.data:
                df_inv = pd.DataFrame(res_inv.data)

                # Calcular valor neto
                df_inv["valor_neto"] = df_inv.apply(
                    lambda x: x["cantidad"]
                    if x["tipo_movimiento"] == "Entrada"
                    else -x["cantidad"],
                    axis=1
                )

                # Agrupar en el orden correcto
                balance = df_inv.groupby(
                    ["codigo_huevo", "referencia", "color"]
                )["valor_neto"].sum().reset_index()

                # Renombrar columnas SIN depender del orden
                balance = balance.rename(columns={
                    "codigo_huevo": "Código",
                    "referencia": "Referencia",
                    "color": "Color",
                    "valor_neto": "Stock Actual"
                })

                st.dataframe(balance, use_container_width=True, hide_index=True)

                total_stock = balance["Stock Actual"].sum()
                st.metric("Total Unidades en Bodega", f"{total_stock:,.0f}")

            else:
                st.info("No hay movimientos registrados aún.")

        except Exception as e:
            st.error(f"Error al cargar balance: {e}")

    # =====================================================
    # 📜 HISTORIAL DE MOVIMIENTOS
    # =====================================================

    st.divider()
    st.subheader("📜 Historial de Movimientos Registrados")

    if not df_inv.empty:

        df_historial = df_inv[[
            "fecha",
            "tipo_movimiento",
            "codigo_huevo",
            "referencia",
            "color",
            "cantidad",
            "documento"
        ]].copy()

        df_historial = df_historial.rename(columns={
            "fecha": "Fecha",
            "tipo_movimiento": "Movimiento",
            "codigo_huevo": "Código",
            "referencia": "Referencia",
            "color": "Color",
            "cantidad": "Cantidad",
            "documento": "Documento"
        })

        st.dataframe(
            df_historial.sort_values(by="Fecha", ascending=False),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.write("No hay historial disponible.")

# =====================================
# TAB 7: INVENTARIO MATERIALES Y DOTACIÓN
# =====================================

# 1. Lista de Materiales (puedes ampliarla)
PRODUCTOS_MATERIALES = {
    "0601": "Bandeja de carton x 30*100", 
    "0603": "Bandeja de carton x30*120",
    "0608": "Caja de carton x 30",
    "0604": "Estuche carton x12*210",
    "0607": "Estuche Pet x 6",
    "0614": "Polystretch",
    "0701": "Camiseta tipo polo",
    "0702": "Jean Hombre"
}

PROVEEDORES_LISTA = ["Empaques y Cartones", "Multiservicios", "Comolsa", "Darnel", "Ipack", "Otros"]

with tab7: # Asegúrate de haber agregado "📦 Materiales" en la definición de st.tabs inicial
    st.header("📦 Gestión de Insumos y Materiales")
    
    col_m1, col_m2 = st.columns([1, 2])

    # --- COLUMNA 1: FORMULARIO DE REGISTRO ---
    with col_m1:
        st.subheader("Registrar Movimiento")
        with st.form("form_materiales"):
            tipo_mov_m = st.selectbox("Tipo de Movimiento", ["Entrada", "Salida"])
            cat_m = st.selectbox("Categoría", ["Insumos", "Dotacion", "Papelería"])
            cod_m = st.selectbox("Producto", list(PRODUCTOS_MATERIALES.keys()), 
                                format_func=lambda x: f"{x} - {PRODUCTOS_MATERIALES[x]}")
            
            prov_m = st.selectbox("Proveedor / Origen", PROVEEDORES_LISTA)
            cant_m = st.number_input("Cantidad", min_value=1, step=1)
            doc_m = st.text_input("N° Documento (Factura/Remisión)")
            
            if st.form_submit_button("Guardar Material"):
                nuevo_mat = {
                    "fecha_registro": date.today().isoformat(),
                    "numero_documento": doc_m,
                    "codigo_producto": cod_m,
                    "descripcion": PRODUCTOS_MATERIALES[cod_m],
                    "lote_proveedor": prov_m,
                    "cantidad": cant_m,
                    "tipo_movimiento": tipo_mov_m,
                    "categoria": cat_m
                }
                
                try:
                    supabase.table("inventario_materiales").insert(nuevo_mat).execute()
                    st.success(f"Registrado: {PRODUCTOS_MATERIALES[cod_m]}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

    # --- COLUMNA 2: BALANCE Y STOCK ---
    with col_m2:
        st.subheader("📋 Stock Actual de Almacén")
        try:
            res_m = supabase.table("inventario_materiales").select("*").execute()
            if res_m.data:
                df_m = pd.DataFrame(res_m.data)
                
                # Calcular cantidad neta (Entrada es positivo, Salida es negativo)
                df_m['neta'] = df_m.apply(
                    lambda x: x['cantidad'] if x['tipo_movimiento'] == "Entrada" else -x['cantidad'], 
                    axis=1
                )
                
                # Agrupar por descripción para ver el saldo
                balance_m = df_m.groupby(['descripcion', 'categoria'])['neta'].sum().reset_index()
                balance_m.columns = ['Descripción', 'Categoría', 'Existencias']
                
                # Mostrar solo los que tienen stock o mostrar todo
                st.dataframe(balance_m, use_container_width=True, hide_index=True)
                
                # Alerta de stock bajo (ejemplo: menos de 100 unidades)
                bajo_stock = balance_m[balance_m['Existencias'] < 100]
                if not bajo_stock.empty:
                    st.warning("⚠️ ¡Atención! Stock bajo en algunos insumos.")
            else:
                st.info("No hay registros de materiales aún.")
        except Exception as e:
            st.error(f"Error al cargar stock: {e}")

    # --- HISTORIAL COMPLETO ABAJO ---
    st.divider()
    st.subheader("📜 Últimos Movimientos de Almacén")
    if 'df_m' in locals() and not df_m.empty:
        st.dataframe(
            df_m[['fecha_registro', 'tipo_movimiento', 'descripcion', 'cantidad', 'lote_proveedor', 'numero_documento']]
            .sort_values(by="fecha_registro", ascending=False),
            use_container_width=True,
            hide_index=True
        )

# =====================================
# ⚖️ TAB 8: AUDITORÍA Y CONCILIACIÓN FINAL
# =====================================

with tab8:
    st.header("⚖️ Auditoría: Ventas vs. Salidas de Inventario")
    
    fecha_auditoria = st.date_input("Fecha para conciliar", date.today(), key="audit_v_final")

    try:
        # 1. Obtener Pedidos Despachados
        res_peds = supabase.table("pedidos").select("id_pedido").eq("fecha_despacho", fecha_auditoria.isoformat()).eq("estado", "Despachado").execute()
        ids_pedidos = [p["id_pedido"] for p in res_peds.data] if res_peds.data else []

        if not ids_pedidos:
            st.warning(f"No hay pedidos confirmados como 'Despachado' para el {fecha_auditoria}.")
        else:
            # 2. Datos de Ventas y Movimientos Reales
            res_det = supabase.table("detalle_pedido").select("*").in_("id_pedido", ids_pedidos).execute()
            df_ventas = pd.DataFrame(res_det.data)
            
            # Salidas de Tab 6 (Huevos) y Tab 7 (Materiales)
            res_inv_h = supabase.table("inventario").select("*").eq("fecha", fecha_auditoria.isoformat()).eq("tipo_movimiento", "Salida").execute()
            res_inv_m = supabase.table("inventario_materiales").select("*").eq("fecha_registro", fecha_auditoria.isoformat()).eq("tipo_movimiento", "Salida").execute()

            # --- SECCIÓN 1: HUEVOS ---
            st.subheader("🥚 1. Balance de Huevos (Venta vs Salida Bodega)")
            ventas_h = df_ventas.groupby(['referencia', 'color'])['cantidad'].sum().reset_index()
            
            if res_inv_h.data:
                bod_h = pd.DataFrame(res_inv_h.data).groupby(['referencia', 'color'])['cantidad'].sum().reset_index()
                cruce_h = pd.merge(ventas_h, bod_h, on=['referencia', 'color'], how='outer').fillna(0)
                cruce_h.columns = ['Ref', 'Color', 'Vendido', 'Salida Bodega']
                cruce_h['Diferencia'] = cruce_h['Vendido'] - cruce_h['Salida Bodega']
                st.dataframe(cruce_h, use_container_width=True, hide_index=True)

            st.divider()

            # --- SECCIÓN 2: MATERIALES (LÓGICA ESTRICTA) ---
            st.subheader("📦 2. Balance de Materiales (Teórico vs Almacén)")

            def calcular_material_estricto(row):
                emp = str(row["empaque"]).lower()
                cant_h = row["cantidad"]
                
                if "granel" in emp: return None

                # A. MATERIAL PLÁSTICO (PET)
                if "pet" in emp:
                    cap = 6 if "6" in emp else 30 # Por defecto 6 si es petx6
                    return {"cod": "0607", "tipo": "PLÁSTICO PET", "cant": math.ceil(cant_h / cap)}
                
                # B. ESTUCHES DE CARTÓN (x4, x12)
                if "estuche" in emp:
                    if "4" in emp: return {"cod": "0605", "tipo": "ESTUCHE CARTÓN x4", "cant": math.ceil(cant_h / 4)}
                    if "12" in emp: return {"cod": "0604", "tipo": "ESTUCHE CARTÓN x12", "cant": math.ceil(cant_h / 12)}

                # C. BANDEJAS DE CARTÓN (Para cualquier xN: x15, x30, x45, x60, x75...)
                # Se compara contra la unidad de bandeja de 30 huevos
                return {"cod": "0601", "tipo": "BANDEJA CARTÓN (Equiv. x30)", "cant": math.ceil(cant_h / 30)}

            df_ventas['audit'] = df_ventas.apply(calcular_material_estricto, axis=1)
            df_teorico = pd.DataFrame([x for x in df_ventas['audit'] if x is not None])

            if not df_teorico.empty:
                res_teorico = df_teorico.groupby(['cod', 'tipo'])['cant'].sum().reset_index()

                if res_inv_m.data:
                    res_real = pd.DataFrame(res_inv_m.data).groupby('codigo_producto')['cantidad'].sum().reset_index()
                    res_real.columns = ['cod', 'Cant. Real']

                    cruce_m = pd.merge(res_teorico, res_real, on='cod', how='outer').fillna(0)
                    cruce_m['Diferencia'] = cruce_m['Cant. Real'] - cruce_m['cant']
                    
                    # Limpieza para mostrar
                    final_m = cruce_m[['tipo', 'cant', 'Cant. Real', 'Diferencia']]
                    final_m.columns = ['Material', 'Debería Salir (Ventas)', 'Salió Real (Tab 7)', 'Desbalance']
                    
                    st.dataframe(final_m, use_container_width=True, hide_index=True)

                    # Alertas
                    for _, r in final_m.iterrows():
                        if r['Desbalance'] < 0:
                            st.error(f"🚨 Fuga en {r['Material']}: Faltan {abs(int(r['Desbalance']))} unidades por registrar en Almacén.")
                        elif r['Desbalance'] > 0:
                            st.warning(f"⚠️ Sobrecosto: Se gastaron {int(r['Desbalance'])} unidades de {r['Material']} adicionales.")
                else:
                    st.error("❌ No hay registros de salida de materiales en la Tab 7 para hoy.")
            
    except Exception as e:
        st.error(f"Error en auditoría: {e}") 

# =====================================
# TAB 9: CONSUMO TEÓRICO ETIQUETAS - ZUNCHO - PLASTIFLECHAS
# =====================================

with tab9:

    import math
    import pandas as pd

    st.header("Consumo Teórico de Materiales de Empaque")

    fecha_consumo = st.date_input("Fecha de despacho")

    # =========================
    # METROS DE ZUNCHO POR EMPAQUE
    # =========================

    ZUNCHO_POR_EMPAQUE = {
        "x15": 1.08,
        "x30": 2.01,
        "x10": 0.48,
        "x11": 0.48,
        "x12": 0.87,
        "x20": 2.01,
        "x22": 2.01,
        "x45": 2.33,
        "x60": 2.33,
        "x75": 2.55
    }

    # =========================
    # 1️⃣ TRAER PEDIDOS
    # =========================

    pedidos = supabase.table("pedidos") \
        .select("id_pedido, tipo_etiqueta, clientes(nombre)") \
        .eq("fecha_despacho", fecha_consumo.isoformat()) \
        .execute()

    if not pedidos.data:
        st.warning("No hay pedidos ese día")
        st.stop()

    df_ped = pd.DataFrame(pedidos.data)

    df_ped["cliente"] = df_ped["clientes"].apply(
        lambda x: x["nombre"] if isinstance(x, dict) else ""
    )

    ids = df_ped["id_pedido"].tolist()

    # =========================
    # 2️⃣ TRAER DETALLE PEDIDOS
    # =========================

    detalles = supabase.table("detalle_pedido") \
        .select("id_pedido, empaque, cantidad") \
        .in_("id_pedido", ids) \
        .execute()

    if not detalles.data:
        st.warning("No hay detalles de pedido")
        st.stop()

    df_det = pd.DataFrame(detalles.data)

    df = df_det.merge(df_ped, on="id_pedido")

    # =========================
    # 3️⃣ CALCULAR CONSUMO
    # =========================

    resultados = []

    for _, row in df.iterrows():

        cliente = row["cliente"]
        empaque = str(row["empaque"]).lower().strip()
        huevos = row["cantidad"]
        tipo_etiqueta = row["tipo_etiqueta"]

        # PET no usa zuncho ni plastiflecha
        if "pet" in empaque:
            bandejas = math.ceil(huevos / 30)
            empaques = math.ceil(huevos / 6)

            etiquetas = empaques if tipo_etiqueta != "Sin etiqueta" else 0
            plastiflechas = etiquetas * 2
            zuncho = 0

        else:

            numeros = ''.join(filter(str.isdigit, empaque))

            if numeros == "":
                continue

            capacidad = int(numeros)

            bandejas = math.ceil(huevos / 30)
            empaques = math.ceil(huevos / capacidad)

            # etiquetas
            if tipo_etiqueta == "Sin etiqueta":
                etiquetas = 0
            else:
                etiquetas = empaques

            plastiflechas = etiquetas * 2

            # zuncho por bandeja
            metros = ZUNCHO_POR_EMPAQUE.get(empaque, 0)
            zuncho = bandejas * metros

        resultados.append({
            "Cliente": cliente,
            "Empaque": empaque,
            "Bandejas x30": bandejas,
            "Empaques": empaques,
            "Etiquetas": etiquetas,
            "Plastiflechas": plastiflechas,
            "Zuncho (m)": round(zuncho, 2)
        })

    df_resultado = pd.DataFrame(resultados)

    # =========================
    # 4️⃣ TABLA PRINCIPAL
    # =========================

    st.subheader("Consumo por Pedido")

    st.dataframe(
        df_resultado,
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # 5️⃣ TOTALES
    # =========================

    st.divider()

    st.subheader("Consumo Total del Día")

    total_etiquetas = df_resultado["Etiquetas"].sum()
    total_plastiflechas = df_resultado["Plastiflechas"].sum()
    total_zuncho = df_resultado["Zuncho (m)"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Etiquetas",
        f"{total_etiquetas:,.0f}"
    )

    col2.metric(
        "Total Plastiflechas",
        f"{total_plastiflechas:,.0f}"
    )

    col3.metric(
        "Total Zuncho (m)",
        f"{total_zuncho:,.2f}"
    ) 


with tab10:

    st.header("🏷️ Inventario de Etiquetas")

    # =========================
    # LISTAS CONTROLADAS
    # =========================

    MARCAS_ETIQUETAS = [
        "ARA","ISIMO","Huevos Freske","Fresquesitos","H-H",
        "Rapi Huevo","La Vaquita","Mil Variedades","Stiker",
        "Max Ahorro","La Isla (Oceana)","Mercadona",
        "Automerco","Super Beta","My Tienda",
        "Maxi Oferta","Huevos Dia Norte","La 2000"
    ]

    REFERENCIAS_HUEVO = [
        "A rojo",
        "A blanco",
        "AA blanco",
        "AA rojo",
        "AAA rojo",
        "AAA blanco",
        "B rojo",
        "C rojo",
        "sin referencia"
    ]

    PRESENTACIONES = [
        "x6","x10","x11","x12","x15",
        "x20","x22","x30","x45","x60","x75",
        "sin referencia"
    ]

    # =========================
    # FORMULARIO
    # =========================

    st.subheader("➕ Registrar movimiento de etiquetas")

    with st.form("form_etiquetas"):

        col1, col2 = st.columns(2)

        with col1:

            fecha = st.date_input("Fecha")

            marca = st.selectbox(
                "Marca",
                MARCAS_ETIQUETAS
            )

            referencia_huevo = st.selectbox(
                "Referencia de huevo",
                REFERENCIAS_HUEVO
            )

        with col2:

            presentacion = st.selectbox(
                "Presentación",
                PRESENTACIONES
            )

            tipo_movimiento = st.selectbox(
                "Tipo movimiento",
                ["entrada","salida"]
            )

            paquetes = st.number_input(
                "Paquetes (1 paquete = 600 etiquetas)",
                min_value=1,
                step=1
            )

        guardar = st.form_submit_button("Registrar movimiento")

        if guardar:

            supabase.table("movimientos_etiquetas").insert({
                "fecha": str(fecha),
                "marca": marca,
                "referencia_huevo": referencia_huevo,
                "presentacion": presentacion,
                "tipo_movimiento": tipo_movimiento,
                "paquetes": int(paquetes)
            }).execute()

            st.success("Movimiento registrado correctamente")
            st.rerun()

    st.divider()

    # =========================
    # INVENTARIO
    # =========================

    st.subheader("📦 Balance de Inventario de Etiquetas")

    data = supabase.table("movimientos_etiquetas").select("*").execute()

    df = pd.DataFrame(data.data)

    if not df.empty:

        df["entrada"] = np.where(
            df["tipo_movimiento"] == "entrada",
            df["etiquetas_totales"],
            0
        )

        df["salida"] = np.where(
            df["tipo_movimiento"] == "salida",
            df["etiquetas_totales"],
            0
        )

        inventario = df.groupby(
            ["marca","referencia_huevo","presentacion"]
        ).agg(
            Entradas=("entrada","sum"),
            Salidas=("salida","sum")
        ).reset_index()

        inventario["Stock"] = (
            inventario["Entradas"] -
            inventario["Salidas"]
        )

        st.dataframe(
            inventario,
            use_container_width=True,
            hide_index=True
        )

        # =========================
        # ALERTAS
        # =========================

        st.subheader("⚠️ Alertas de Escasez")

        alertas = inventario[inventario["Stock"] < 3000]

        if not alertas.empty:

            st.warning("Inventario bajo en algunas etiquetas")

            st.dataframe(
                alertas,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success("Inventario de etiquetas saludable")

    else:

        st.info("No hay movimientos registrados")

    st.divider()

    # =========================
    # HISTORIAL
    # =========================

    st.subheader("📜 Historial de movimientos")

    if not df.empty:

        historial = df.sort_values(
            by="fecha",
            ascending=False
        )

        st.dataframe(
            historial[
                [
                    "fecha",
                    "marca",
                    "referencia_huevo",
                    "presentacion",
                    "tipo_movimiento",
                    "paquetes",
                    "etiquetas_totales"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("Aún no hay registros")






