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

### Instalación en Kali / Debian

```bash
sudo apt update
sudo apt install -y \
  python3 \
  python3-pip \
  nmap \
  tcpdump \
  iproute2 \
  net-tools


