from itertools import product
from pathlib import Path


configfile: "config.yaml"

particle = config.get("particle", "mu-")
energies = config.get("energies", [])
thetas = config.get("thetas", [])
events = config.get("events_per_point", 100)
random_seed = config.get("random_seed", 0)
cldconfig_path = config.get("cldconfig_path", "")
geometry_name = config.get("geometry_name", "")
geometry_path = config.get("geometry_path", "")
output_path = Path(config["output_path"]).absolute()

points = []
for e, theta in product(energies, thetas):
    points.append({
        "energy": f"{e}*GeV",
        "theta": f"{theta}*degree",
        "label": f"{particle}_{e}GeV_{theta}deg_{events}N",
    })

LABEL_MAP = {p["label"]: p for p in points}

# SIM_FILES = expand(f"{output_path}/sim/{{label}}.edm4hep.root", label=[p["label"] for p in points])
REC_FILES = expand(f"{output_path}/rec/{{label}}_REC.edm4hep.root", label=[p["label"] for p in points])

rule all:
    input: REC_FILES

rule simulate:
    output:
        f"{output_path}/sim/{{label}}.edm4hep.root"
    params:
        energy=lambda wildcards: LABEL_MAP[wildcards.label]["energy"],
        theta=lambda wildcards: LABEL_MAP[wildcards.label]["theta"],
    shell:
        f"""
ddsim --compactFile {geometry_path}/{geometry_name}/{geometry_name}.xml \
      --outputFile {{output}} \
      --steeringFile {cldconfig_path}/cld_steer.py \
      --numberOfEvents {events} \
      --enableGun \
      --gun.particle={particle} \
      --gun.distribution=uniform  \
      --gun.energy={{params.energy}} \
      --gun.thetaMin={{params.theta}} \
      --gun.thetaMax={{params.theta}} \
      --crossingAngleBoost=0 \
      --random.seed {random_seed}
        """

rule reconstruct:
    input:
        f"{output_path}/sim/{{label}}.edm4hep.root"
    output:
        f"{output_path}/rec/{{label}}_REC.edm4hep.root"
    params:
        base_name=lambda wildcards: f"{output_path}/rec/{wildcards.label}"
    shell:
        f"""
pushd {cldconfig_path}
k4run CLDReconstruction.py -n {events} --inputFiles {{input}} --outputBasename {{params.base_name}}
popd
        """
