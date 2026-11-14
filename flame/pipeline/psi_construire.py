# ruff: noqa
# Script dense issu de la phase de préparation : mis en forme par ruff, mais exempté des règles de lint.
"""Build the shared Flame in Freefall dataset from the local PSI mirror.

Input : a folder with PSI-<n>_<name>/ subfolders (Experimental table/, metadata/i_Investigation.txt, Reports/ ...)
        optional all_files.csv produced by psi_telecharger.py (adds a per-file raw data map)
Output: CSV tables + dataset.json + flame_in_freefall.sqlite
Usage : python psi_construire.py <mirror_folder> <output_folder>
Standard library only.
"""

import csv, glob, io, json, os, re, sqlite3, sys

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
PSI_URL = "https://psi.nasa.gov/physci/repo/data/investigations/PSI-%d"
API = "https://psi.nasa.gov/geode-py/ws"

# ---------------------------------------------------------------- curated layer
# family / facility / hardware groups: from the official challenge statement ("Hardware" consideration).
# pillar + priority: team proposal (Hugo's GUIDE_SOURCES.md), to be validated. statement_cited: named in the statement
# as directly tied to fire safety. raw_gb / raw_files / total_files: PSI file listings read on 14 Nov 2026.
# id: (acronym, family, facility, fuel_phase, pillars, statement_cited, priority, related, raw_gb, raw_files, total_files, one_liner)
CUR = {
    26: (
        "BASS",
        "MSG flow duct",
        "Microgravity Science Glovebox (MSG), SPICE fan-driven flow duct",
        "solid",
        "Prevention;Suppression",
        1,
        1,
        "PSI-25;PSI-107",
        163.5,
        173,
        210,
        "Small solid samples (fabric, PMMA) burning in a low-speed wind tunnel; bridges the 1-g NASA-STD-6001 test and real microgravity flammability.",
    ),
    25: (
        "BASS-II",
        "MSG flow duct",
        "Microgravity Science Glovebox (MSG), SPICE fan-driven flow duct",
        "solid",
        "Prevention;Suppression",
        1,
        1,
        "PSI-26",
        274.6,
        685,
        695,
        "Ignition, flame spread and extinction limits of solids vs airflow and oxygen (O2 lowered with nitrogen).",
    ),
    98: (
        "Saffire-I",
        "Saffire (Cygnus)",
        "Saffire enclosure inside a Cygnus cargo vehicle",
        "solid",
        "Prevention",
        1,
        1,
        "PSI-99;PSI-100;PSI-26",
        12.2,
        68,
        76,
        "First large-scale fire in a spacecraft: 41 x 94 cm cotton-fiberglass fabric.",
    ),
    99: (
        "Saffire-II",
        "Saffire (Cygnus)",
        "Saffire enclosure inside a Cygnus cargo vehicle",
        "solid",
        "Prevention",
        1,
        1,
        "PSI-98;PSI-100",
        16.9,
        211,
        217,
        "Nine smaller samples (silicone, fabric, PMMA, Nomex) to compare with the 1-g flammability test.",
    ),
    100: (
        "Saffire-III",
        "Saffire (Cygnus)",
        "Saffire enclosure inside a Cygnus cargo vehicle",
        "solid",
        "Prevention",
        1,
        1,
        "PSI-99;PSI-98",
        35.2,
        75,
        87,
        "Repeat of the large fabric burn at higher airflow (30 cm/s).",
    ),
    102: (
        "SAME",
        "SAME smoke hardware",
        "Microgravity Science Glovebox (MSG), SAME hardware",
        "smoke aerosol (overheated solids)",
        "Detection",
        1,
        1,
        "PSI-101",
        0.0,
        0,
        101,
        "Smoke particle size from overheated spacecraft materials, to design better smoke detectors.",
    ),
    101: (
        "SAME-R",
        "SAME smoke hardware",
        "Microgravity Science Glovebox (MSG), SAME hardware",
        "smoke aerosol (overheated solids)",
        "Detection",
        1,
        1,
        "PSI-102",
        5.7,
        223,
        344,
        "Reflight of SAME with improved diagnostics and more materials.",
    ),
    47: (
        "DAFT / DAFT-2",
        "SAME smoke hardware",
        "ISS cabin, TSI P-Trak particle counter",
        "dust aerosol (no flame)",
        "Detection",
        1,
        1,
        "PSI-102",
        0.0,
        6,
        33,
        "Feasibility test of the particle counter later used by SAME; measured dust, not smoke.",
    ),
    69: (
        "FLEX",
        "MDCA droplet",
        "Combustion Integrated Rack (CIR), Multi-user Droplet Combustion Apparatus (MDCA)",
        "liquid droplet",
        "Suppression",
        1,
        1,
        "PSI-68;PSI-39",
        918.3,
        6424,
        6555,
        "Burning fuel droplets in atmospheres diluted with CO2, helium or nitrogen: flammability limits and suppressant effectiveness.",
    ),
    68: (
        "FLEX-2",
        "MDCA droplet",
        "Combustion Integrated Rack (CIR), Multi-user Droplet Combustion Apparatus (MDCA)",
        "liquid droplet",
        "Suppression",
        0,
        2,
        "PSI-69",
        1220.4,
        10081,
        10156,
        "Extends FLEX to more fuels, pressures (0.5-3 atm), oxygen levels and slow flow.",
    ),
    39: (
        "CFI",
        "MDCA droplet",
        "Combustion Integrated Rack (CIR), Multi-user Droplet Combustion Apparatus (MDCA)",
        "liquid droplet",
        "Prevention",
        0,
        2,
        "PSI-69",
        718.9,
        2771,
        2812,
        "Cool flames on n-dodecane droplets, discovered during FLEX.",
    ),
    20: (
        "ACME BRE",
        "ACME gas burner",
        "Combustion Integrated Rack (CIR), ACME chamber insert",
        "gas (emulates a solid or liquid)",
        "Prevention",
        1,
        1,
        "",
        2035.1,
        2297,
        2361,
        "Gas burner that emulates a burning material in still air: flammability as a function of material properties.",
    ),
    159: (
        "ACME CFI-G",
        "ACME gas burner",
        "Combustion Integrated Rack (CIR), ACME chamber insert",
        "gas",
        "Prevention",
        1,
        2,
        "",
        2085.6,
        3749,
        3756,
        "Spherical cool flames of gases; holds the highest-oxygen microgravity tests (up to 85% O2, inverse flames).",
    ),
    22: (
        "ACME E-FIELD Flames",
        "ACME gas burner",
        "Combustion Integrated Rack (CIR), ACME chamber insert",
        "gas",
        "Prevention",
        1,
        2,
        "PSI-23",
        949.2,
        2502,
        2590,
        "Electric field acting on flame ions; the statement notes it mimics partial gravity.",
    ),
    10: (
        "ACME Flame Design",
        "ACME gas burner",
        "Combustion Integrated Rack (CIR), ACME chamber insert",
        "gas",
        "Fundamental",
        0,
        3,
        "",
        2180.4,
        3792,
        3807,
        "Spherical flames to find soot-free and extinction limits.",
    ),
    21: (
        "ACME CLD Flame",
        "ACME gas burner",
        "Combustion Integrated Rack (CIR), ACME chamber insert",
        "gas",
        "Fundamental",
        0,
        3,
        "",
        2005.5,
        4881,
        4883,
        "Coflow laminar diffusion flames as benchmark data for numerical models.",
    ),
    23: (
        "ACME s-Flame",
        "ACME gas burner",
        "Combustion Integrated Rack (CIR), ACME chamber insert",
        "gas",
        "Fundamental",
        0,
        3,
        "",
        780.8,
        4058,
        4165,
        "Structure and extinction of spherical diffusion flames.",
    ),
    107: (
        "SPICE",
        "MSG flow duct",
        "Microgravity Science Glovebox (MSG), SPICE fan-driven flow duct",
        "gas",
        "Detection",
        0,
        2,
        "PSI-106",
        6.9,
        172,
        188,
        "Smoke point of gas jet flames in coflow: when a flame starts to emit soot.",
    ),
    106: (
        "SLICE",
        "MSG flow duct",
        "Microgravity Science Glovebox (MSG), SPICE fan-driven flow duct",
        "gas",
        "Fundamental",
        0,
        3,
        "PSI-107",
        72.9,
        23461,
        23463,
        "Structure and lift-off of coflow gas flames.",
    ),
    117: (
        "",
        "Ground study (reuses flight data)",
        "Computer simulation",
        "liquid droplet (model)",
        "Suppression",
        0,
        3,
        "PSI-69;PSI-142",
        0.0,
        0,
        16,
        "3-D CFD of cool flames under perturbation, using FLEX data.",
    ),
    142: (
        "",
        "Ground study (reuses flight data)",
        "Laboratory counterflow burner (1 g)",
        "liquid/gas (lab)",
        "Prevention",
        0,
        3,
        "PSI-69",
        0.0,
        0,
        3,
        "Cool-flame transitions near extinction, measured on the ground to interpret FLEX.",
    ),
    62: (
        "",
        "Ground study (reuses flight data)",
        "Computer simulation",
        "solid (model)",
        "Prevention",
        0,
        3,
        "PSI-25;PSI-26",
        0.0,
        0,
        1,
        "Concurrent flame spread model compared with BASS experiments.",
    ),
    60: (
        "",
        "Ground study (reuses flight data)",
        "Image analysis and simulation",
        "gas (model)",
        "Detection",
        0,
        3,
        "PSI-107",
        0.0,
        0,
        1,
        "Analysis of SPICE images: soot on Earth vs in microgravity.",
    ),
    115: (
        "",
        "Ground study (reuses flight data)",
        "Computer simulation",
        "smoke aerosol (model)",
        "Detection",
        0,
        3,
        "PSI-102",
        0.0,
        0,
        47,
        "Simulation of smoke generation using SAME data.",
    ),
}
HARDWARE = [
    (
        "ACME gas burner",
        "Combustion Integrated Rack (CIR)",
        "Six ACME experiments burned gaseous fuels with the same modular ACME hardware in the CIR.",
        "statement",
    ),
    (
        "MDCA droplet",
        "Combustion Integrated Rack (CIR)",
        "FLEX, FLEX-2 and CFI burned liquid fuel droplets with the Multi-user Droplet Combustion Apparatus in the CIR.",
        "statement",
    ),
    (
        "MSG flow duct",
        "Microgravity Science Glovebox (MSG)",
        "BASS, BASS-II, SPICE and SLICE (solid and gaseous fuels) used the modular fan-driven flow duct built for SPICE, inside the MSG.",
        "statement",
    ),
    (
        "Saffire (Cygnus)",
        "Cygnus cargo vehicle",
        "Large-scale burns inside an uncrewed Cygnus after it left the ISS.",
        "PSI",
    ),
    (
        "SAME smoke hardware",
        "MSG / ISS cabin",
        "SAME and SAME-R smoke experiments; one SAME instrument was first used to detect dust in DAFT and DAFT-2.",
        "statement",
    ),
    (
        "Ground study (reuses flight data)",
        "Earth laboratories and computers",
        "Modeling or lab studies that reuse PSI flight data.",
        "PSI",
    ),
]
HABITATS = [
    ("earth_sea_level", "Earth, sea level", 21, 21, 14.7, 14.7, 1.0, "Reference", "statement"),
    (
        "iss",
        "ISS cabin",
        21,
        21,
        14.7,
        14.7,
        0.0,
        "Earth-like air; most PSI tests were run near this condition.",
        "general knowledge, to cite",
    ),
    (
        "spacesuit",
        "Spacesuit (EVA)",
        100,
        100,
        4.3,
        4.3,
        None,
        "100% oxygen at 4.3 psi to keep the suit flexible.",
        "statement",
    ),
    (
        "moon_base",
        "Moon Base",
        30,
        None,
        None,
        10.2,
        0.165,
        "Expected 30% O2 or more at 10.2 psi or less: over 40% more oxygen than Earth air. No partial-gravity data in PSI yet.",
        "statement (gravity value: general knowledge)",
    ),
    (
        "pressurized_rover",
        "Pressurized rover",
        30,
        None,
        None,
        10.2,
        0.165,
        "Same intermediate atmosphere as the Moon Base, to shorten pre-breathing before EVA.",
        "statement (gravity value: general knowledge)",
    ),
    (
        "mars_base",
        "Mars surface base",
        None,
        None,
        None,
        None,
        0.38,
        "Statement names Martian bases as a target habitat but gives no atmosphere values.",
        "statement (gravity value: general knowledge)",
    ),
]
RESOURCES = [
    (
        "data",
        "PSI Data Repository: Combustion Science",
        "https://psi.nasa.gov/physci/repo/search",
        "Source of the data the app must be based on.",
    ),
    (
        "reference",
        "NASA Combustion Science",
        "https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/",
        "Basic information about most combustion investigations.",
    ),
    (
        "reference",
        "A Researcher's Guide to ISS Combustion Science (2015)",
        "https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/",
        "50+ page review of ISS combustion research.",
    ),
    (
        "video",
        "NASA ScienceCasts: The Power of Studying Combustion on the ISS (2018)",
        "https://www.youtube.com/watch?v=W1oXykoz9zg",
        "3.6-minute introduction.",
    ),
    (
        "incident",
        "Apollo 1",
        "https://sma.nasa.gov/sma-disciplines/accllp/apollo-1",
        "1967 pre-launch test fire in an oxygen-filled cabin; crew lost.",
    ),
    (
        "incident",
        "Apollo 13",
        "https://sma.nasa.gov/sma-disciplines/accllp/apollo-13",
        "1970 oxygen tank explosion on the way to the Moon.",
    ),
    (
        "incident",
        "Fire aboard Mir (1997)",
        "https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/",
        "Oxygen generator fire on the Mir space station.",
    ),
    (
        "earth_benefit",
        "Fireman's Air Tanks",
        "https://spinoff.nasa.gov/node/9582",
        "1970s spacesuit technology adapted to firefighter breathing gear.",
    ),
    (
        "earth_benefit",
        "Fire Detector",
        "https://spinoff.nasa.gov/node/9407",
        "1970s shuttle smoke detector that tells smoke from dust; used in mining.",
    ),
    (
        "earth_benefit",
        "New Technology for the Fire Attire",
        "https://spinoff.nasa.gov/node/9918",
        "1980s spacesuit technology applied to firefighter clothing.",
    ),
]


