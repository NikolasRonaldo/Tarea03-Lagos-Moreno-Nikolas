#Tarea03-Lagos-Moreno-Nikolas
#integrantes:
#Nikolas Ronaldo Lagos Moreno - nikolas.lagos@alumnos.uv.cl


import subprocess
import getopt
import sys
import time
import requests

# Función pura que consulta la API por dirección MAC y devuelve el fabricante y el tiempo de respuesta
def obtener_datos_por_api(mac):
    mac = normalizar_mac(mac)  # Normalizamos la MAC aquí
    url = f"https://api.maclookup.app/v2/macs/{mac}/company/name?apiKey=01j9cmzmy3702pjpwyvdr54vcz01j9cnb7ta4aj7cvfzmqcm93ajaw63m3hknjtl"
    inicio = time.time()
    response = requests.get(url)
    fin = time.time()

    if response.status_code == 200:
        if response.text in ["*NO COMPANY*", "*PRIVATE*"]:
            return "Not found", round((fin - inicio) * 1000)  # Simula el "Not found" de la tarea
        else:
            return response.text.strip(), round((fin - inicio) * 1000)  # Simula el nombre del fabricante
    else:
        return None, round((fin - inicio) * 1000)

# Función pura que obtiene la tabla ARP y devuelve un diccionario con las IPs y sus MACs
def obtener_tabla_arp():
    dicc = {}
    try:
        tabla_arp = subprocess.check_output(['arp', '-a'], universal_newlines=True)
        arp_itt = tabla_arp.split('\n')
        for linea in arp_itt:
            if 'Internet Address' in linea or 'Interfaz' in linea or 'Direcci¢n' in linea or 'Direccion' in linea or 'Interface' in linea:  # Ignorar encabezados
                continue
            if linea.strip():
                parts = linea.split()
                if len(parts) >= 2:
                    cortado = parts[1].replace("-", ":").upper()  # Normaliza el formato de la MAC
                    dicc[parts[0]] = cortado  # IP: MAC
        return dicc
    except subprocess.CalledProcessError as e:
        return None  # Devuelve None si hay un error
    except Exception as e:
        return None

# Función pura para mostrar la ayuda
def ayuda():
    return (
        "Use: python OUILookup.py --mac <MAC> | --arp | [--help]\n"
        "--mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.\n"
        "--arp: muestra los fabricantes de los hosts disponibles en la tabla ARP.\n"
        "--help: muestra este mensaje y termina.\n"
    )

# Función que normaliza la MAC, añadiendo ceros si es necesario y cambiando guiones a dos puntos
def normalizar_mac(mac):
    # Convertir guiones a dos puntos
    mac = mac.replace("-", ":").lower()

    # Si la MAC es corta (como 9c:a5:13), añadimos ceros en las partes faltantes
    partes = mac.split(":")
    if len(partes) < 6:
        while len(partes) < 6:
            partes.append("00")
        mac = ":".join(partes)
    
    return mac

# Función para procesar la lógica de acuerdo a los argumentos pasados
def procesar_argumentos(argv):
    try:
        opts, args = getopt.getopt(argv, "m:ah", ["mac=", "arp", "help"])
        return opts
    except getopt.GetoptError:
        return None

# Función principal que organiza la lógica
def main(argv):
    parametros = procesar_argumentos(argv)

    if parametros is None or len(parametros) == 0:
        return ayuda()

    resultados = []
    for opt, arg in parametros:
        if opt in ('--help', "-h"):
            resultados.append(ayuda())
        elif opt in ("-m", "--mac"):
            if not arg:
                resultados.append("La opción --mac no puede estar vacía.")
            else:
                vendor, tiempo = obtener_datos_por_api(arg)
                resultados.append(f"MAC Address : {arg}\nFabricante : {vendor}\nTiempo de respuesta: {tiempo}ms")
        elif opt in ("-a", "--arp"):
            diccionario_arp = obtener_tabla_arp()
            if diccionario_arp:
                resultados.append("IP\t/\tMAC\t/\t/Vendor")
                for ip, mac in diccionario_arp.items():
                    vendor, tiempo = obtener_datos_por_api(mac)  # Consulta la API por cada MAC
                    resultados.append(f"{ip}\t {mac}, {vendor}")  # Muestra la IP, la MAC y el fabricante
            else:
                resultados.append("Error al obtener la tabla ARP.")

    return "\n".join(resultados)

# Esta parte solo se ejecuta si el archivo es ejecutado directamente
if __name__ == "__main__":
    resultado = main(sys.argv[1:])  # Pasamos solo los argumentos relevantes, sin el nombre del script
    print(resultado)