import os
import random
import string
import datetime
import time
import pyautogui, webbrowser
import getpass
import re
from time import sleep

# Constantes
ARCHIVO_CLIENTES = "clientes.txt"
ARCHIVO_BANCO = "banco.txt"
ARCHIVO_TRANSACCIONES = "transacciones.txt"
INTENTOS_MAXIMOS = 3
LIMITE_RETIRO_DIARIO = 500
LIMITE_TRANSFERENCIA_DIARIA = 500
COSTO_IMPRESION = 0.35

# Función para limpiar la pantalla
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

# Función para verificar si un archivo existe
def verificar_archivo(nombre_archivo):
    if not os.path.exists(nombre_archivo):
        with open(nombre_archivo, "w") as archivo:
            if nombre_archivo == ARCHIVO_CLIENTES:
                # Crear usuario admin por defecto
                archivo.write("admin,2025,Administrador,-,-,-,-,-,-,-,-,-,0,0\n")
    return True

# Función para inicializar archivos
def inicializar_archivos():
    verificar_archivo(ARCHIVO_CLIENTES)
    verificar_archivo(ARCHIVO_BANCO)
    verificar_archivo(ARCHIVO_TRANSACCIONES)

# Función para validar cédula ecuatoriana (10 dígitos)
def validar_cedula(cedula):
    if not cedula.isdigit() or len(cedula) != 10:
        return False
    
    # Algoritmo de validación de cédula ecuatoriana
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0
    
    for i in range(9):
        valor = int(cedula[i]) * coeficientes[i]
        if valor > 9:
            valor -= 9
        total += valor
    
    verificador = 10 - (total % 10)
    if verificador == 10:
        verificador = 0
    
    return verificador == int(cedula[9])

# Función para validar número de teléfono (9 dígitos)
def validar_telefono(telefono):
    return telefono.isdigit() and len(telefono) == 9

# Función para validar correo electrónico
def validar_correo(correo):
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, correo) is not None

# Función para validar fecha de nacimiento (formato dd/mm/aaaa)
def validar_fecha(fecha):
    try:
        dia, mes, anio = fecha.split("/")
        fecha_nacimiento = datetime.datetime(int(anio), int(mes), int(dia))
        
        # Verificar que no sea una fecha futura
        if fecha_nacimiento > datetime.datetime.now():
            return False
        
        # Verificar mayoría de edad (18 años)
        edad = (datetime.datetime.now() - fecha_nacimiento).days // 365
        if edad < 18:
            return False
        
        return True
    except:
        return False

# Función para generar clave provisional (PIN de 4 dígitos)
def generar_clave_provisional():
    return ''.join(random.choice(string.digits) for i in range(4))

# Función para simular envío de SMS/WhatsApp
def enviar_sms(telefono, mensaje):
    webbrowser.open(f"https://web.whatsapp.com/send?phone={telefono}&text={mensaje}")
    sleep(15)
    pyautogui.press('enter')
    sleep(5)
    # Cerrar el navegador
    pyautogui.hotkey('alt', 'f4')
    input("\nPresione Enter para continuar...")

# Función para buscar cliente por usuario (cédula)
def buscar_cliente(usuario):
    if not os.path.exists(ARCHIVO_CLIENTES):
        return None
    
    with open(ARCHIVO_CLIENTES, "r") as archivo:
        for linea in archivo:
            datos = linea.strip().split(",")
            if datos[0] == usuario:
                return datos
    return None

# Función para actualizar datos de un cliente
def actualizar_cliente(datos_cliente):
    lineas = []
    with open(ARCHIVO_CLIENTES, "r") as archivo:
        for linea in archivo:
            datos = linea.strip().split(",")
            if datos[0] == datos_cliente[0]:
                linea = ",".join(datos_cliente) + "\n"
            lineas.append(linea)
    
    with open(ARCHIVO_CLIENTES, "w") as archivo:
        archivo.writelines(lineas)

# Función para eliminar a un cliente
def eliminar_cliente(cedula):
    lineas = []
    cliente_encontrado = False
    
    with open(ARCHIVO_CLIENTES, "r") as archivo:
        for linea in archivo:
            datos = linea.strip().split(",")
            if datos[0] != cedula:
                lineas.append(linea)
            else:
                cliente_encontrado = True
    
    if cliente_encontrado:
        with open(ARCHIVO_CLIENTES, "w") as archivo:
            archivo.writelines(lineas)
        return True
    else:
        return False

# Función para registrar transacción
def registrar_transaccion(usuario, tipo, monto, saldo_anterior, saldo_nuevo, destinatario=None):
    fecha_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(ARCHIVO_TRANSACCIONES, "a") as archivo:
        if destinatario:
            archivo.write(f"{fecha_hora},{usuario},{tipo},{monto},{saldo_anterior},{saldo_nuevo},{destinatario}\n")
        else:
            archivo.write(f"{fecha_hora},{usuario},{tipo},{monto},{saldo_anterior},{saldo_nuevo}\n")