# ---------------------------------------------------------------- helpers
def clean(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def nums(s):
    return [float(x) for x in re.findall(r"(?<![A-Za-z])-?\d+\.?\d*(?:[eE]-?\d+)?", str(s or "").replace(",", " "))]


def rng(s, scale=1.0, lo=None, hi=None):
    v = [x * scale for x in nums(s)]
    if lo is not None:
        v = [x for x in v if x >= lo]
    if hi is not None:
        v = [x for x in v if x <= hi]
    return (round(min(v), 4), round(max(v), 4)) if v else (None, None)


def frac_to_pct(s):
    a, b = rng(s, lo=0, hi=1.0001)
    return (round(a * 100, 2), round(b * 100, 2)) if a is not None else (None, None)


def read_table(path):
    raw = open(path, "rb").read().decode("utf-8-sig", "replace")
    rows = [r for r in csv.reader(io.StringIO(raw)) if any(c.strip() for c in r)]
    hdr = [clean(c) for c in rows[0]]
    return hdr, [dict(zip(hdr, [clean(c) for c in r] + [""] * (len(hdr) - len(r)))) for r in rows[1:]]


def folder(n):
    g = glob.glob(os.path.join(SRC, "PSI-%d_*" % n)) + glob.glob(os.path.join(SRC, "PSI-%d" % n))
    return g[0] if g else None


def isa(n):
    meta = {}
    f = folder(n)
    p = os.path.join(f, "metadata", "i_Investigation.txt") if f else ""
    if os.path.exists(p):
        for row in csv.reader(io.StringIO(open(p, encoding="utf-8").read()), delimiter="\t"):
            if row and any(x.strip() for x in row[1:]):
                meta.setdefault(row[0].strip(), row[1:])
    return meta


# ---------------------------------------------------------------- tests (one row per experiment-table row)
T = []


def add(
    n,
    table,
    level,
    r,
    test_id="",
    date="",
    fuel="",
    form="",
    o2=(None, None),
    p=(None, None),
    flow=(None, None),
    diluent="",
    flow_dir="",
    outcome="",
    burn_time=None,
    n_flames=None,
    notes="",
):
    T.append(
        {
            "investigation_id": "PSI-%d" % n,
            "acronym": CUR[n][0],
            "source_table": table,
            "row_level": level,
            "test_id": test_id,
            "date": date,
            "fuel": fuel,
            "fuel_form": form,
            "o2_pct_min": o2[0],
            "o2_pct_max": o2[1],
            "pressure_atm_min": p[0],
            "pressure_atm_max": p[1],
            "flow_cm_s_min": flow[0],
            "flow_cm_s_max": flow[1],
            "flow_direction": flow_dir,
            "diluent": diluent,
            "outcome": outcome,
            "burn_time_s": burn_time,
            "n_flames": n_flames,
            "notes": notes,
            "raw_data_url": PSI_URL % n,
            "original_row_json": json.dumps(r, ensure_ascii=False),
        }
    )


def one(s):
    v = nums(s)
    return v[0] if v else None


for n in sorted(CUR):
    f = folder(n)
    if not f:
        continue
    for path in sorted(glob.glob(os.path.join(f, "Experimental table", "*.csv"))):
        tb = os.path.basename(path)
        hdr, rows = read_table(path)
        for r in rows:
            g = r.get
            if n == 10 and "Inverse" in tb:
                add(
                    n,
                    tb,
                    "test",
                    r,
                    g("Test"),
                    "",
                    "C2H4 (ethylene) in N2, ambient",
                    "gas, spherical inverse flame",
                    frac_to_pct(g("XO2")),
                    rng(g("pmean (atm)")),
                    diluent="N2",
                    notes="Oxidizer flows from the burner into fuel-laden ambient gas.",
                )
            elif n == 10:
                add(
                    n,
                    tb,
                    "test",
                    r,
                    g("Test"),
                    "",
                    g("Fuel"),
                    "gas, spherical flame",
                    frac_to_pct(g("XO2 (init)")),
                    rng(g("pmean (atm)") or g("pinit (atm)")),
                    diluent="N2",
                )
            elif n == 20:
                add(
                    n,
                    tb,
                    "test day",
                    r,
                    "",
                    "%s %s %s" % (g("Year"), g("Month"), g("Date")),
                    g("Fuel Bottle"),
                    "gas, flat porous burner %s mm" % g("Burner Size (mm)"),
                    tuple(x / 100 if x and x > 100 else x for x in rng(g("Oxygen Conc (percent)"))),
                    n_flames=one(g("Flames Ignited")),
                    diluent="N2",
                    notes=clean(
                        g("Notes")
                        + (
                            " Oxygen value was stored as '%s' in PSI's CSV (percent formatting glitch); divided by 100."
                            % g("Oxygen Conc (percent)")
                            if "00%" in g("Oxygen Conc (percent)")
                            else ""
                        )
                    ),
                )
            elif n == 21:
                add(
                    n,
                    tb,
                    "test day",
                    r,
                    g("Test Day"),
                    "",
                    g("Fuel Bottle"),
                    "gas, coflow jet flame",
                    n_flames=one(g("Flames ignited")),
                    notes=clean(g("Test Type") + ". " + g("Notes")),
                )
            elif n == 22:
                if not g("Test Day"):
                    # continuation line of the PSI table: one more fuel concentration used on the same test day
                    mm = (
                        T
                        and T[-1]["investigation_id"] == "PSI-22"
                        and re.search(r"Fuel conc ([^.]*)\.", T[-1]["notes"])
                    )
                    if g("Fuel Conc") and mm and g("Fuel Conc") not in mm.group(1).split(", "):
                        T[-1]["notes"] = T[-1]["notes"].replace(
                            mm.group(0), "Fuel conc %s, %s." % (mm.group(1), g("Fuel Conc")), 1
                        )
                    continue
                if T and T[-1]["investigation_id"] == "PSI-22" and T[-1]["test_id"] == g("Test Day"):
                    continue  # PSI's table repeats the last test day
                add(
                    n,
                    tb,
                    "test day",
                    r,
                    g("Test Day"),
                    "%s-%s-%s" % (g("Year"), g("Month"), g("Date")),
                    g("Fuel Bottle"),
                    "gas, flame in an electric field (mesh %s)" % g("Mesh Polarity"),
                    n_flames=one(g("Flames Ignited")),
                    notes=clean(g("Test Type") + ". Fuel conc " + g("Fuel Conc") + ". " + g("Notes")),
                )
            elif n == 23:
                at = g("Atmosphere*")
                add(
                    n,
                    tb,
                    "test day",
                    r,
                    g("Test Day*"),
                    "%s %s %s" % (g("Year"), g("Month"), g("Date")),
                    g("Fuel Bottle"),
                    "gas, spherical flame",
                    rng(at.split("O2")[0], lo=1, hi=100),
                    (1.0, 1.0) if at else (None, None),
                    diluent="He" if "He" in at else ("N2" if "N" in at else ""),
                    n_flames=one(g("Flames Ignited*")),
                    notes=clean(g("Test Type") + ". Atmosphere: " + at + ". " + g("Notes")),
                )
            elif n == 25:
                add(
                    n,
                    tb,
                    "test",
                    r,
                    g("Test #"),
                    g("Date"),
                    g("Fuel Sample Material"),
                    "solid",
                    rng(g("Calibrated initial O2 % by vol"), lo=5, hi=100),
                    diluent="N2",
                    notes="PI %s; sample %s; fan display %s (fan setting, not cm/s); final O2 %s%%"
                    % (g("PI"), g("Sample #"), g("Fan display"), g("Calibrated final O2 % by vol")),
                )
            elif n == 26:
                add(
                    n,
                    tb,
                    "test",
                    r,
                    g("Test #"),
                    g("Date"),
                    g("Fuel Sample Material"),
                    "solid",
                    notes="As-run test %s; sample %s. Oxygen and flow are not in this table: see the BASS test matrix in Science Documents."
                    % (g("As Run Test #"), g("Sample #")),
                )
            elif n == 39:
                dil = "He" if (one(g("Helium")) or 0) > 0 else "N2"
                add(
                    n,
                    tb,
                    "test",
                    r,
                    g("Flex Number"),
                    g("Test Date"),
                    g("Fuel"),
                    "liquid droplet" + (", fiber-supported" if g("Fiber").lower().startswith("y") else ", free"),
                    frac_to_pct(g("Oxygen")),
                    rng(g("Pressure")),
                    diluent=dil,
                    notes="CIR id %s; N2 %s; He %s" % (g("CIR"), g("Nitrogen"), g("Helium")),
                )
            elif n == 47:
                add(
                    n,
                    tb,
                    "session",
                    r,
                    g("Session Name"),
                    g("Actual Day"),
                    g("Sample Material"),
                    "dust aerosol (no flame)",
                    notes=clean(g("Hardware Description") + ". " + g("Sampled Location")),
                )
            elif n == 68:
                add(
                    n,
                    tb,
                    "planned condition set",
                    r,
                    "",
                    "",
                    g("Sample (Fuel Type)"),
                    "liquid droplet %s mm" % g("Initial Droplet Diameter (mm)"),
                    frac_to_pct(g("Oxygen Mole Fraction")),
                    rng(g("Ambient Pressure (atm)")),
                    rng(g("Flow Velocity (cm/s)").replace(" - ", " ")),
                    diluent=g("Ambient Gas Mixture"),
                    notes="Test matrix ranges, not individual runs. Ambient %s C." % g("Ambient Temperature (C)"),
                )
            elif n == 69:
                keys = list(r.keys())
                val = lambda frag: next((r[k] for k in keys if k.startswith(frag)), "")
                dl = [
                    nm
                    for nm, k in (("CO2", "CO initial"), ("He", "He initial"), ("N2", "N initial"))
                    if (one(val(k)) or 0) > 0
                ]
                add(
                    n,
                    tb,
                    "test",
                    r,
                    g("FLEX Identifier"),
                    g("Test Date"),
                    g("Fuel"),
                    "liquid droplet %s mm" % val("Droplet initial diameter"),
                    frac_to_pct(val("O initial")),
                    (
                        rng(val("Ambient pressure"), 1 / 760.0)
                        if (one(val("Ambient pressure")) or 0) > 0
                        else (None, None)
                    ),
                    diluent="+".join(dl),
                    outcome=g("Test end"),
                    burn_time=one(val("Burn time")),
                    notes="FLEX test %s; N2 %s, CO2 %s, He %s mole fraction; burning rate %s mm2/s; extinction diameter %s mm. Column headers lost subscripts in PSI's CSV (O = O2, N = N2, CO = CO2)."
                    % (
                        g("FLEX Test #"),
                        val("N initial"),
                        val("CO initial"),
                        val("He initial"),
                        val("Burning rate"),
                        val("Visible flame extinction"),
                    ),
                )
            elif n in (98, 99, 100):
                sid = g("Sample Number")
                # Saffire-II: the Material cell of samples 2-6 and 2-9 is empty in PSI's table (merged cell). Table 1 of
                # "SAFFIRE Objectives, Development and Status.pdf" gives S6 = SIBAL fabric and S9 = flat PMMA.
                filled = (
                    {"2-6": "Cotton-Fiberglass (SIBAL)", "2-9": "PMMA"}.get(sid)
                    if n == 99 and not g("Material")
                    else None
                )
                if filled:
                    r = dict(r, Material=filled)
                    g = r.get
                if not g("Material") or len(sid) > 12 or g("Material").lower().startswith("pre-test"):
                    continue
                o2 = rng(g("Percent O2") or g("Percent O2 (Note 1)"), lo=5, hi=100)
                fl = rng(g("Air Flow (cm/s)") or g("Air Flow"))
                th = g("Sample Thickness (cm)") or g("Samle Thickness") or g("Sample Thickness")
                add(
                    n,
                    tb,
                    "sample",
                    r,
                    sid,
                    "",
                    g("Material"),
                    "solid sheet, %s thick, %s x %s"
                    % (th, g("Sample Length (cm)") or g("Sample Length"), g("Sample Width (cm)") or g("Sample Width")),
                    o2,
                    flow=fl,
                    flow_dir=g("Flow Direction") or g("Direction"),
                    burn_time=one(g("Burn Time (s)")),
                    outcome=g("?-g Burn Length")
                    and "microgravity burn length %s; 1-g burn length %s" % (g("?-g Burn Length"), g("1-g Burn Length"))
                    or "",
                    notes="Cameras %s %s" % (g("Camera 1"), g("Camera 2"))
                    + (
                        "; material cell is empty in PSI's table (merged cell), filled from Table 1 of 'SAFFIRE Objectives, Development and Status.pdf'"
                        if filled
                        else ""
                    ),
                )
            elif n == 101:
                add(
                    n,
                    tb,
                    "test",
                    r,
                    g("SAME Test #"),
                    g("Date"),
                    g("Sample Type"),
                    "smoke from overheated solid",
                    flow=rng(g("Inlet velocity (cm/s)")),
                    notes=clean(
                        g("Description")
                        + ". Duration %s s; net aging %s s" % (g("Duration (sec)"), g("Net aging time (sec)"))
                    ),
                )
            elif n == 102:
                add(
                    n,
                    tb,
                    "sample",
                    r,
                    g("Sample #"),
                    "",
                    g("Sample Material"),
                    "smoke from overheated solid",
                    flow=rng(g("Air Flow (cm/s)")),
                    notes="Weight loss %s mg/min; aging %s min"
                    % (g("Weight loss rate (mg/min)"), g("Aging Duration (minutes)")),
                )
            elif n == 106:
                add(
                    n,
                    tb,
                    "test day",
                    r,
                    "",
                    g("Test Date")[:11],
                    g("Fuel Type"),
                    "gas, coflow jet flame",
                    notes=g("Test Date"),
                )
            elif n == 107:
                add(
                    n,
                    tb,
                    "test",
                    r,
                    "GMT%s %s" % (g("GMT date"), g("GMT ignition")),
                    "GMT day %s" % g("GMT date"),
                    g("Fuel"),
                    "gas jet, nozzle %s mm" % g("Nozzle (mm)"),
                    flow=rng(g("Air Rate (cm/s)")),
                    flow_dir="Coflow",
                    notes="Fuel rate %s mg/s" % g("Fuel Rate (mg/s)"),
                )
            elif n == 142:
                add(
                    n,
                    tb,
                    "published data item",
                    r,
                    g("Data ID"),
                    "",
                    "",
                    "lab counterflow flame (1 g)",
                    notes=clean(
                        g("Data Description")
                        + " | "
                        + g("Reference Publication Link")
                        + " fig "
                        + g("Figure ID in Reference")
                    ),
                )
            elif n == 159:
                inv = "Inverse" in tb
                o2 = frac_to_pct(g("XO2") if inv else g("XO2 before test"))
                cool = g("Cool flame?") or g("TFP")
                add(
                    n,
                    tb,
                    "test",
                    r,
                    g("Test"),
                    "",
                    g("Fuel"),
                    "gas, spherical %s flame" % ("inverse" if inv else "normal"),
                    o2,
                    rng(g("approx p (bar)"), 1 / 1.01325),
                    outcome=clean(
                        "hot ignition: %s; end: %s"
                        % (g("Hot ignition"), g("Self -ext or flow term") or g("Self-ext or flow term"))
                    ),
                    burn_time=one(g("burn time (sec)")),
                    notes=clean(g("Comments")),
                )


# ---------------------------------------------------------------- enrichment from NASA spreadsheets in Science Documents
def air_display(s):
    """BASS / BASS-II 'Air display' = flow speed in the duct in cm/s (BASS-II data FAQ). One test often steps through several speeds."""
    s0 = str(s or "")
    s1 = re.sub(r"\([^)]*\)?", " ", s0)
    s1 = re.split(r"pot", s1, flags=re.I)[0]
    v = [x for x in nums(s1.replace("-", " ")) if 0 <= x <= 60]
    if not v:
        return (None, None)
    lo = 0.0 if re.search(r"ext|zero|low|<", s0, re.I) else min(v)
    return (round(lo, 2), round(max(v), 2))


MEAS = []
import zipfile
import xml.etree.ElementTree as ET


def xlsx_rows(path, sheet):
    """Rows of one sheet of an .xlsx file as tuples (standard library only; formulas give their stored value)."""
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rid = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        shared = [
            "".join(t.text or "" for t in si.iter("{%s}t" % ns["m"]))
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns)
        ]
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    target = next(
        rels[sh.get(rid)]
        for sh in ET.fromstring(z.read("xl/workbook.xml")).find("m:sheets", ns)
        if sh.get("name") == sheet
    )
    target = target.lstrip("/") if target.startswith("/") else "xl/" + target
    out = []
    for row in ET.fromstring(z.read(target)).find("m:sheetData", ns):
        cells = {}
        for c in row:
            col = 0
            for ch in re.match(r"[A-Z]+", c.get("r")).group(0):
                col = col * 26 + ord(ch) - 64
            v = c.find("m:v", ns)
            typ = c.get("t")
            if typ == "inlineStr":
                val = "".join(t.text or "" for t in c.iter("{%s}t" % ns["m"]))
            elif v is None or v.text is None:
                val = None
            elif typ == "s":
                val = shared[int(v.text)]
            elif typ in ("str", "e"):
                val = v.text
            elif typ == "b":
                val = v.text == "1"
            else:
                val = float(v.text)
                val = int(val) if val == int(val) and "." not in v.text and "E" not in v.text.upper() else val
            cells[col] = val
        out.append(tuple(cells.get(i) for i in range(1, max(cells) + 1)) if cells else ())
    return out


