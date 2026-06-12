#!/usr/bin/env python3
"""Patch PPTX run and theme fonts for WPS-friendly Chinese rendering."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree


NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def patch_font_elements(root, east_asia_font: str, latin_font: str) -> int:
    changed = 0
    for rpr in root.xpath("//a:rPr", namespaces=NS):
        for tag, typeface in [("latin", latin_font), ("ea", east_asia_font), ("cs", east_asia_font)]:
            child = rpr.find(f"a:{tag}", namespaces=NS)
            if child is None:
                child = etree.SubElement(rpr, f"{{{NS['a']}}}{tag}")
            if child.get("typeface") != typeface:
                child.set("typeface", typeface)
                changed += 1
    return changed


def patch_theme(root, east_asia_font: str, latin_font: str) -> int:
    changed = 0
    for font in root.xpath("//a:fontScheme/a:majorFont/a:latin | //a:fontScheme/a:minorFont/a:latin", namespaces=NS):
        if font.get("typeface") != latin_font:
            font.set("typeface", latin_font)
            changed += 1
    for font in root.xpath(
        "//a:fontScheme/a:majorFont/a:ea | //a:fontScheme/a:minorFont/a:ea | "
        "//a:fontScheme/a:majorFont/a:cs | //a:fontScheme/a:minorFont/a:cs",
        namespaces=NS,
    ):
        if font.get("typeface") != east_asia_font:
            font.set("typeface", east_asia_font)
            changed += 1
    return changed


def patch_pptx(src: Path, out: Path, east_asia_font: str, latin_font: str) -> dict:
    parser = etree.XMLParser(remove_blank_text=False)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        with ZipFile(src) as zin:
            zin.extractall(tmp)

        changed_runs = 0
        changed_theme = 0
        for xml_path in (tmp / "ppt" / "slides").glob("slide*.xml"):
            root = etree.parse(str(xml_path), parser)
            changed = patch_font_elements(root, east_asia_font, latin_font)
            if changed:
                xml_path.write_bytes(etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=False))
                changed_runs += changed

        theme_path = tmp / "ppt" / "theme" / "theme1.xml"
        if theme_path.exists():
            root = etree.parse(str(theme_path), parser)
            changed_theme = patch_theme(root, east_asia_font, latin_font)
            if changed_theme:
                theme_path.write_bytes(etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=False))

        out.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(out, "w", ZIP_DEFLATED) as zout:
            for file in tmp.rglob("*"):
                if file.is_file():
                    zout.write(file, file.relative_to(tmp).as_posix())

    return {
        "pptx": str(out),
        "east_asia_font": east_asia_font,
        "latin_font": latin_font,
        "changed_run_font_slots": changed_runs,
        "changed_theme_slots": changed_theme,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch PPTX fonts for Chinese/WPS compatibility.")
    parser.add_argument("pptx")
    parser.add_argument("--out", help="Output PPTX. Defaults to in-place patch.")
    parser.add_argument("--east-asia-font", default="PingFang SC")
    parser.add_argument("--latin-font", default="Aptos")
    args = parser.parse_args()

    src = Path(args.pptx)
    if args.out:
        out = Path(args.out)
    else:
        backup = src.with_suffix(".before-font-patch.pptx")
        if not backup.exists():
            shutil.copy2(src, backup)
        out = src

    result = patch_pptx(src, out, args.east_asia_font, args.latin_font)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
