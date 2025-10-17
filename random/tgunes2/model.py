# Bird and Hulstrom's Solar Irradiance Model
# Based on: https://instesre.org/Solar/BirdModelNew.htm

import math

def station_pressure(p_sea_level, h):
    """
    p_sea_level : deniz seviyesindeki basınç (mbar)
    h           : yükseklik (metre)
    """
    H = float(h) / 1000.0
    return float(p_sea_level) * math.exp(-0.119 * H - 0.0013 * H * H)


def get_julian_date(month, day, year, hour, minute, second):
    """
    Gregorian tarihinden Julian Date hesaplama
    """
    m, d, y = int(month), int(day), int(year)
    hr, mn, sec = float(hour), float(minute), float(second)

    if m < 3:
        y -= 1
        m += 12

    A = math.floor(y / 100.0)
    B = 2 - A + math.floor(A / 4.0)
    JD = (math.floor(365.25 * (y + 4716)) +
          math.floor(30.6001 * (m + 1)) +
          d + B - 1524.5)

    return JD + hr / 24.0 + mn / 1440.0 + sec / 86400.0


def get_solar_position(JD, lon, lat):
    """
    Güneş zenit açısını hesaplar (derece).
    JD  : Julian Date
    lon : Boylam (°) (Batı negatif)
    lat : Enlem (°) (Kuzey pozitif)
    """
    dr = math.pi / 180.0
    T = (JD - 2451545.0) / 36525.0

    L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T * T
    M = 357.52910 + 35999.05030 * T - 0.0001559 * T * T - 0.00000048 * T * T * T
    M_rad = M * dr

    e = 0.016708617 - 0.000042037 * T - 0.0000001236 * T * T
    C = ((1.914600 - 0.004817 * T - 0.000014 * T * T) * math.sin(M_rad) +
         (0.019993 - 0.000101 * T) * math.sin(2.0 * M_rad) +
         0.000290 * math.sin(3.0 * M_rad))

    L_true = L0 + C
    L_true = L_true % 360.0

    f = M_rad + C * dr
    R = 1.000001018 * (1.0 - e * e) / (1.0 + e * math.cos(f))

    # Sidereal time
    Sidereal_time = (280.46061837 +
                     360.98564736629 * (JD - 2451545.0) +
                     0.000387933 * T * T -
                     T * T * T / 38710000.0)

    Sidereal_time = Sidereal_time % 360.0

    # Obliquity
    Obliquity = (23.0 + 26.0 / 60.0 +
                 21.448 / 3600.0 -
                 46.8150 / 3600.0 * T -
                 0.00059 / 3600.0 * T * T +
                 0.001813 / 3600.0 * T * T * T)

    Right_Ascension = math.atan2(math.sin(L_true * dr) * math.cos(Obliquity * dr),
                                 math.cos(L_true * dr))
    Declination = math.asin(math.sin(Obliquity * dr) * math.sin(L_true * dr))

    Hour_Angle = Sidereal_time + lon - (Right_Ascension / dr)
    Elevation = math.asin(math.sin(lat * dr) * math.sin(Declination) +
                          math.cos(lat * dr) * math.cos(Declination) *
                          math.cos(Hour_Angle * dr)) / dr

    Z = 90.0 - Elevation
    return Z, R


def bird_model(So, lon, lat, elevation, month, day, year,
               hour, minute, second, p_station, albedo,
               O3, H2O, AOT500, AOT380):
    """
    Bird & Hulstrom Solar Irradiance Model (1981)
    """

    # Julian date
    JD = get_julian_date(month, day, year, hour, minute, second)

    # Station pressure
    p = station_pressure(p_station, elevation)

    # Solar position
    Z, R = get_solar_position(JD, lon, lat)

    dr = math.pi / 180.0
    Z_rad = Z * dr

    # Relative air mass
    AM = 1.0 / (math.cos(Z_rad) + 0.15 * pow(93.885 - Z, -1.25))
    AMp = AM * p / 1013.0

    # Rayleigh
    Tr = math.exp(-0.0903 * pow(AMp, 0.84) * (1.0 + AMp - pow(AMp, 1.01)))

    # Ozone
    Ozm = O3 * AM
    Toz = (1.0 - 0.1611 * Ozm * pow(1.0 + 139.48 * Ozm, -0.3035) -
           0.002715 * Ozm / (1.0 + 0.044 * Ozm + 0.0003 * Ozm * Ozm))

    # Mixed gases
    Tm = math.exp(-0.0127 * pow(AMp, 0.26))

    # Water vapor
    Wm = AM * H2O
    Tw = 1.0 - 2.4959 * Wm / ((1.0 + pow(79.034 * Wm, 0.6828)) + 6.385 * Wm)

    # Aerosols
    Tau = 0.2758 * AOT380 + 0.35 * AOT500
    Ta = math.exp((-pow(Tau, 0.873)) * (1.0 + Tau - pow(Tau, 0.7088)) * pow(AM, 0.9108))
    TAA = 1.0 - 0.1 * (1.0 - AM + pow(AM, 1.06)) * (1.0 - Ta)
    TAs = Ta / TAA
    Rs = 0.0685 + (1.0 - 0.84) * (1.0 - TAs)

    # Earth-Sun distance correction
    Rsq = 1.0 / (R * R)

    # Direct irradiance
    Id = Rsq * So * 0.9662 * Tr * Toz * Tm * Tw * Ta
    Idh = Id * math.cos(Z_rad)

    # Diffuse irradiance
    Ias = 0.79 * So * math.cos(Z_rad) * Toz * Tm * Tw * TAA
    Ias = Ias * (0.5 * (1.0 - Tr) + 0.85 * (1.0 - TAs)) / (1.0 - AM + pow(AM, 1.02))

    # Total irradiance
    Itot = (Idh + Ias) / (1.0 - albedo * Rs)
    Idif = Itot - Idh

    return {
        "JD": JD,
        "p": p,
        "R": R,
        "Z": Z,
        "air_mass": AM,
        "S_corrected": Rsq * So,
        "direct": Idh,
        "diffuse": Idif,
        "total": Itot
    }


# --- Örnek kullanım ---
if __name__ == "__main__":
    result = bird_model(
        So=1367,
        lon=-75,
        lat=40,
        elevation=120,
        month=6,
        day=21,
        year=2007,
        hour=17,
        minute=0,
        second=0,
        p_station=1012,
        albedo=0.2,
        O3=0.3,
        H2O=1.5,
        AOT500=0.10,
        AOT380=0.15
    )

    for k, v in result.items():
        print(f"{k}: {v}")