for t in T:
    if t["investigation_id"] == "PSI-25":
        r = json.loads(t["original_row_json"])
        a = r.get("Air display", "")
        t["flow_cm_s_min"], t["flow_cm_s_max"] = air_display(a)
        if a:
            t["notes"] += "; air display (cm/s, as logged over the test): %s" % a
if True:
    f = folder(26)
    p = f and os.path.join(f, "Science Documents", "BASS test matrix.xlsx")
    if p and os.path.exists(p):
        rows = xlsx_rows(p, "as run matrix")
        hi = next(i for i, r in enumerate(rows) if r and any(str(c or "").startswith("As run test") for c in r))
        hdr = [clean(str(c or "")) for c in rows[hi]]
        ix = lambda name: next(i for i, h in enumerate(hdr) if h.lower().startswith(name))
        ia, iair, ifan, ign2, irad = (
            ix("as run test"),
            ix("air display"),
            ix("fan display"),
            ix("gn2 pot"),
            ix("radiometer gain"),
        )
        m = {clean(str(r[ia])): r for r in rows[hi + 1 :] if r and r[ia] is not None}
        hit = 0
        for t in T:
            if t["investigation_id"] != "PSI-26":
                continue
            key = clean(json.loads(t["original_row_json"]).get("As Run Test #", ""))
            r = m.get(key)
            if not r:
                continue
            hit += 1
            t["flow_cm_s_min"], t["flow_cm_s_max"] = air_display(r[iair])
            t["diluent"] = "N2 (suppression flow available)"
            t["notes"] = (
                "As-run test %s. From NASA's 'BASS test matrix.xlsx': air display (cm/s) %s; fan display %s; nitrogen (GN2) pot %s. Oxygen was not logged for BASS."
                % (key, r[iair], r[ifan], r[ign2])
            )
        print("BASS rows enriched from as-run matrix: %d" % hit)
    f = folder(39)
    p = f and os.path.join(f, "Science Documents", "CFI_DataSummary_Spreadsheet_Jan2021.xlsx")
    if p and os.path.exists(p):

        def sheet(name):
            rows = xlsx_rows(p, name)
            hdr = [clean(str(c or "")) for c in rows[0]]
            return {str(r[0]).split(".")[0]: dict(zip(hdr, r)) for r in rows[1:] if r and r[0] is not None}

        D, C = sheet("DATA"), sheet("Comments")
        hit = 0
        for t in T:
            if t["investigation_id"] != "PSI-39":
                continue
            d = D.get(t["test_id"])
            c = C.get(t["test_id"])
            if d:
                hit += 1
                bt = d.get("HF Burn Time")
                t["burn_time_s"] = round(bt, 2) if isinstance(bt, (int, float)) else None
                t["outcome"] = (
                    "cool flame observed"
                    if isinstance(d.get("kcool ( mm^2/s )"), (int, float))
                    else "no cool-flame burning rate reported"
                )
                orj = json.loads(t["original_row_json"])
                orj["_from_CFI_DataSummary_DATA_sheet"] = {k: v for k, v in d.items() if k and v is not None}
                t["original_row_json"] = json.dumps(orj, ensure_ascii=False, default=str)
                t["notes"] += (
                    "; D0 %s mm; hot-flame burning rate %s mm2/s; cool-flame burning rate %s mm2/s; hot-flame extinction diameter %s mm"
                    % (
                        d.get("D0 ( mm )"),
                        d.get("khot ( mm^2/s )"),
                        d.get("kcool ( mm^2/s )"),
                        d.get("Dext, hot ( mm )"),
                    )
                )
            if c and c.get("Comments"):
                t["notes"] += "; PI comment: " + clean(str(c["Comments"]))[:400]
        print("CFI rows enriched from data summary: %d" % hit)
