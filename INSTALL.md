# 🛠️ Instalación de PARANOID

Este documento describe paso a paso cómo instalar y preparar **PARANOID** en sistemas Linux.

PARANOID es una herramienta de **reconocimiento de red avanzada** y **requiere permisos elevados** para funcionar correctamente, debido a:

* uso de Nmap con técnicas avanzadas
* captura pasiva de tráfico
* selección manual de interfaces de red
* modificación opcional de `/etc/hosts`

---

## 🖥️ Sistemas soportados

* **Linux** (probado en):

  * Kali Linux
  * Distribuciones basadas en Debian
* Arquitectura: **x86_64**
* **Python 3.9 o superior**

> ⚠️ No se recomienda ejecutar PARANOID en contenedores Docker ni en entornos virtuales altamente restringidos, ya que el acceso a interfaces de red suele estar limitado.

---

## 📦 Dependencias del sistema

Antes de instalar PARANOID, asegúrate de tener las siguientes herramientas disponibles.

### 🔹 Dependencias requeridas

* `python3`
* `pip3`
* `nmap`

### 🔹 Dependencias recomendadas

* `tcpdump` → captura pasiva de tráfico
* `iproute2` → gestión de interfaces de red
* `net-tools` → utilidades de red clásicas

---

## 📥 Instalación de dependencias (Kali / Debian)

Ejecuta los siguientes comandos:

```bash
sudo apt update
sudo apt install -y \
  python3 \
  python3-pip \
  nmap \
  tcpdump \
  iproute2 \
  net-tools
```

---

## 📂 Clonar el repositorio

```bash
git clone https://github.com/lLVXX/PARANOID.git
cd PARANOID
```

---

## 🐍 Instalación de dependencias Python

PARANOID utiliza un conjunto mínimo de dependencias Python.

```bash
pip3 install -r requirements.txt
```

> 💡 Se recomienda usar `pip3` del sistema. PARANOID **no requiere** entornos virtuales para su funcionamiento normal.

---

## 🔐 Permisos y ejecución

PARANOID debe ejecutarse con privilegios elevados para:

* escaneos SYN (`-sS`)
* captura pasiva de paquetes
* escritura opcional en `/etc/hosts`

Ejecuta la herramienta con:

```bash
sudo python3 r-recon.py
```

---

## 🌐 Interfaces de red

Por defecto, PARANOID utiliza la interfaz `tun0`.

El usuario puede cambiar la interfaz manualmente desde la propia herramienta (por ejemplo `eth0`, `wlan0`, etc.), sin necesidad de modificar código.

Asegúrate de que la interfaz seleccionada:

* esté activa
* tenga conectividad con el objetivo

---

## ✅ Verificación rápida

Si la instalación fue correcta, deberías ver:

* el banner de PARANOID
* el prompt interactivo
* comandos como `set target`, `scan service`, `help`

---

## 🧪 Notas finales

* PARANOID **no es un framework de explotación**
* No ejecuta ataques ni payloads
* Está diseñado para **laboratorios, auditorías autorizadas y aprendizaje**

Consulta también:

* `README.md` → visión general
* `DISCLAIMER.md` → uso legal
* `LICENSE` → términos de distribución
