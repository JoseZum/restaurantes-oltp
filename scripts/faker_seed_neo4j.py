#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
faker_seed_neo4j.py

– Genera datos sintéticos OLTP (usuarios, restaurantes, menus, pedidos, reservas)
– Crea CSVs para PostgreSQL
– Procesa el archivo map.osm (zona Cartago) para extraer nodos y aristas
– Asocia cada restaurante al nodo de calle más cercano
– Crea CSVs para Neo4j: nodes.csv, edges.csv, restaurantes_osm.csv

Requisitos:
    pip install faker pandas osmnx networkx shapely
    (osmnx ya incluye networkx y shapely internamente)

Estructura de salida esperada:
    data/
        usuarios.csv
        restaurantes.csv
        menus.csv
        pedidos.csv
        reservas.csv
        nodes.csv
        edges.csv
        restaurantes_osm.csv
"""

import os
import random
import csv
import datetime as dt

from faker import Faker
import pandas as pd
import osmnx as ox

# --------------------------------------------
# Parámetros generales
# --------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))         # directorio donde está este script
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")    # ../data
OSM_PATH = os.path.join(os.path.dirname(BASE_DIR), "map.osm") # ../map.osm

# Asegurarnos que exista el directorio data/
os.makedirs(DATA_DIR, exist_ok=True)

# Cantidades que queremos generar
N_USUARIOS   = 8000
N_RESTAURANT = 200
N_MENUS      = 800
N_PEDIDOS    = 30000
N_RESERVAS   = 30000

# Zona exacta que elegiste (Cartago)
LAT_MIN = 9.84406
LAT_MAX = 9.88380
LON_MIN = -83.94447
LON_MAX = -83.89606

faker = Faker("es_MX")

# --------------------------------------------
# Helper: genera lat/lon aleatorio dentro de la caja Cartago
# --------------------------------------------
def random_cartago_coords():
    lat = random.uniform(LAT_MIN, LAT_MAX)
    lon = random.uniform(LON_MIN, LON_MAX)
    return round(lat, 6), round(lon, 6)

# --------------------------------------------
# 1. Generar CSV: USUARIOS
# --------------------------------------------
print("Generando usuarios.csv ...")
with open(os.path.join(DATA_DIR, "usuarios.csv"), "w", newline="", encoding="utf8") as f:
    w = csv.writer(f)
    # Columnas de la tabla usuarios: id, email, password, rol, fecha_alta
    w.writerow(["id", "email", "password", "rol", "fecha_alta"])
    for i in range(1, N_USUARIOS + 1):
        email     = faker.unique.email()
        password  = faker.password(length=10)
        rol       = random.choice(["Cliente", "Chef", "Admin"])
        fecha_alta = faker.date_time_between(start_date="-2y", end_date="now").strftime("%Y-%m-%d %H:%M:%S")
        w.writerow([i, email, password, rol, fecha_alta])

# --------------------------------------------
# 2. Generar CSV: RESTAURANTES
# --------------------------------------------
print("Generando restaurantes.csv ...")
CATEGORIAS_REST = ["fast-food", "casual", "gourmet"]
with open(os.path.join(DATA_DIR, "restaurantes.csv"), "w", newline="", encoding="utf8") as f:
    w = csv.writer(f)
    # Columnas de restaurantes: id, nombre, direccion, telefono, capacidad, categoria_local, lat, lon
    w.writerow(["id", "nombre", "direccion", "telefono", "capacidad", "categoria_local", "lat", "lon"])
    for rid in range(1, N_RESTAURANT + 1):
        nombre     = faker.unique.company()
        direccion  = faker.street_address() + ", Cartago, CR"
        telefono   = faker.phone_number()
        capacidad  = random.randint(30, 120)
        categoria  = random.choice(CATEGORIAS_REST)
        lat, lon   = random_cartago_coords()
        w.writerow([rid, nombre, direccion, telefono, capacidad, categoria, lat, lon])

# --------------------------------------------
# 3. Generar CSV: MENUS
# --------------------------------------------
print("Generando menus.csv ...")
CATEGORIAS_MENU = ["Entrada", "Plato Fuerte", "Postre"]
with open(os.path.join(DATA_DIR, "menus.csv"), "w", newline="", encoding="utf8") as f:
    w = csv.writer(f)
    # Columnas de menus: id, titulo, categoria, activo, restaurante_id
    w.writerow(["id", "titulo", "categoria", "activo", "restaurante_id"])
    for mid in range(1, N_MENUS + 1):
        titulo        = faker.word().title()
        categoria     = random.choice(CATEGORIAS_MENU)
        activo        = random.choice([True, False])
        restaurante_id = random.randint(1, N_RESTAURANT)
        w.writerow([mid, titulo, categoria, activo, restaurante_id])

# --------------------------------------------
# 4. Generar CSV: PEDIDOS
# --------------------------------------------
print("Generando pedidos.csv ...")
with open(os.path.join(DATA_DIR, "pedidos.csv"), "w", newline="", encoding="utf8") as f:
    w = csv.writer(f)
    # Columnas de pedidos: id, menu_id, total, estado, restaurante_id, usuario_id, fecha_creacion
    w.writerow(["id", "menu_id", "total", "estado", "restaurante_id", "usuario_id", "fecha_creacion"])
    for pid in range(1, N_PEDIDOS + 1):
        menu_id        = random.randint(1, N_MENUS)
        total          = round(random.uniform(5, 100), 2)
        estado         = random.choice(["PENDING", "READY", "PICKED_UP", "CANCELLED"])
        restaurante_id = random.randint(1, N_RESTAURANT)
        usuario_id     = random.randint(1, N_USUARIOS)
        fecha_creacion = faker.date_time_between(start_date="-18m", end_date="now").strftime("%Y-%m-%d %H:%M:%S")
        w.writerow([pid, menu_id, total, estado, restaurante_id, usuario_id, fecha_creacion])

# --------------------------------------------
# 5. Generar CSV: RESERVAS
# --------------------------------------------
print("Generando reservas.csv ...")
with open(os.path.join(DATA_DIR, "reservas.csv"), "w", newline="", encoding="utf8") as f:
    w = csv.writer(f)
    # Columnas de reservas: id, usuario_id, restaurante_id, fecha, hora, invitados, estado, menu_id, pedido_id
    w.writerow(["id", "usuario_id", "restaurante_id", "fecha", "hora", "invitados", "estado", "menu_id", "pedido_id"])
    for ridx in range(1, N_RESERVAS + 1):
        usuario_id     = random.randint(1, N_USUARIOS)
        restaurante_id = random.randint(1, N_RESTAURANT)
        fecha_dt       = faker.date_time_between(start_date="-18m", end_date="now")
        fecha          = fecha_dt.date().isoformat()
        hora           = fecha_dt.time().strftime("%H:%M:%S")
        invitados      = random.randint(1, 8)
        estado         = random.choice(["ACTIVE", "CANCELLED"])
        menu_id        = random.randint(1, N_MENUS)
        pedido_id      = random.randint(1, N_PEDIDOS)
        w.writerow([ridx, usuario_id, restaurante_id, fecha, hora, invitados, estado, menu_id, pedido_id])

# --------------------------------------------
# 6. Procesar el archivo OSM y extraer nodos+aristas
# --------------------------------------------
print("Cargando grafo OSM desde:", OSM_PATH)

# 6.1 Construir grafo desde el archivo OSM
G = ox.graph_from_xml(OSM_PATH)

# 6.2 Convertir a grafo no dirigido (para shortestPath)
G_undir = G.to_undirected()

# 6.3 Extraer nodos a DataFrame
print("Extrayendo nodos de calle...")
nodes_data = []
for node_id, data in G_undir.nodes(data=True):
    # 'x' y 'y' contienen lon/lat en OSMnx
    lon = data.get("x")
    lat = data.get("y")
    nodes_data.append({"node_id": node_id, "lon": lon, "lat": lat})
df_nodes = pd.DataFrame(nodes_data)

# Guardar nodes.csv (para Neo4j)
nodes_csv_path = os.path.join(DATA_DIR, "nodes.csv")
df_nodes.to_csv(nodes_csv_path, index=False)
print(f"  → {len(df_nodes)} nodos exportados a {nodes_csv_path}")

# 6.4 Extraer aristas (edges) a DataFrame
print("Extrayendo aristas (edges) de OSM...")
edge_data = []
for u, v, data in G_undir.edges(data=True):
    if "length" in data:
        dist = data["length"]
    else:
        # Si no hay longitud, estimamos con Haversine aproximado
        lat1 = df_nodes.loc[df_nodes.node_id == u, "lat"].values[0]
        lon1 = df_nodes.loc[df_nodes.node_id == u, "lon"].values[0]
        lat2 = df_nodes.loc[df_nodes.node_id == v, "lat"].values[0]
        lon2 = df_nodes.loc[df_nodes.node_id == v, "lon"].values[0]
        dist = ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5 * 111000
    edge_data.append({"source": u, "target": v, "distance": dist})

df_edges = pd.DataFrame(edge_data)

# Guardar edges.csv (para Neo4j)
edges_csv_path = os.path.join(DATA_DIR, "edges.csv")
df_edges.to_csv(edges_csv_path, index=False)
print(f"  → {len(df_edges)} aristas exportadas a {edges_csv_path}")

# --------------------------------------------
# 7. Asociar CADA RESTAURANTE al nodo de calle más cercano
# --------------------------------------------
print("Asociando restaurantes al nodo OSM más cercano...")
df_rest = pd.read_csv(os.path.join(DATA_DIR, "restaurantes.csv"))

restaurante_osm_rows = []
for idx, row in df_rest.iterrows():
    lon, lat = row["lon"], row["lat"]
    # nearest_nodes espera los argumentos (G, X, Y)
    nearest_node = ox.distance.nearest_nodes(G_undir, X=lon, Y=lat)
    restaurante_osm_rows.append({
        "restaurante_id": int(row["id"]),
        "nombre":         row["nombre"],
        "lat":            row["lat"],
        "lon":            row["lon"],
        "nearest_node_id": int(nearest_node)
    })

df_rest_osm = pd.DataFrame(restaurante_osm_rows)

# Guardar restaurantes_osm.csv
rest_osm_csv_path = os.path.join(DATA_DIR, "restaurantes_osm.csv")
df_rest_osm.to_csv(rest_osm_csv_path, index=False)
print(f"  → {len(df_rest_osm)} restaurantes asociados a nodos guardados en {rest_osm_csv_path}")

print("¡Todo listo! CSVs generados en ./data:")
for fn in os.listdir(DATA_DIR):
    print("   >", fn)