SRC_FAQ = "BASS-II data FAQ.docx (PSI-25 Science Documents)"
for nm, what, unit in [
    ("Video display", "Flame video with overlaid fan voltage, airflow and radiometer readings, 5 Hz data rate", ""),
    ("Digital still camera (Nikon)", "Still images of the flame and of the sample after the burn", "frames"),
    ("Duct anemometer ('Air display')", "Flow speed in the duct; slow response (about 1 min)", "cm/s"),
    (
        "Radiometer",
        "Uncalibrated flame radiation: relative intensity and flame dynamics such as pre-extinction oscillations",
        "relative",
    ),
    ("O2 sensor", "Oxygen before and after the test, corrected against the ISS MCA reading", "% by volume"),
    ("CDM sensor", "CO2 before and after the test", "% by volume"),
    ("CSA-CP sensor", "CO before and after the test (over range above 1000 ppm)", "ppm"),
]:
    MEAS.append(
        {
            "investigation_id": "PSI-25",
            "acronym": "BASS-II",
            "instrument": nm,
            "measures": what,
            "unit": unit,
            "source": SRC_FAQ,
        }
    )
SRC_CFI = "CFI_DataSummary_Spreadsheet_Jan2021.xlsx (PSI-39 Science Documents), sheet names and columns"
for nm, what, unit in [
    (
        "Droplet imaging",
        "Initial droplet diameter D0, extinction diameters, burning rates of the hot and cool flame",
        "mm, mm2/s",
    ),
    ("Radiometers", "Peak hot-flame radiation, peak water-vapour radiation and their ratio", "as recorded"),
    (
        "Cameras listed per test (HIBMS, LLL, HIBMS-2, IPSU-4, downlink video)",
        "Which cameras recorded each test, with gain and illumination settings",
        "yes/no",
    ),
    ("Igniter log", "Ignition power and ignition time per test", "W, ms"),
]:
    MEAS.append(
        {
            "investigation_id": "PSI-39",
            "acronym": "CFI",
            "instrument": nm,
            "measures": what,
            "unit": unit,
            "source": SRC_CFI,
        }
    )