# Función para notificar al cliente sobre transacción
def notificar_transaccion(cliente, tipo_transaccion, monto, saldo_nuevo, destinatario=None):
    telefono = cliente[6]  # Obtener teléfono del cliente
    banco = obtener_datos_banco()
    
    mensaje = f"{banco['nombre']} le informa: Se ha realizado una {tipo_transaccion} por ${monto:.2f}. "
    
    if destinatario:
        cliente_destino = buscar_cliente(destinatario)
        nombre_destino = f"{cliente_destino[2]} {cliente_destino[3]}" if cliente_destino else "desconocido"
        mensaje += f"Destinatario: {nombre_destino}. "
    
    mensaje += f"Su saldo actual es: ${saldo_nuevo:.2f}"
    
    enviar_sms(telefono, mensaje)

# Función para calcular montos de retiro/transferencia del día
def calcular_monto_diario(usuario, tipo):
    fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y")
    total = 0
    
    with open(ARCHIVO_TRANSACCIONES, "r") as archivo:
        for linea in archivo:
            datos = linea.strip().split(",")
            fecha_transaccion = datos[0].split()[0]  # Obtener solo la fecha
            
            if fecha_transaccion == fecha_actual and datos[1] == usuario:
                if tipo == "Retiro" and datos[2] == "Retiro":
                    total += float(datos[3])
                elif tipo == "Transferencia" and datos[2] == "Transferencia Enviada":
                    total += float(datos[3])
    
    return total

# Función para obtener datos del banco
def obtener_datos_banco():
    if not os.path.exists(ARCHIVO_BANCO):
        return {"nombre": "Banco", "razon_social": "Banco S.A.", "ruc": "9999999999999", "direccion": "Dirección no registrada", "telefono": "999999999", "correo": "info@banco.com"}
    
    with open(ARCHIVO_BANCO, "r") as archivo:
        linea = archivo.readline().strip()
        if linea:
            datos = linea.split(",")
            return {
                "nombre": datos[0] if len(datos) > 0 else "Banco",
                "razon_social": datos[1] if len(datos) > 1 else "Banco S.A.",
                "ruc": datos[2] if len(datos) > 2 else "9999999999999",
                "direccion": datos[3] if len(datos) > 3 else "Dirección no registrada",
                "telefono": datos[4] if len(datos) > 4 else "999999999",
                "correo": datos[5] if len(datos) > 5 else "info@banco.com"
            }
    return {"nombre": "Banco", "razon_social": "Banco S.A.", "ruc": "9999999999999", "direccion": "Dirección no registrada", "telefono": "999999999", "correo": "info@banco.com"}

# Función para registrar datos del banco
def registrar_datos_banco(nombre, razon_social, ruc, direccion, telefono, correo):
    # Convertir nombre a mayúsculas
    nombre = nombre.upper()
    razon_social = razon_social.upper()
    direccion = direccion.upper()
    
    with open(ARCHIVO_BANCO, "w") as archivo:
        archivo.write(f"{nombre},{razon_social},{ruc},{direccion},{telefono},{correo}\n")
    return True

# Función para registrar nuevo cliente
def registrar_cliente(cedula, nombre, apellido, correo, direccion, telefono, fecha_nacimiento, tipo_cuenta, deposito_inicial):
    # Verificar si el cliente ya existe
    if buscar_cliente(cedula):
        return False, "El cliente ya existe"
    
    # Convertir a mayúsculas
    nombre = nombre.upper()
    apellido = apellido.upper()
    direccion = direccion.upper()
    tipo_cuenta = tipo_cuenta.upper()
    
    # Generar clave provisional
    clave_provisional = generar_clave_provisional()
    cambio_clave = "0"  # 0 indica que debe cambiar la clave
    intentos = "0"
    
    # Guardar cliente
    with open(ARCHIVO_CLIENTES, "a") as archivo:
        archivo.write(f"{cedula},{clave_provisional},{nombre},{apellido},{correo},{direccion},{telefono},{fecha_nacimiento},{tipo_cuenta},{cambio_clave},{intentos},{deposito_inicial},0,0\n")
    
    # Enviar SMS con clave provisional
    mensaje = f"Bienvenido al Banco. Su clave provisional es: {clave_provisional}. Por favor cámbiela en su primer acceso."
    enviar_sms(telefono, mensaje)
    
    # Registrar transacción de depósito inicial
    registrar_transaccion(cedula, "Deposito Inicial", deposito_inicial, 0, deposito_inicial)
    
    return True, clave_provisional

# Función para restablecer clave
def restablecer_clave(cedula):
    cliente = buscar_cliente(cedula)
    if not cliente:
        return False, "Cliente no encontrado"
    
    # Generar nueva clave provisional
    clave_provisional = generar_clave_provisional()
    
    # Actualizar cliente
    cliente[1] = clave_provisional  # Actualizar clave
    cliente[9] = "0"  # Forzar cambio de clave
    cliente[10] = "0"  # Reiniciar intentos
    
    actualizar_cliente(cliente)
    
    # Enviar SMS con clave provisional
    mensaje = f"Su nueva clave provisional es: {clave_provisional}. Por favor cámbiela en su próximo acceso."
    enviar_sms(cliente[6], mensaje)
    
    return True, clave_provisional

# Función para cambiar clave
def cambiar_clave(usuario, clave_actual, clave_nueva):
    cliente = buscar_cliente(usuario)
    if not cliente:
        return False, "Cliente no encontrado"
    
    # Verificar clave actual
    if cliente[1] != clave_actual:
        return False, "Clave actual incorrecta"
    
    # Actualizar cliente
    cliente[1] = clave_nueva  # Actualizar clave
    cliente[9] = "1"  # Marcar que ya cambió la clave
    
    actualizar_cliente(cliente)
    
    return True, "Clave cambiada exitosamente"

