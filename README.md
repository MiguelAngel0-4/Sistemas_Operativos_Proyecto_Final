# Sistemas_Operativos_Proyecto_Final

## El archivo pequeño_OS.py contiene la aplicación completa en ~627 líneas con un tema oscuro tipo terminal. Aquí un resumen de lo que incluye cada módulo:

## Arquitectura:

### Pequeño_OS (Ventana Principal)
├── FileExplorer   → módulo A
├── ProcessManager → módulo B
├── EduShell       → módulo C
└── SysInfo        → módulo D

## MODULOS IMPLEMENTADOS:

Módulo                       Características

-📁 Explorador Listado con iconos, tamaño, tipo; doble-clic para navegar; subir nivel; refrescar; mensaje si carpeta vacía
-⚙️ Procesos Tabla con PID, nombre, estado, CPU%, RAM; filtro en vivo; ordenar columnas; botón terminar con confirmación, 
-🖥️ Shell Whitelist de comandos seguros (ls, dir, pwd, echo, whoami, date…); salida coloreada; fallback cross-platform para ls/dir
-ℹ️ Sistema Usuario, home, OS, versión, arquitectura, CPU, núcleos, disco total/usado/libre y RAM


# COMO EJECUTAR?

## 1. Instalar dependencia (solo una vez)
pip install psutil

# 2. Ejecutar
python3 pequeño_OS.py