# Sensors and measurement types read from NASA's Reports and Science Documents (PDF, docx) in PSI.
# basis: "document" = described in a document of this investigation; "shared hardware" = described for a sister
# investigation that used the same facility; "PSI metadata" = from the investigation's Approach text.
ACR = {n: CUR[n][0] for n in CUR}


def meas(ids, rows, source, basis="document"):
    for n in ids:
        for nm, what, unit in rows:
            MEAS.append(
                {
                    "investigation_id": "PSI-%d" % n,
                    "acronym": ACR[n],
                    "instrument": nm,
                    "measures": what,
                    "unit": unit,
                    "source": source,
                    "basis": basis,
                }
            )


for m_ in MEAS:
    m_.setdefault("basis", "document")
ACME_ALL = [10, 20, 21, 22, 23, 159]
meas(
    ACME_ALL,
    [
        (
            "Mass flow controllers (3, Teledyne Hastings HFC-D-302)",
            "Flow rates of oxidizer (static mixer), nitrogen or inert, and fuel",
            "SLPM",
        ),
        ("Pressure transducers (3)", "Outer coflow, burner and chamber pressure, 0 to 145 psia", "psia"),
        (
            "Thermocouples (rake A-D, two at 200 mm from the axis, burner)",
            "Gas temperature near and far from the flame, burner temperature",
            "deg C",
        ),
        (
            "Radiometers (thermopile array at +60, +30, centre, -30, -60 degrees, plus offset)",
            "Flame radiation",
            "V (thermopile output)",
        ),
        (
            "Photomultiplier tubes (3: 310 nm, broadband, 430 nm)",
            "Flame light emission: OH* band, broadband, CH* band",
            "microamp",
        ),
        ("Non-imaging data file", "All channels above in one CSV per test point, sampled at 125 Hz by default", "csv"),
    ],
    "ACME non-imaging data file description.pdf (Science Documents of PSI-20, PSI-22, PSI-23)",
    "shared hardware",
)
for m_ in MEAS:
    if m_["source"].startswith("ACME non-imaging") and m_["investigation_id"] in ("PSI-20", "PSI-22", "PSI-23"):
        m_["basis"] = "document"