# Función para realizar depósito
def realizar_deposito(usuario, monto):
    cliente = buscar_cliente(usuario)
    if not cliente:
        return False, "Cliente no encontrado"
    
    saldo_anterior = float(cliente[11])
    saldo_nuevo = saldo_anterior + float(monto)
    
    # Actualizar cliente
    cliente[11] = str(saldo_nuevo)
    actualizar_cliente(cliente)
    
    # Registrar transacción
    registrar_transaccion(usuario, "Deposito", monto, saldo_anterior, saldo_nuevo)
    
    # Notificar al cliente
    notificar_transaccion(cliente, "depósito", monto, saldo_nuevo)
    
    return True, saldo_nuevo

# Función para realizar retiro
def realizar_retiro(usuario, monto):
    cliente = buscar_cliente(usuario)
    if not cliente:
        return False, "Cliente no encontrado"
    
    # Verificar que el monto sea múltiplo de 10
    if float(monto) % 10 != 0:
        return False, "El monto debe ser múltiplo de 10"
    
    # Verificar límite de retiro diario
    monto_retirado_hoy = calcular_monto_diario(usuario, "Retiro")
    if monto_retirado_hoy + float(monto) > LIMITE_RETIRO_DIARIO:
        return False, f"Límite diario de retiro excedido. Disponible: ${LIMITE_RETIRO_DIARIO - monto_retirado_hoy:.2f}"
    
    saldo_anterior = float(cliente[11])
    
    # Verificar fondos suficientes
    if saldo_anterior < float(monto):
        return False, "Fondos insuficientes"
    
    saldo_nuevo = saldo_anterior - float(monto)
    
    # Actualizar cliente
    cliente[11] = str(saldo_nuevo)
    actualizar_cliente(cliente)
    
    # Registrar transacción
    registrar_transaccion(usuario, "Retiro", monto, saldo_anterior, saldo_nuevo)
    
    # Notificar al cliente
    notificar_transaccion(cliente, "retiro", monto, saldo_nuevo)
    
    return True, saldo_nuevo

# Función para realizar transferencia
def realizar_transferencia(usuario_origen, usuario_destino, monto):
    # Verificar que existan ambos clientes
    cliente_origen = buscar_cliente(usuario_origen)
    cliente_destino = buscar_cliente(usuario_destino)
    
    if not cliente_origen:
        return False, "Cliente origen no encontrado"
    
    if not cliente_destino:
        return False, "Cliente destino no encontrado"
    
    if usuario_origen == usuario_destino:
        return False, "No puede transferir a su propia cuenta"
    
    # Verificar límite de transferencia diaria
    monto_transferido_hoy = calcular_monto_diario(usuario_origen, "Transferencia")
    if monto_transferido_hoy + float(monto) > LIMITE_TRANSFERENCIA_DIARIA:
        return False, f"Límite diario de transferencia excedido. Disponible: ${LIMITE_TRANSFERENCIA_DIARIA - monto_transferido_hoy:.2f}"
    
    saldo_origen = float(cliente_origen[11])
    
    # Verificar fondos suficientes
    if saldo_origen < float(monto):
        return False, "Fondos insuficientes"
    
    # Restar monto de la cuenta origen
    saldo_nuevo_origen = saldo_origen - float(monto)
    cliente_origen[11] = str(saldo_nuevo_origen)
    actualizar_cliente(cliente_origen)
    
    # Sumar monto a la cuenta destino
    saldo_destino = float(cliente_destino[11])
    saldo_nuevo_destino = saldo_destino + float(monto)
    cliente_destino[11] = str(saldo_nuevo_destino)
    actualizar_cliente(cliente_destino)
    
    # Registrar transacciones
    registrar_transaccion(usuario_origen, "Transferencia Enviada", monto, saldo_origen, saldo_nuevo_origen, usuario_destino)
    registrar_transaccion(usuario_destino, "Transferencia Recibida", monto, saldo_destino, saldo_nuevo_destino, usuario_origen)
    
    # Notificar al cliente origen
    notificar_transaccion(cliente_origen, "transferencia enviada", monto, saldo_nuevo_origen, usuario_destino)
    
    # Notificar al cliente destino
    mensaje = f"Ha recibido una transferencia por ${float(monto):.2f} de {cliente_origen[2]} {cliente_origen[3]}. Su saldo actual es: ${saldo_nuevo_destino:.2f}"
    enviar_sms(cliente_destino[6], mensaje)
    
    return True, saldo_nuevo_origen

# Función para consultar saldo
def consultar_saldo(usuario, imprimir=False):
    cliente = buscar_cliente(usuario)
    if not cliente:
        return False, "Cliente no encontrado"
    
    saldo = float(cliente[11])
    fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    if imprimir:
        # Cobrar por impresión
        nuevo_saldo = saldo - COSTO_IMPRESION
        cliente[11] = str(nuevo_saldo)
        actualizar_cliente(cliente)
        
        # Registrar transacción
        registrar_transaccion(usuario, "Cargo por impresión", COSTO_IMPRESION, saldo, nuevo_saldo)
        
        return True, nuevo_saldo, fecha_actual, True  # True adicional indica que se imprimió
    
    return True, saldo,fecha_actual, False

