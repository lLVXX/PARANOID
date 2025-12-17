import re
import ipaddress

def validate_target(target):
    """Valida IP individual, red CIDR, rango o múltiples IPs"""
    if not target:
        return False
    
    target = str(target).strip()
    
    # Eliminar espacios extra
    target = re.sub(r'\s+', '', target)
    
    try:
        # 1. Intentar como IP individual
        ipaddress.ip_address(target)
        return True
    except ValueError:
        pass
    
    try:
        # 2. Intentar como red CIDR
        ipaddress.ip_network(target, strict=False)
        return True
    except ValueError:
        pass
    
    # 3. Verificar si es rango (192.168.1.1-100)
    range_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})-(\d{1,5})$'
    range_match = re.match(range_pattern, target)
    
    if range_match:
        # Validar cada octeto
        for i in range(4):
            octet = int(range_match.group(i+1))
            if not 0 <= octet <= 255:
                return False
        # Validar último número del rango
        last = int(range_match.group(5))
        if not 1 <= last <= 65535:
            return False
        return True
    
    # 4. Verificar si es lista de IPs separadas por comas
    if ',' in target:
        ips = target.split(',')
        all_valid = True
        for ip in ips:
            ip = ip.strip()
            if not validate_single_target(ip):  # Usar validación simple
                all_valid = False
                break
        return all_valid
    
    return False

def validate_single_target(target):
    """Valida solo IP individual (para compatibilidad)"""
    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        return False

def is_cidr(target):
    """Verifica si es notación CIDR"""
    return '/' in target and validate_target(target)

def is_range(target):
    """Verifica si es un rango"""
    return '-' in target and '/' not in target and validate_target(target)

def is_multiple_ips(target):
    """Verifica si son múltiples IPs separadas por comas"""
    return ',' in target and validate_target(target)

def expand_target(target):
    """Expande el target a lista de IPs individuales"""
    if not validate_target(target):
        return []
    
    try:
        # Si es IP individual
        ipaddress.ip_address(target)
        return [target]
    except ValueError:
        pass
    
    try:
        # Si es red CIDR
        network = ipaddress.ip_network(target, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError:
        pass
    
    # Si es rango (192.168.1.1-100)
    range_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})-(\d{1,5})$'
    range_match = re.match(range_pattern, target)
    
    if range_match:
        base_ip = f"{range_match.group(1)}.{range_match.group(2)}.{range_match.group(3)}.{range_match.group(4)}"
        last_octet = int(range_match.group(5))
        
        # Obtener los 3 primeros octetos
        base_parts = base_ip.split('.')
        base_network = '.'.join(base_parts[:3])
        first = int(base_parts[3])
        
        ips = []
        for i in range(first, min(last_octet, 255) + 1):
            ips.append(f"{base_network}.{i}")
        return ips
    
    # Si son múltiples IPs separadas por comas
    if ',' in target:
        return [ip.strip() for ip in target.split(',')]
    
    return []