meas(
    [22],
    [
        (
            "Ion current sensor",
            "Ion current between the electric-field mesh and the burner, -25 to 25 microamp",
            "microamp",
        ),
        ("Electric field voltage monitor", "High voltage applied to the mesh, -10 to +10 kV", "V"),
    ],
    "ACME non-imaging data file description.pdf (PSI-22 Science Documents)",
)
meas(
    [20],
    [
        (
            "Heat flux sensors (2, Medtherm, centre and offset)",
            "Heat flux from the flame back to the burner surface (BRE burner only)",
            "mV (1 mV = 1 Btu/ft2 in the document)",
        ),
        ("Burner surface thermocouples (type K)", "Burner surface temperature at centre and offset positions", "deg C"),
    ],
    "ACME non-imaging data file description.pdf (PSI-20 Science Documents)",
)
meas(
    ACME_ALL,
    [
        (
            "Color digital camera (ACME DataCam, 12 bit, 1360x1024, up to 30 fps, filter wheel)",
            "Flame shape and colour; CH* imaging (430 nm filter); soot temperature and soot volume fraction by colour pyrometry; formaldehyde band for cool flames",
            "images",
        ),
        ("Analog operations camera", "Live downlink video for operations, recorded on the ground only", "video"),
        (
            "CIR HiBMs monochrome camera (with illumination package)",
            "Backlit imaging; soot volume fraction by light extinction; 512x512 or 1024x1024 at 30 fps",
            "images",
        ),
        (
            "Thin-filament pyrometry (array of silicon carbide fibres)",
            "Gas temperature profile across the flame, read from fibre glow in camera images",
            "deg C (derived)",
        ),
        (
            "CIR LLL-UV intensified camera",
            "OH* chemiluminescence; used only for s-Flame during ACME operations",
            "images",
        ),
    ],
    "PSI-159_Reports_FinalRpt_ACME.CFI-G.pdf, section on ACME diagnostics (PSI-159 Reports)",
    "shared hardware",
)
for m_ in MEAS:
    if m_["source"].startswith("PSI-159_Reports") and m_["investigation_id"] == "PSI-159":
        m_["basis"] = "document"
meas(
    [159],
    [("CFI intensified camera (IPSU-G)", "Cool-flame chemiluminescence, too dim for the colour camera", "images")],
    "PSI-159_Reports_FinalRpt_ACME.CFI-G.pdf (PSI-159 Reports)",
)
MDCA = [
    (
        "CIR HiBMs backlit cameras",
        "Droplet diameter history, burning rate, soot volume fraction (with tunable filter)",
        "mm, mm2/s",
    ),
    ("CIR LLL-UV camera", "OH* chemiluminescence: flame diameter, flame stand-off, extinction", "images"),
    ("MDCA colour camera", "Colour view of the flame: shape, visible extinction", "video"),
    ("Radiometers (wide band and narrow band)", "Flame radiation history", "as recorded"),
    (
        "Chamber pressure and temperature sensors",
        "Ambient pressure (kept within 10% of initial) and initial gas temperature (18 to 27 deg C)",
        "atm, deg C",
    ),
    ("Acceleration measurement (SAMS)", "Residual acceleration, required below 1e-4 m/s2", "m/s2"),
]
meas([68], MDCA, "FLEX-2 SRD Final.pdf, science data requirements (PSI-68 Science Documents)")
meas(
    [69, 39],
    MDCA[:5],
    "FLEX-2 SRD Final.pdf (PSI-68 Science Documents); FLEX and CFI used the same MDCA/CIR hardware",
    "shared hardware",
)
SMOKE = [
    (
        "TSI P-Trak (condensation particle counter)",
        "Particle number concentration (zeroth moment of the size distribution)",
        "particles/cm3",
    ),
    ("TSI DustTrak (laser light scattering)", "Particle mass concentration (third moment)", "mg/m3"),
]
meas(
    [47],
    SMOKE
    + [
        (
            "Test aerosol and impactor",
            "Arizona Road Dust as reference particles; impactor removes particles above the P-Trak limit (2.5 micron)",
            "",
        )
    ],
    "Exp_13_DAFT_30-Day_Postflight_Report.pdf (PSI-47 Reports)",
)
SAME_ROWS = SMOKE + [
    ("Ionization smoke detector (First Alert)", "First moment of the size distribution (diameter concentration)", "V"),
    (
        "ISS and Shuttle (STS) smoke detectors",
        "Response of the two U.S. flight smoke detectors to each smoke",
        "detector signal",
    ),
    (
        "Thermal precipitator with TEM grids",
        "Particles collected for electron microscopy: size and shape (grids from the first SAME run were contaminated)",
        "TEM images",
    ),
    (
        "Derived from the three moments",
        "Count mean, diameter-of-average-mass and geometric mean diameter of smoke particles",
        "micron",
    ),
]
meas([102], SAME_ROWS, "SAME_Baseline Concept Description Document_001 Rev A.pdf (PSI-102 Science Documents)")
meas(
    [101],
    SAME_ROWS
    + [("MPASS two-moment smoke detector prototype", "Combined number and mass signal to tell smoke types apart", "V")],
    "SAMER_Final 0602 2014.pdf (PSI-101 Reports)",
)
meas(
    [107],
    [
        (
            "Still camera (modified Nikon D100, top window)",
            "Flame images: luminous flame length, smoke point, soot",
            "NEF images",
        ),
        (
            "Video camera (Panasonic WV-CP654) with title overlay",
            "Flame video with air and fuel flow readings overlaid",
            "video",
        ),
        ("Thermopile radiometer (Oriel 71768)", "Flame radiation, 90 degree view of the whole flame", "relative"),
        ("Omni-directional anemometer (TSI 8475)", "Coflow air speed in the duct", "cm/s"),
        ("Mass flow controller (MKS 2179)", "Fuel gas flow rate", "sccm"),
    ],
    "SPICE Final Report 12_2_2012.pdf (PSI-107 Reports)",
)
meas(
    [106],
    [
        (
            "High-resolution still camera with data overlay",
            "Flame images (more than 4,000) with sensor readings overlaid",
            "images",
        ),
        ("Duct flow and temperature sensors", "Coflow air and fuel flow rates, temperature", "as recorded"),
    ],
    "PSI investigation metadata, Approach (PSI-106); SLICE reused the SPICE flow duct",
    "PSI metadata",
)
meas(
    [26],
    [
        ("Duct anemometer", "Air flow speed, 5 to 50 cm/s", "cm/s"),
        ("Nitrogen mass flow controller", "Nitrogen flow through the suppression nozzle, 0 to 500 cc/min", "sccm"),
        ("Radiometer", "Flame radiation output", "relative"),
        (
            "Video and digital still cameras",
            "Colour flame video and still images; video overlay shows nitrogen flow, radiometer and air flow",
            "video, images",
        ),
        (
            "Cabin oxygen (ISS MCA or hand-held CSA-CP)",
            "Oxygen in the cabin or glovebox on each test day; tests restricted to 21% O2 or above; values not in the PSI table",
            "% by volume",
        ),
    ],
    "SRD_BASS.pdf (PSI-26 Science Documents)",
)
meas(
    [98, 99, 100],
    [
        ("Thermocouples at inlet and outlet of the flow duct", "Flow temperature", "deg C"),
        ("Thermocouples embedded in the sample", "Flame temperature", "deg C"),
        ("Plume thermocouple", "Plume temperature", "deg C"),
        ("Radiometers (two facing the front, two the back of the sample)", "Flame radiation", "as recorded"),
        ("Solid-state CO2 sensor (avionics bay)", "CO2 mole fraction", "mole fraction"),
        ("Solid-state O2 sensor (inlet to avionics bay)", "O2 mole fraction", "mole fraction"),
        ("Pressure sensor (avionics bay)", "Pressure", "as recorded"),
        ("Anemometers (one on each side of the sample)", "Flow velocity", "cm/s"),
        (
            "Cameras (two viewing the front of the sample)",
            "Flame images: spread rate, flame size (primary data)",
            "images",
        ),
        ("Smoke wire at the sample leading edge", "Flow uniformity", "images"),
    ],
    "SAFFIRE Objectives, Development and Status.pdf, Table 2 (Science Documents of PSI-98, PSI-99, PSI-100)",
)
meas(
    [60],
    [
        (
            "Colour-ratio pyrometry on SPICE Nikon raw images",
            "Soot temperature fields and soot volume fraction",
            "K, ppm",
        ),
        (
            "Numerical model (flow, species, soot)",
            "Computed soot evolution for normal gravity and microgravity",
            "simulation",
        ),
    ],
    "PSI investigation metadata, Approach (PSI-60)",
    "PSI metadata",
)
meas(
    [62],
    [
        ("Two-colour tomography on BASS and BASS-II camera images", "3D soot and temperature fields", "derived"),
        (
            "Numerical model of concurrent flame spread",
            "Flame geometry, temperature, soot volume fraction, flame spread rate",
            "simulation",
        ),
    ],
    "PSI investigation metadata, Approach (PSI-62)",
    "PSI metadata",
)
meas(
    [115],
    [
        (
            "Direct numerical simulation of smoke particle growth",
            "Particle size distributions in Earth gravity and microgravity, compared with SAME",
            "simulation",
        )
    ],
    "NNX17AF08A_FinalReport.pdf (PSI-115 Reports)",
)
meas(
    [117],
    [
        (
            "3-D CFD model (OpenFOAM) of droplet cool flames",
            "Ignition delay, oscillation frequency and amplitude, stand-off and extinction diameters",
            "simulation",
        )
    ],
    "PSI investigation metadata, Approach (PSI-117)",
    "PSI metadata",
)
meas(
    [142],
    [
        (
            "Numerical models of cool flames",
            "Extinction limits and burning regimes against oxygen concentration and pressure (up to 20 atm)",
            "simulation",
        )
    ],
    "PSI investigation metadata, Approach (PSI-142)",
    "PSI metadata",
)
for t in T:
    if t["investigation_id"] == "PSI-26" and "restricted to" not in t["notes"]:
        t["notes"] += " The science requirements (SRD_BASS.pdf) restricted testing to cabin air at 21% O2 or above."

