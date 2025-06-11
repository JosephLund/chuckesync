import geocoder


def get_ip_info(ip):
    g = geocoder.ipinfo(ip)  # no 'method=' needed here
    return {
        "lat": g.latlng[0] if g.latlng else None,
        "lon": g.latlng[1] if g.latlng else None,
        "timezone": getattr(g, "timezone", "America/Los_Angeles")
    }