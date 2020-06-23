import csv
import json
import logging
import os
import sys
import urllib.parse
from difflib import get_close_matches
from operator import itemgetter
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
current_dir = Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve().parent
gitrepo_dir = (current_dir / "..").resolve()

Project = Dict[str, Any]

# SEE https://shields.io/
BASE_URL = "{baseurl}/study/{prj_id}"
# fixed color badge
BADGE = "![badge](https://img.shields.io/badge/open-{name}-{color})"
# color shows online/offline
BADGE = "![{name}](https://img.shields.io/website?down_message=offline&label={name}&up_message=run&url={baseurl})"

deploys_config = {
    "master": {
        "color": "lightgrey",
        "baseurl": "https://osparc01.speag.com",
        "name": "master.dev",
    },
    "staging": {
        "color": "blue",
        "baseurl": "https://staging.osparc.io",
        "name": "staging",
    },
    "production": {
        "color": "red",
        "baseurl": "https://osparc.io",
        "name": "osparc.io",
    },
}


def load_projects_from_csv(csvfile: Path) -> List[Project]:
    projects = []
    with csvfile.open(mode="r", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for prj in reader:
            prj.pop("id")
            # normalize json
            prj["workbench"] = json.loads(prj["workbench"])
            # normalizes name
            prj["name"] = (
                prj["name"]
                .replace("[ISAN]", "")
                .replace("ISAN", "")
                .replace(":", "")
                .replace("-", " ")
                .strip()
                .capitalize()
            )
            projects.append(prj)
    return projects


def write_jsons(projects: List[Project]) -> List[Path]:
    paths = []
    for prj in projects:
        prjfile = gitrepo_dir / prj["name"] / "project.json"
        logger.info("Writing %s ...", prjfile)
        os.makedirs(prjfile.parent, exist_ok=True)
        prjfile.write_text(json.dumps(prj, indent=2))
        paths.append(prjfile)
    return paths


def load_projects_in_repo() -> List[Project]:
    # all project file
    projects = []
    for base, dirs, filenames in os.walk(gitrepo_dir):
        for name in filenames:
            if name == "project.json":
                path = Path(base) / name
                project = json.loads(path.read_text())

                # add path
                project["path"] = Path(path)
                projects.append(project)
        dirs[:] = [d for d in dirs if not d.startswith(".")]
    projects = sorted(projects, key=itemgetter("name"))
    return projects


def write_readme(projects: List[Project]):
    for prj in projects:
        with (prj["path"].parent / "README.md").open("wt") as fh:
            print("#", prj["name"], file=fh)

            for _, cfg in deploys_config.items():
                # badge = BADGE.format(
                #     name=urllib.parse.quote(cfg["name"]), color=cfg["color"]
                # )

                badge = BADGE.format(
                    **{key: urllib.parse.quote(cfg[key]) for key in ["baseurl", "name"]}
                )

                link = BASE_URL.format(baseurl=cfg["baseurl"], prj_id=prj["uuid"])
                print(f"[{badge}]({link})", file=fh)

            print("", file=fh)
            if prj.get("thumbnail"):
                print(f"![Project Thumbnail]({prj['thumbnail']})", file=fh)
                print("", file=fh)
            print(prj["description"], file=fh)


def write_summary(projects: List[Project]):
    with open("summary.md", "wt") as fh:
        print("# Studies available [%2d]" % len(projects), file=fh)
        print("", file=fh)

        for _, cfg in deploys_config.items():
            print("##", cfg["name"], file=fh)
            for prj in projects:
                url = BASE_URL.format(baseurl=cfg["baseurl"], prj_id=prj["uuid"])
                print(f"1. [{prj['name']}]({url})", file=fh)
            print("", file=fh)


def match_projects(production_projects: List[Project]) -> Path:

    staging_projects = load_projects_from_csv(current_dir / "staging-published.csv")
    master_projects = load_projects_from_csv(current_dir / "master-published.csv")

    for prefix, collection in [
        ("production", production_projects),
        ("staging", staging_projects),
        ("master", master_projects),
    ]:
        print(f"Number of projects in {prefix}:", len(collection))

    stg = {p["name"]: p for p in staging_projects}
    mst = {p["name"]: p for p in master_projects}

    prod_map = {"staging": {}, "master": {}}
    for prj in production_projects:
        name = prj["name"]
        for deploy in prod_map:

            other_prjs = {"staging": stg, "master": mst}[deploy]

            similar = get_close_matches(name, other_prjs.keys(), cutoff=0.5)

            if similar:
                pname = similar[0]
                prod_map[deploy][name] = {
                    "uuid": other_prjs[pname]["uuid"],
                    "name": pname,
                }
            else:
                logger.error("Cannot find match for %s in %s", name, deploy)

    (current_dir / "production_map.json").write_text(json.dumps(prod_map, indent=2))
    return current_dir / "production_map.json"


def main():

    db_projects = load_projects_from_csv(current_dir / "production-published.csv")
    ## match_projects(db_projects)

    write_jsons(db_projects)

    projects = load_projects_in_repo()
    write_readme(projects)
    ## write_summary(projects)


if __name__ == "__main__":
    main()