# ---------------------------------------------------------------- investigations
I, PUB, DOCS, RAW = [], [], [], []
allfiles = {}
af = os.path.join(SRC, "all_files.csv")
if os.path.exists(af):
    for r in csv.DictReader(open(af, encoding="utf-8")):
        allfiles.setdefault(r["accession"], []).append(r)
for n in sorted(CUR):
    c = CUR[n]
    m = isa(n)
    f = folder(n)
    g = lambda *ks: next((clean(" ".join(x for x in m[k] if x.strip())) for k in ks if k in m), "")
    tt = [t for t in T if t["investigation_id"] == "PSI-%d" % n]

    def span(a, b):
        v = [t[a] for t in tt if t[a] is not None] + [t[b] for t in tt if t[b] is not None]
        return (min(v), max(v)) if v else (None, None)

    o2, pr, fl = (
        span("o2_pct_min", "o2_pct_max"),
        span("pressure_atm_min", "pressure_atm_max"),
        span("flow_cm_s_min", "flow_cm_s_max"),
    )
    fuels = sorted({t["fuel"] for t in tt if t["fuel"]})
    tables = sorted(glob.glob(os.path.join(f, "Experimental table", "*.csv"))) if f else []
    cols = []
    for p in tables:
        cols += [h for h in read_table(p)[0] if h not in cols]
    I.append(
        {
            "investigation_id": "PSI-%d" % n,
            "acronym": c[0],
            "title": g("Study Title"),
            "one_liner": c[11],
            "project_type": g("Comment[Project Type]"),
            "flight_platform": g("Comment[Flight Platform]"),
            "start_date": g("Comment[Investigation Start Date]"),
            "end_date": g("Comment[Investigation End Date]"),
            "hardware_family": c[1],
            "facility": c[2],
            "hardware_psi": g("Comment[Experiment Hardware]"),
            "fuel_phase": c[3],
            "fire_safety_pillar": c[4],
            "cited_in_statement_as_fire_safety": c[5],
            "team_priority": c[6],
            "related_investigations": c[7],
            "n_table_rows": len(tt),
            "row_levels": "; ".join(sorted({t["row_level"] for t in tt})),
            "fuels": "; ".join(fuels)[:1500],
            "n_distinct_fuels": len(fuels),
            "o2_pct_min": o2[0],
            "o2_pct_max": o2[1],
            "pressure_atm_min": pr[0],
            "pressure_atm_max": pr[1],
            "flow_cm_s_min": fl[0],
            "flow_cm_s_max": fl[1],
            "recorded_variables": " | ".join(cols),
            "objectives": g("Comment[Objective]", "Comment[Objectives]"),
            "approach": g("Comment[Approach]"),
            "hypothesis": g("Comment[Hypothesis]"),
            "impacts_earth_benefits": g("Comment[Research Impacts]"),
            "n_publications": len([x for x in m.get("Study Publication Title", []) if x.strip()]),
            "doi": g("Comment[DOI]"),
            "license": "CC0-1.0",
            "psi_url": PSI_URL % n,
            "psi_total_files": c[10],
            "raw_data_files": c[9],
            "raw_data_gb": c[8],
        }
    )
    ti, au, do, li = (
        m.get(k, [])
        for k in (
            "Study Publication Title",
            "Study Publication Author List",
            "Study Publication DOI",
            "Comment[Study Publication Link]",
        )
    )
    for i, t in enumerate(ti):
        if t.strip():
            pick = lambda a: clean(a[i]) if i < len(a) else ""
            PUB.append(
                {
                    "investigation_id": "PSI-%d" % n,
                    "acronym": c[0],
                    "title": clean(t),
                    "authors": pick(au),
                    "doi": pick(do),
                    "link": pick(li),
                }
            )
    if f:
        for root, _, files in os.walk(f):
            for fn in sorted(files):
                if fn in ("investigation.json", "files.json"):
                    continue
                p = os.path.join(root, fn)
                DOCS.append(
                    {
                        "investigation_id": "PSI-%d" % n,
                        "acronym": c[0],
                        "category": os.path.basename(root),
                        "file_name": fn,
                        "size_kb": round(os.path.getsize(p) / 1024, 1),
                        "local_path": os.path.relpath(p, SRC).replace(os.sep, "/"),
                        "psi_url": PSI_URL % n,
                    }
                )
    RAW.append(
        {
            "investigation_id": "PSI-%d" % n,
            "acronym": c[0],
            "raw_data_gb": c[8],
            "raw_data_files": c[9],
            "psi_total_files": c[10],
            "where": (PSI_URL % n) + "  -> section 'Data files and documents' -> folder 'Raw Data'",
            "doi": g("Comment[DOI]"),
            "api_file_listing": 'POST %s/files/v2  body {"folder":"","fileType":"study","studyId":"PSI-%d","version":<version from GET %s/repo/investigations/PSI-%d>}'
            % (API, n, API, n),
            "api_download": "GET %s/studies/PSI-%d/download?file=<file name>&version=<file version>&redirect=false  (returns a 1-hour S3 link)"
            % (API, n),
            "bulk_download_note": "Files over 1 GB: PSI web page 'Download Zip' emails links in parts of up to 15 GB."
            if c[8] > 1
            else "",
            "per_file_map": "raw_files.csv" if "PSI-%d" % n in allfiles else "run psi_telecharger.py then rebuild",
        }
    )
RAWF = [
    {
        "investigation_id": a,
        **{k: r.get(k, "") for k in ("category", "subcategory", "key", "name", "bytes", "version")},
        "psi_url": PSI_URL % int(a.split("-")[1]),
    }
    for a, rs in allfiles.items()
    for r in rs
    if r["category"] in ("Raw Data", "Calibration")
]

REL = []
for n in sorted(CUR):
    for x in filter(None, CUR[n][7].split(";")):
        kind = "reuses data from" if CUR[n][1].startswith("Ground") else "related to"
        REL.append(
            {"from_id": "PSI-%d" % n, "to_id": x, "relation": kind, "source": "PSI 'Related Investigations' field"}
        )