# Función para generar reporte de transacciones
def generar_reporte_transacciones(filtro=None, valor=None):
    if not os.path.exists(ARCHIVO_TRANSACCIONES):
        return []
    
    transacciones = []
    
    with open(ARCHIVO_TRANSACCIONES, "r") as archivo:
        for linea in archivo:
            datos = linea.strip().split(",")
            
            # Aplicar filtros si existen
            if filtro == "usuario" and valor != datos[1]:
                continue
            if filtro == "tipo" and valor != datos[2]:
                continue
            if filtro == "fecha" and not datos[0].startswith(valor):
                continue
            
            transaccion = {
                "fecha_hora": datos[0],
                "usuario": datos[1],
                "tipo": datos[2],
                "monto": float(datos[3]),
                "saldo_anterior": float(datos[4]),
                "saldo_nuevo": float(datos[5]),
                "destinatario": datos[6] if len(datos) > 6 else None
            }
            
            transacciones.append(transaccion)
    
    return transacciones

# Menú de cliente
def menu_cliente(usuario):
    cliente = buscar_cliente(usuario)
    if not cliente:
        print("Error: Cliente no encontrado")
        time.sleep(2)
        return
    
    # Verificar si debe cambiar la clave
    if cliente[9] == "0":
        limpiar_pantalla()
        print("Debe cambiar su clave provisional antes de continuar")
        clave_actual = getpass.getpass("Ingrese su clave actual: ")
        if clave_actual != cliente[1]:
            print("Clave incorrecta")
            time.sleep(2)
            return
        
        while True:
            clave_nueva = getpass.getpass("Ingrese su nueva clave (exactamente 4 dígitos): ")
            if len(clave_nueva) != 4 or not clave_nueva.isdigit():
                print("La clave debe ser de 4 dígitos numéricos")
                continue
            
            confirmacion = getpass.getpass("Confirme su nueva clave: ")
            if clave_nueva != confirmacion:
                print("Las claves no coinciden")
                continue
            
            exito, mensaje = cambiar_clave(usuario, clave_actual, clave_nueva)
            print(mensaje)
            if not exito:
                time.sleep(2)
                return
            break
    
    banco = obtener_datos_banco()
    
    while True:
        limpiar_pantalla()
        print(f"===== {banco['nombre']} =====")
        print(f"Bienvenido/a, {cliente[2]} {cliente[3]}")
        print(f"Tipo de cuenta: {cliente[8]}")
        print("\nMENU CLIENTE")
        print("1. Depositar")
        print("2. Retirar")
        print("3. Consultar saldo")
        print("4. Transferir a otra cuenta")
        print("5. Cambiar clave")
        print("6. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            limpiar_pantalla()
            print("===== DEPÓSITO =====")
            while True:
                try:
                    monto = float(input("Ingrese el monto a depositar: $"))
                    if monto <= 0:
                        print("El monto debe ser mayor a 0")
                        continue
                    break
                except ValueError:
                    print("Ingrese un valor numérico válido")
            
            exito, resultado = realizar_deposito(usuario, monto)
            if exito:
                print(f"Depósito exitoso. Saldo actual: ${resultado:.2f}")
            else:
                print(f"Error: {resultado}")
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == "2":
            limpiar_pantalla()
            print("===== RETIRO =====")
            
            # Verificar límite de retiro diario
            monto_retirado_hoy = calcular_monto_diario(usuario, "Retiro")
            disponible = LIMITE_RETIRO_DIARIO - monto_retirado_hoy
            
            if disponible <= 0:
                print("Ha alcanzado su límite diario de retiro")
                input("\nPresione Enter para continuar...")
                continue
                
            print(f"Límite diario disponible: ${disponible:.2f}")
            print("\nOpciones de retiro:")
            print("1. $10")
            print("2. $20")
            print("3. $40")
            print("4. $50")
            print("5. Otro valor")
            
            opcion_retiro = input("\nSeleccione una opción: ")
            
            if opcion_retiro == "1":
                monto = 10
            elif opcion_retiro == "2":
                monto = 20
            elif opcion_retiro == "3":
                monto = 40
            elif opcion_retiro == "4":
                monto = 50
            elif opcion_retiro == "5":
                while True:
                    try:
                        monto = float(input("Ingrese el monto a retirar (múltiplo de 10): $"))
                        if monto <= 0:
                            print("El monto debe ser mayor a 0")
                            continue
                        if monto % 10 != 0:
                            print("El monto debe ser múltiplo de 10")
                            continue
                        break
                    except ValueError:
                        print("Ingrese un valor numérico válido")
            else:
                print("Opción inválida")
                input("\nPresione Enter para continuar...")
                continue
            
            exito, resultado = realizar_retiro(usuario, monto)
            if exito:
                print(f"Retiro exitoso. Saldo actual: ${resultado:.2f}")
            else:
                print(f"Error: {resultado}")
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == "3":
            limpiar_pantalla()
            print("===== CONSULTA DE SALDO =====")
            
            print("¿Desea imprimir el comprobante? Se cobrará $0.35")
            print("1. Sí")
            print("2. No (solo mostrar en pantalla)")
            
            opcion_impresion = input("\nSeleccione una opción: ")

            imprimir = opcion_impresion == "1"
            
            exito, saldo, fecha , impreso = consultar_saldo(usuario, imprimir)
            if exito:
                print(f"fecha: {fecha}")
                if impreso:
                    print(f"Imprimiendo comprobante...")
                    print(f"Se ha cobrado ${COSTO_IMPRESION:.2f} por este servicio")
                    print(f"Su saldo actual es: ${saldo:.2f}")
                else:
                    print(f"Su saldo actual es: ${saldo:.2f}")
            else:
                print(f"Error: {saldo}")
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == "4":
            limpiar_pantalla()
            print("===== TRANSFERENCIA =====")
            
            # Verificar límite de transferencia diario
            monto_transferido_hoy = calcular_monto_diario(usuario, "Transferencia")
            disponible = LIMITE_TRANSFERENCIA_DIARIA - monto_transferido_hoy
            
            if disponible <= 0:
                print("Ha alcanzado su límite diario de transferencia")
                input("\nPresione Enter para continuar...")
                continue
                
            print(f"Límite diario disponible: ${disponible:.2f}")
            
            # Solicitar cuenta destino
            cedula_destino = input("Ingrese la cédula del destinatario: ")
            
            # Verificar si el destinatario existe
            cliente_destino = buscar_cliente(cedula_destino)
            if not cliente_destino:
                print("Cliente destinatario no encontrado")
                input("\nPresione Enter para continuar...")
                continue
            
            if cedula_destino == usuario:
                print("No puede transferir a su propia cuenta")
                input("\nPresione Enter para continuar...")
                continue
            
            print(f"Destinatario: {cliente_destino[2]} {cliente_destino[3]}")
            confirmacion = input("¿Es correcto? (S/N): ").upper()
            if confirmacion != "S":
                print("Transferencia cancelada")
                input("\nPresione Enter para continuar...")
                continue
            
            # Solicitar monto
            while True:
                try:
                    monto = float(input("Ingrese el monto a transferir: $"))
                    if monto <= 0:
                        print("El monto debe ser mayor a 0")
                        continue
                    break
                except ValueError:
                    print("Ingrese un valor numérico válido")
            
            # Realizar transferencia
            exito, resultado = realizar_transferencia(usuario, cedula_destino, monto)
            if exito:
                print(f"Transferencia exitosa a {cliente_destino[2]} {cliente_destino[3]}")
                print(f"Saldo actual: ${resultado:.2f}")
            else:
                print(f"Error: {resultado}")
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == "5":
            limpiar_pantalla()
            print("===== CAMBIO DE CLAVE =====")
            clave_actual = getpass.getpass("Ingrese su clave actual: ")
            
            while True:
                clave_nueva = getpass.getpass("Ingrese su nueva clave (exactamente 4 dígitos): ")
                if len(clave_nueva) != 4 or not clave_nueva.isdigit():
                    print("La clave debe ser de 4 dígitos numéricos")
                    continue
                
                confirmacion = getpass.getpass("Confirme su nueva clave: ")
                if clave_nueva != confirmacion:
                    print("Las claves no coinciden")
                    continue
                
                exito, mensaje = cambiar_clave(usuario, clave_actual, clave_nueva)
                print(mensaje)
                break
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == "6":
            break
        
        else:
            print("Opción inválida")
            time.sleep(1)

# Menú de administrador
def menu_administrador():
    banco = obtener_datos_banco()
    
    while True:
        limpiar_pantalla()
        print(f"===== {banco['nombre']} =====")
        print("\nMENU ADMINISTRADOR")
        print("1. Registrar datos del banco")
        print("2. Registrar nuevo cliente")
        print("3. Consultar datos de cliente")
        print("4. Actualizar datos de cliente")
        print("5. Eliminar cliente")
        print("6. Restablecer clave de cliente")
        print("7. Generar reporte de transacciones")
        print("8. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            limpiar_pantalla()
            print("===== REGISTRAR DATOS DEL BANCO =====")
            
            # Solicitar datos del banco
            nombre = input("Ingrese el nombre del banco: ").strip()
            if not nombre:
                print("El nombre del banco es obligatorio")
                input("\nPresione Enter para continuar...")
                continue
                

            razon_social = input("Ingrese la razón social: ").strip()
            if not razon_social:
                print("La razón social es obligatoria")
                input("\nPresione Enter para continuar...")
                continue
                
            ruc = input("Ingrese el RUC (13 dígitos): ").strip()
            if not ruc.isdigit() or len(ruc) != 13:
                print("El RUC debe tener 13 dígitos numéricos")
                input("\nPresione Enter para continuar...")
                continue
                
            direccion = input("Ingrese la dirección: ").strip()
            if not direccion:
                print("La dirección es obligatoria")
                input("\nPresione Enter para continuar...")
                continue
                
            telefono = input("Ingrese el teléfono (9 dígitos): ").strip()
            if not validar_telefono(telefono):
                print("El teléfono debe tener 9 dígitos numéricos")
                input("\nPresione Enter para continuar...")
                continue
                
            correo = input("Ingrese el correo electrónico: ").strip()
            if not validar_correo(correo):
                print("El correo electrónico no es válido")
                input("\nPresione Enter para continuar...")
                continue
                
            # Guardar datos del banco
            if registrar_datos_banco(nombre, razon_social, ruc, direccion, telefono, correo):
                print("Datos del banco registrados exitosamente")
            else:
                print("Error al registrar datos del banco")
                
            input("\nPresione Enter para continuar...")
            
        elif opcion == "2":
            limpiar_pantalla()
            print("===== REGISTRAR NUEVO CLIENTE =====")
            
            # Solicitar datos del cliente
            cedula = input("Ingrese la cédula (10 dígitos): ").strip()
            if not validar_cedula(cedula):
                print("La cédula no es válida")
                input("\nPresione Enter para continuar...")
                continue
                
            # Verificar si el cliente ya existe
            if buscar_cliente(cedula):
                print("Ya existe un cliente con esa cédula")
                input("\nPresione Enter para continuar...")
                continue
                
            nombre = input("Ingrese el nombre: ").strip()
            if not nombre:
                print("El nombre es obligatorio")
                input("\nPresione Enter para continuar...")
                continue
                
            apellido = input("Ingrese el apellido: ").strip()
            if not apellido:
                print("El apellido es obligatorio")
                input("\nPresione Enter para continuar...")
                continue
                
            correo = input("Ingrese el correo electrónico: ").strip()
            if not validar_correo(correo):
                print("El correo electrónico no es válido")
                input("\nPresione Enter para continuar...")
                continue
                
            direccion = input("Ingrese la dirección: ").strip()
            if not direccion:
                print("La dirección es obligatoria")
                input("\nPresione Enter para continuar...")
                continue
                
            telefono = input("Ingrese el teléfono (9 dígitos): ").strip()
            if not validar_telefono(telefono):
                print("El teléfono debe tener 9 dígitos numéricos")
                input("\nPresione Enter para continuar...")
                continue
                
            fecha_nacimiento = input("Ingrese la fecha de nacimiento (dd/mm/aaaa): ").strip()
            if not validar_fecha(fecha_nacimiento):
                print("La fecha de nacimiento no es válida o indica que es menor de edad")
                input("\nPresione Enter para continuar...")
                continue
                
            print("\nTipo de cuenta:")
            print("1. AHORRO")
            print("2. CORRIENTE")
            opcion_cuenta = input("\nSeleccione una opción: ")
            
            if opcion_cuenta == "1":
                tipo_cuenta = "AHORRO"
            elif opcion_cuenta == "2":
                tipo_cuenta = "CORRIENTE"
            else:
                print("Opción inválida")
                input("\nPresione Enter para continuar...")
                continue
                
            while True:
                try:
                    deposito_inicial = float(input("Ingrese el monto de depósito inicial: $"))
                    if deposito_inicial < 0:
                        print("El monto debe ser un valor positivo")
                        continue
                    break
                except ValueError:
                    print("Ingrese un valor numérico válido")
            
            # Registrar cliente
            exito, clave = registrar_cliente(cedula, nombre, apellido, correo, direccion, telefono, fecha_nacimiento, tipo_cuenta, deposito_inicial)
            
            if exito:
                print("Cliente registrado exitosamente")
                print(f"Se ha enviado la clave provisional {clave} al teléfono del cliente")
            else:
                print(f"Error: {clave}")
                
            input("\nPresione Enter para continuar...")
        
        elif opcion == "3":
            limpiar_pantalla()
            print("===== CONSULTAR DATOS DE CLIENTE =====")
            
            cedula = input("Ingrese la cédula del cliente: ").strip()
            cliente = buscar_cliente(cedula)
            
            if not cliente:
                print("Cliente no encontrado")
                input("\nPresione Enter para continuar...")
                continue
                
            print("\nDATOS DEL CLIENTE:")
            print(f"Nombre: {cliente[2]} {cliente[3]}")
            print(f"Cédula: {cliente[0]}")
            print(f"Correo: {cliente[4]}")
            print(f"Dirección: {cliente[5]}")
            print(f"Teléfono: {cliente[6]}")
            print(f"Fecha de Nacimiento: {cliente[7]}")
            print(f"Tipo de Cuenta: {cliente[8]}")
            print(f"Saldo Actual: ${float(cliente[11]):.2f}")
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == "4":
            limpiar_pantalla()
            print("===== ACTUALIZAR DATOS DE CLIENTE =====")
            
            cedula = input("Ingrese la cédula del cliente: ").strip()
            cliente = buscar_cliente(cedula)
            
            if not cliente:
                print("Cliente no encontrado")
                input("\nPresione Enter para continuar...")
                continue
                
            print("\nDATOS ACTUALES:")
            print(f"1. Nombre: {cliente[2]}")
            print(f"2. Apellido: {cliente[3]}")
            print(f"3. Correo: {cliente[4]}")
            print(f"4. Dirección: {cliente[5]}")
            print(f"5. Teléfono: {cliente[6]}")
            print(f"6. Cancelar")
            
            opcion_dato = input("\nSeleccione el dato a actualizar: ")
            
            if opcion_dato == "1":
                nuevo_valor = input("Ingrese el nuevo nombre: ").strip().upper()
                if not nuevo_valor:
                    print("El nombre es obligatorio")
                    input("\nPresione Enter para continuar...")
                    continue
                cliente[2] = nuevo_valor
            elif opcion_dato == "2":
                nuevo_valor = input("Ingrese el nuevo apellido: ").strip().upper()
                if not nuevo_valor:
                    print("El apellido es obligatorio")
                    input("\nPresione Enter para continuar...")
                    continue
                cliente[3] = nuevo_valor
            elif opcion_dato == "3":
                nuevo_valor = input("Ingrese el nuevo correo: ").strip()
                if not validar_correo(nuevo_valor):
                    print("El correo electrónico no es válido")
                    input("\nPresione Enter para continuar...")
                    continue
                cliente[4] = nuevo_valor
            elif opcion_dato == "4":
                nuevo_valor = input("Ingrese la nueva dirección: ").strip().upper()
                if not nuevo_valor:
                    print("La dirección es obligatoria")
                    input("\nPresione Enter para continuar...")
                    continue
                cliente[5] = nuevo_valor
            elif opcion_dato == "5":
                nuevo_valor = input("Ingrese el nuevo teléfono (9 dígitos): ").strip()
                if not validar_telefono(nuevo_valor):
                    print("El teléfono debe tener 9 dígitos numéricos")
                    input("\nPresione Enter para continuar...")
                    continue
                cliente[6] = nuevo_valor
            elif opcion_dato == "6":
                continue
            else:
                print("Opción inválida")
                input("\nPresione Enter para continuar...")
                continue
            
            # Actualizar cliente
            actualizar_cliente(cliente)
            print("Datos actualizados exitosamente")
            input("\nPresione Enter para continuar...")
        
        elif opcion == "5":
            limpiar_pantalla()
            print("===== ELIMINAR CLIENTE =====")
            
            cedula = input("Ingrese la cédula del cliente a eliminar: ").strip()
            cliente = buscar_cliente(cedula)
            
            if not cliente:
                print("Cliente no encontrado")
                input("\nPresione Enter para continuar...")
                continue
                
            print("\nDATOS DEL CLIENTE:")
            print(f"Nombre: {cliente[2]} {cliente[3]}")
            print(f"Cédula: {cliente[0]}")
            print(f"Saldo Actual: ${float(cliente[11]):.2f}")
            
            if float(cliente[11]) > 0:
                print("\nATENCIÓN: El cliente tiene saldo en su cuenta. No se puede eliminar.")
                input("\nPresione Enter para continuar...")
                continue
                
            confirmacion = input("\n¿Está seguro de eliminar este cliente? (S/N): ").upper()
            if confirmacion != "S":
                print("Operación cancelada")
                input("\nPresione Enter para continuar...")
                continue
                
            if eliminar_cliente(cedula):
                print("Cliente eliminado exitosamente")
            else:
                print("Error al eliminar cliente")
                
            input("\nPresione Enter para continuar...")
        
        elif opcion == "6":
            limpiar_pantalla()
            print("===== RESTABLECER CLAVE DE CLIENTE =====")
            
            cedula = input("Ingrese la cédula del cliente: ").strip()
            cliente = buscar_cliente(cedula)
            
            if not cliente:
                print("Cliente no encontrado")
                input("\nPresione Enter para continuar...")
                continue
                
            print(f"Cliente: {cliente[2]} {cliente[3]}")
            confirmacion = input("¿Está seguro de restablecer la clave de este cliente? (S/N): ").upper()
            
            if confirmacion != "S":
                print("Operación cancelada")
                input("\nPresione Enter para continuar...")
                continue
                
            exito, clave = restablecer_clave(cedula)
            
            if exito:
                print("Clave restablecida exitosamente")
                print(f"Se ha enviado la nueva clave provisional {clave} al teléfono del cliente")
            else:
                print(f"Error: {clave}")
                
            input("\nPresione Enter para continuar...")
        
        elif opcion == "7":
            limpiar_pantalla()
            print("===== REPORTE DE TRANSACCIONES =====")
            
            print("Filtros:")
            print("1. Por cliente")
            print("2. Por tipo de transacción")
            print("3. Por fecha")
            print("4. Sin filtros")
            
            opcion_filtro = input("\nSeleccione una opción: ")
            
            filtro = None
            valor = None
            
            if opcion_filtro == "1":
                cedula = input("Ingrese la cédula del cliente: ").strip()
                cliente = buscar_cliente(cedula)
                if not cliente:
                    print("Cliente no encontrado")
                    input("\nPresione Enter para continuar...")
                    continue
                filtro = "usuario"
                valor = cedula
            elif opcion_filtro == "2":
                print("\nTipos de transacción:")
                print("1. Depósito")
                print("2. Retiro")
                print("3. Transferencia Enviada")
                print("4. Transferencia Recibida")
                
                opcion_tipo = input("\nSeleccione una opción: ")
                
                if opcion_tipo == "1":
                    filtro = "tipo"
                    valor = "Deposito"
                elif opcion_tipo == "2":
                    filtro = "tipo"
                    valor = "Retiro"
                elif opcion_tipo == "3":
                    filtro = "tipo"
                    valor = "Transferencia Enviada"
                elif opcion_tipo == "4":
                    filtro = "tipo"
                    valor = "Transferencia Recibida"
                else:
                    print("Opción inválida")
                    input("\nPresione Enter para continuar...")
                    continue
            elif opcion_filtro == "3":
                fecha = input("Ingrese la fecha (dd/mm/aaaa): ").strip()
                # Validar formato de fecha
                try:
                    dia, mes, anio = fecha.split("/")
                    datetime.datetime(int(anio), int(mes), int(dia))
                    filtro = "fecha"
                    valor = fecha
                except:
                    print("Formato de fecha inválido")
                    input("\nPresione Enter para continuar...")
                    continue
            elif opcion_filtro == "4":
                pass
            else:
                print("Opción inválida")
                input("\nPresione Enter para continuar...")
                continue
            
            transacciones = generar_reporte_transacciones(filtro, valor)
            
            if not transacciones:
                print("No se encontraron transacciones")
                input("\nPresione Enter para continuar...")
                continue
                
            limpiar_pantalla()
            print("===== REPORTE DE TRANSACCIONES =====")
            if filtro == "usuario":
                cliente = buscar_cliente(valor)
                print(f"Cliente: {cliente[2]} {cliente[3]}")
            elif filtro == "tipo":
                print(f"Tipo: {valor}")
            elif filtro == "fecha":
                print(f"Fecha: {valor}")
                
            print("\n{:<20} {:<15} {:<20} {:<12} {:<12} {:<12} {:<15}".format(
                "Fecha/Hora", "Usuario", "Tipo", "Monto", "Saldo Ant.", "Saldo Nuevo", "Destinatario"))
            print("-" * 110)
            
            for t in transacciones:
                print("{:<20} {:<15} {:<20} ${:<11.2f} ${:<11.2f} ${:<11.2f} {:<15}".format(
                    t["fecha_hora"], t["usuario"], t["tipo"], t["monto"], t["saldo_anterior"], 
                    t["saldo_nuevo"], t["destinatario"] if t["destinatario"] else ""))
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == "8":
            break
        
        else:
            print("Opción inválida")
            time.sleep(1)

# Función principal
def main():
    # Inicializar archivos
    inicializar_archivos()

    # Actualizar usuario admin para asegurar que tenga clave de 4 dígitos
    admin = buscar_cliente("admin")
    if admin and (len(admin[1]) != 4 or admin[1] != "2025"):
        admin[1] = "2025"
        actualizar_cliente(admin)
    
    banco = obtener_datos_banco()
    
    while True:
        limpiar_pantalla()
        banco = obtener_datos_banco()
        print(f"===== {banco['nombre']} =====")
        print("\nBIENVENIDO")
        print("\n1. Iniciar sesión como Cliente")
        print("2. Recuperar clave")
        print("3. Salir")
        print("4. Iniciar sesion como administrador")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            limpiar_pantalla()
            print("===== INICIAR SESIÓN =====")
            
            usuario = input("Usuario (cédula): ").strip()
            clave = getpass.getpass("Clave: ")
            
            cliente = buscar_cliente(usuario)
            
            if not cliente:
                print("Usuario no encontrado")
                time.sleep(2)
                continue
            
            # Verificar bloqueo de la cuenta por intentos fallidos
            if int(cliente[10]) >= INTENTOS_MAXIMOS:
                print("Cuenta bloqueada por intentos fallidos. Contacte al administrador.")
                time.sleep(2)
                continue
            
            # Verificar clave
            if cliente[1] != clave:
                # Incrementar contador de intentos fallidos
                cliente[10] = str(int(cliente[10]) + 1)
                actualizar_cliente(cliente)
                
                intentos_restantes = INTENTOS_MAXIMOS - int(cliente[10])
                print(f"Clave incorrecta. Intentos restantes: {intentos_restantes}")
                time.sleep(2)
                continue
            
            # Reiniciar contador de intentos fallidos
            cliente[10] = "0"
            actualizar_cliente(cliente)
            
            # Redirigir según el tipo de usuario
            if usuario == "admin":
                menu_administrador()
            else:
                menu_cliente(usuario)
        
        elif opcion == "2":
            limpiar_pantalla()
            print("===== RECUPERAR CLAVE =====")
            
            usuario = input("Usuario (cédula): ").strip()
            cliente = buscar_cliente(usuario)
            
            if not cliente:
                print("Usuario no encontrado")
                time.sleep(2)
                continue
            
            # No permitir recuperar la clave del administrador
            if usuario == "admin":
                print("No se puede recuperar la clave del administrador")
                time.sleep(2)
                continue
            
            print(f"Se enviará una nueva clave provisional al teléfono registrado: {cliente[6]}")
            confirmacion = input("¿Desea continuar? (S/N): ").upper()
            
            if confirmacion != "S":
                print("Operación cancelada")
                time.sleep(2)
                continue
            
            exito, clave = restablecer_clave(usuario)
            
            if exito:
                print("Clave restablecida exitosamente")
                print(f"Se ha enviado la nueva clave provisional al teléfono registrado")
            else:
                print(f"Error: {clave}")
                
            time.sleep(2)
        
        elif opcion == "3":
            print("\n¡Gracias por utilizar nuestros servicios!")
            time.sleep(2)
            break
        elif opcion == "4":
            limpiar_pantalla()
            print("===== INGRESO DE ADMINISTRADOR =====")
            usuario = input("Ingrese usuario: ")
            clave = getpass.getpass("Ingrese clave: ")
            
            admin = buscar_cliente("admin")
            if admin and usuario == "admin" and clave == admin[1]:
                menu_administrador()
            else:
                print("Credenciales incorrectas")
                time.sleep(2)
        
        else:
            print("Opción inválida")
            time.sleep(1)

if __name__ == "__main__":
    main()