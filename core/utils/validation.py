# core/utils/validation.py

import re
import ipaddress


def validate_target(target):
    if not target:
        return False

    target = str(target).strip()
    target = re.sub(r"\s+", "", target)

    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        pass

    try:
        ipaddress.ip_network(target, strict=False)
        return True
    except ValueError:
        pass

    range_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})-(\d{1,5})$'
    m = re.match(range_pattern, target)
    if m:
        for i in range(4):
            if not 0 <= int(m.group(i + 1)) <= 255:
                return False
        return True

    if ',' in target:
        return all(validate_target(ip.strip()) for ip in target.split(','))

    return False