REL += [
    {
        "from_id": "PSI-47",
        "to_id": "PSI-102",
        "relation": "shared instrument (smoke detector used for dust)",
        "source": "statement",
    },
    {
        "from_id": "PSI-47",
        "to_id": "PSI-101",
        "relation": "shared instrument (smoke detector used for dust)",
        "source": "statement",
    },
    {
        "from_id": "PSI-22",
        "to_id": "partial gravity",
        "relation": "mimics partial gravity with an electric field",
        "source": "statement",
    },
    {
        "from_id": "PSI-159",
        "to_id": "high oxygen",
        "relation": "highest-oxygen microgravity tests (up to 85% O2)",
        "source": "statement",
    },
    {
        "from_id": "PSI-20",
        "to_id": "materials flammability",
        "relation": "gas burner emulating material flammability in still air",
        "source": "statement",
    },
]

HW = [
    {
        "hardware_family": a,
        "facility": b,
        "description": c,
        "source": d,
        "investigations": "; ".join("PSI-%d %s" % (n, CUR[n][0]) for n in sorted(CUR) if CUR[n][1] == a).strip(),
    }
    for a, b, c, d in HARDWARE
]
HAB = [
    dict(
        zip(
            (
                "habitat_id",
                "name",
                "o2_pct_min",
                "o2_pct_max",
                "pressure_psi_min",
                "pressure_psi_max",
                "gravity_g",
                "note",
                "source",
            ),
            h,
        )
    )
    for h in HABITATS
]
for h in HAB:
    lo = h["o2_pct_min"]
    h["n_tests_at_or_above_o2_min"] = (
        sum(1 for t in T if lo is not None and t["o2_pct_max"] is not None and t["o2_pct_max"] >= lo) if lo else None
    )
    h["investigations_with_such_tests"] = (
        "; ".join(
            sorted(
                {
                    t["investigation_id"] + " " + t["acronym"]
                    for t in T
                    if lo and t["o2_pct_max"] is not None and t["o2_pct_max"] >= lo
                }
            )
        )
        if lo
        else ""
    )
RES = [dict(zip(("kind", "title", "url", "note"), r)) for r in RESOURCES]


# ---------------------------------------------------------------- relevance (habitat x investigation)
# Decision of PA, 14 Nov 2026: the fire-safety pillars (categories) are dropped. One row per habitat and investigation,
# scored on evidence only. Everything is computed from the tables, except `cited_in_statement` (read in the statement).
# habitat_id, label, o2 window (min, max) in %, max pressure in atm, gravity class, atmosphere source
HR = [
    (
        "space_station",
        "Space station (ISS-like cabin)",
        19,
        23,
        None,
        "micro",
        "Earth-like air; statement gives no number",
    ),
    (
        "spacecraft",
        "Spacecraft in transit",
        19,
        23,
        None,
        "micro",
        "ASSUMPTION: Earth-like cabin air; statement gives no number",
    ),
    ("moon_base", "Moon Base", 30, 100, 0.694, "partial", "Statement: 30% O2 or more at 10.2 psi (0.694 atm) or less"),
    (
        "pressurized_rover",
        "Pressurized rover",
        30,
        100,
        0.694,
        "partial",
        "Statement: same intermediate atmosphere as the Moon Base",
    ),
    (
        "mars_base",
        "Mars surface base",
        None,
        None,
        None,
        "partial",
        "Unknown: the statement gives no number for Mars",
    ),
]
RELV = []
for hid, hlabel, olo, ohi, pmax, grav, asrc in HR:
    for n in sorted(CUR):
        iid = "PSI-%d" % n
        tt = [t for t in T if t["investigation_id"] == iid]
        with_o2 = [t for t in tt if t["o2_pct_max"] is not None]
        in_o2 = [t for t in with_o2 if olo is not None and t["o2_pct_max"] >= olo and t["o2_pct_min"] <= ohi]
        in_both = [
            t for t in in_o2 if pmax is not None and t["pressure_atm_min"] is not None and t["pressure_atm_min"] <= pmax
        ]
        low_p = [
            t for t in tt if pmax is not None and t["pressure_atm_min"] is not None and t["pressure_atm_min"] <= pmax
        ]
        ground = CUR[n][1].startswith("Ground")
        if olo is None:
            atm, atxt = 0.0, "atmosphere of this habitat unknown, so no test can be matched to it"
            in_o2 = in_both = []
        elif not with_o2:
            atm, atxt = (0.3 if pmax is None else 0.0), "oxygen not recorded in PSI's table"
        elif pmax is None:
            atm, atxt = (
                (1.0, "%d table rows at %d-%d%% O2" % (len(in_o2), olo, ohi))
                if in_o2
                else (0.0, "no rows at %d-%d%% O2" % (olo, ohi))
            )
        elif in_both:
            atm, atxt = 1.0, "%d rows at >=%d%% O2 and <=%.2f atm" % (len(in_both), olo, pmax)
        elif in_o2:
            atm, atxt = 0.7, "%d rows at >=%d%% O2, none at reduced pressure" % (len(in_o2), olo)
        elif low_p:
            atm, atxt = 0.3, "%d rows at reduced pressure, none at >=%d%% O2" % (len(low_p), olo)
        else:
            atm, atxt = 0.0, "no rows at >=%d%% O2 or reduced pressure" % olo
        if grav == "micro":
            gv, gtxt = (0.5, "ground or model study") if ground else (1.0, "microgravity flight data")
        elif n == 22:
            gv, gtxt = 1.0, "mimics partial gravity with an electric field (statement)"
        elif n == 99:
            gv, gtxt = 0.6, "has both microgravity and 1-g results, which bound partial gravity"
        elif ground:
            gv, gtxt = 0.3, "ground or model study; no partial-gravity data in PSI"
        else:
            gv, gtxt = 0.4, "microgravity only: one bound for partial gravity (no partial-gravity data in PSI)"
        RELV.append(
            {
                "habitat_id": hid,
                "habitat": hlabel,
                "investigation_id": iid,
                "acronym": CUR[n][0] or iid,
                "score": round(60 * atm + 20 * gv + 20 * CUR[n][5]),
                "rank": None,
                "atmosphere_fit": atm,
                "gravity_fit": gv,
                "cited_in_statement": CUR[n][5],
                "n_rows_matching_atmosphere": len(in_both) if pmax is not None else len(in_o2),
                "why": "%s; %s%s" % (atxt, gtxt, "; named in the statement as fire-safety work" if CUR[n][5] else ""),
                "atmosphere_source": asrc,
            }
        )
for hid, *_ in HR:
    grp = sorted([r for r in RELV if r["habitat_id"] == hid], key=lambda r: (-r["score"], r["investigation_id"]))
    for i, r in enumerate(grp):
        r["rank"] = i + 1

TABLES = {
    "investigations": I,
    "tests": T,
    "hardware_families": HW,
    "relations": REL,
    "habitats": HAB,
    "publications": PUB,
    "documents": DOCS,
    "raw_data_map": RAW,
    "resources": RES,
    "relevance": RELV,
    "measurements": MEAS,
}
if RAWF:
    TABLES["raw_files"] = RAWF
db = os.path.join(OUT, "flame_in_freefall.sqlite")
if os.path.exists(db):
    os.remove(db)
con = sqlite3.connect(db)
for name, rows in TABLES.items():
    if not rows:
        continue
    keys = list(rows[0].keys())
    with open(os.path.join(OUT, name + ".csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    con.execute("CREATE TABLE %s (%s)" % (name, ", ".join('"%s"' % k for k in keys)))
    con.executemany(
        "INSERT INTO %s VALUES (%s)" % (name, ",".join("?" * len(keys))), [[r[k] for k in keys] for r in rows]
    )
    print("%-18s %5d rows" % (name, len(rows)))
con.commit()
con.close()
json.dump(
    {k: v for k, v in TABLES.items() if k != "raw_files"},
    open(os.path.join(OUT, "dataset.json"), "w", encoding="utf-8"),
    ensure_ascii=False,
    indent=1,
)
