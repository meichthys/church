import ast
import json
import os
import shutil

import frappe
from frappe.utils.fixtures import export_fixtures as _frappe_export_fixtures

_IGNORE_FIELDS = {"modified"}

AFTER_INSTALL_PATCH = "after_install"
_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "patches", "_template")


def export_fixtures():
	"""
	Export all app fixtures and route any patch fixture files to their patch data directory.
	This replaces running `bench export-fixtures` directly — always use this instead.

	Patch fixtures (those with a "patch" key in hooks.py) are moved out of fixtures/ and
	into their patch data directory after export. Regular fixtures remain in fixtures/.

	- If the exported file differs from the existing patch data file (or is new),
	  it is moved to the patch data directory.
	- If the exported file is identical (ignoring the "modified" field), it is removed.
	- For versioned patches (any patch name other than "after_install"), __init__.py,
	  insert_data.py, and the patches.txt entry are scaffolded automatically if missing.

	Usage:
	    1. Add fixture with "patch" key in hooks.py (leave it there permanently):
	           {"dt": "Member Status", "patch": "after_install"}
	    2. Run: bench execute church.utils.export_fixtures

	    For versioned patches (to push data to existing sites), use a patch name
	    other than "after_install" (e.g. "v2_0"). The script will automatically
	    scaffold __init__.py, insert_data.py, and the patches.txt entry.

	Ordering:
	    Use the "order" key to control insertion order in the patch data directory.
	    Files are prefixed with a zero-padded number (e.g. 01_, 02_) so that
	    insert_data.py processes them in the correct dependency order.

	        {"dt": "Form Tour", "patch": "after_install", "order": 1}
	        -> 01_form_tour.json

	    Fixtures without "order" keep their default name and sort alphabetically
	    after any numbered files. Multiple fixtures can share the same order value
	    if their relative order doesn't matter.
	"""
	_frappe_export_fixtures(app="church")

	app_dir = os.path.dirname(__file__)
	hooks_path = os.path.join(app_dir, "hooks.py")
	fixtures_dir = os.path.join(app_dir, "fixtures")
	patches_dir = os.path.join(app_dir, "patches")
	patches_txt = os.path.join(app_dir, "patches.txt")

	with open(hooks_path) as f:
		hooks_source = f.read()

	fixtures = _find_fixtures(hooks_source)
	if not fixtures:
		print("No fixtures found in hooks.py")
		return

	patch_fixtures = [f for f in fixtures if f.get("patch")]
	if not patch_fixtures:
		print("No patch fixtures found in hooks.py")
		return

	moved = 0
	unchanged = 0
	skipped = 0
	patch_names = set()

	for fixture in patch_fixtures:
		dt = fixture["dt"]
		patch_name = fixture["patch"]
		patch_names.add(patch_name)
		filename = frappe.scrub(dt)
		src = os.path.join(fixtures_dir, filename + ".json")
		order = fixture.get("order")
		dest_filename = f"{order:02d}_{filename}.json" if order else f"{filename}.json"
		dest_dir = os.path.join(patches_dir, patch_name, "data")
		dest = os.path.join(dest_dir, dest_filename)

		if not os.path.exists(src):
			print(f"  Skipped: {filename}.json (not found in fixtures/)")
			skipped += 1
			continue

		if os.path.exists(dest) and _json_equal(src, dest):
			os.remove(src)
			print(f"  Unchanged: {dest_filename} (removed fixture copy)")
			unchanged += 1
		else:
			os.makedirs(dest_dir, exist_ok=True)
			shutil.move(src, dest)
			print(f"  Updated: {filename}.json -> patches/{patch_name}/data/{dest_filename}")
			moved += 1

	print(f"\nDone: {moved} moved, {unchanged} unchanged, {skipped} skipped")

	versioned = patch_names - {AFTER_INSTALL_PATCH}
	if versioned:
		_scaffold_versioned_patches(patches_dir, patches_txt, versioned)


def _scaffold_versioned_patches(patches_dir, patches_txt, patch_names):
	"""Scaffold __init__.py, insert_data.py, and patches.txt entry for new versioned patches."""
	with open(patches_txt) as f:
		patches_content = f.read()

	for patch_name in sorted(patch_names):
		patch_dir = os.path.join(patches_dir, patch_name)
		os.makedirs(patch_dir, exist_ok=True)

		for filename in ("__init__.py", "insert_data.py"):
			dest = os.path.join(patch_dir, filename)
			if not os.path.exists(dest):
				shutil.copy(os.path.join(_TEMPLATE_DIR, filename), dest)
				print(f"  Scaffolded: patches/{patch_name}/{filename}")

		patch_entry = f"church.patches.{patch_name}.execute"
		if patch_entry not in patches_content:
			with open(patches_txt, "a") as f:
				f.write(f"{patch_entry}\n")
			print(f"  Registered: {patch_entry} in patches.txt")
			patches_content += patch_entry


def _json_equal(path_a, path_b):
	"""Compare two fixture JSON files, ignoring fields that change on every export."""
	with open(path_a) as f:
		a = json.load(f)
	with open(path_b) as f:
		b = json.load(f)

	def strip(records):
		return [{k: v for k, v in r.items() if k not in _IGNORE_FIELDS} for r in records]

	return strip(a) == strip(b)


def _find_fixtures(source):
	"""Parse hooks.py and return the fixtures list."""
	tree = ast.parse(source)
	for node in ast.walk(tree):
		if isinstance(node, ast.Assign):
			for target in node.targets:
				if isinstance(target, ast.Name) and target.id == "fixtures":
					return ast.literal_eval(ast.get_source_segment(source, node.value))
	return None
