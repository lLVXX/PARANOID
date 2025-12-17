# PARANOID

> Context-aware Nmap reconnaissance framework with traffic intelligence and Active Directory awareness.

PARANOID es una herramienta de **reconocimiento de red avanzada**, diseñada como un wrapper inteligente sobre Nmap que combina:

- Escaneo de puertos y servicios
- Análisis pasivo de tráfico
- Detección automática de hostnames
- Conciencia de entornos Active Directory
- Control explícito del usuario sobre objetivo e interfaz

🚫 No es un exploit framework  
🚫 No ejecuta ataques  
🚫 No toma decisiones ofensivas  

PARANOID **observa, correlaciona y contextualiza**.





# 🛠️ Instalación de PARANOID

Este documento explica cómo instalar y preparar **PARANOID** en sistemas Linux.

PARANOID es una herramienta de reconocimiento de red que **requiere permisos elevados**
para funcionar correctamente, debido a su uso de Nmap avanzado, captura pasiva de tráfico
y gestión opcional del archivo `/etc/hosts`.

---

## 🖥️ Sistemas soportados

- Linux (probado en):
  - Kali Linux
  - Distribuciones basadas en Debian
- Arquitectura: `x86_64`
- Python **3.9 o superior**

> ⚠️ No se recomienda ejecutar PARANOID en contenedores Docker o entornos virtuales
> altamente restringidos, ya que puede limitar el acceso a interfaces de red.

---

## 📦 Dependencias del sistema

Antes de instalar PARANOID, asegúrate de tener las siguientes herramientas instaladas.

### 🔹 Dependencias requeridas
- `python3`
- `pip3`
- `nmap`

### 🔹 Dependencias recomendadas
- `tcpdump` → captura pasiva de tráfico
- `iproute2` → gestión de interfaces
- `net-tools` → utilidades de red clásicas



## 📚 Documentation

- 📦 [Installation Guide](INSTALL.md)
- ⚠️ [Legal Disclaimer](DISCLAIMER.md)
- 📄 [License](LICENSE)
