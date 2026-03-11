import ast
import filecmp
import os
import shutil

import frappe


def update_patches():
	"""
	Route exported fixture files marked with a "patch" key to the corresponding
	patch data directory. Fixtures stay in hooks.py permanently.

	- If the exported file differs from the existing patch data file (or is new),
	  it is moved to the patch data directory.
	- If the exported file is identical to the existing one, it is simply removed.

	Usage:
	    1. Add fixture with "patch" key in hooks.py (leave it there permanently):
	           {"dt": "Member Status", "patch": "v1_0"}
	    2. Run: bench export-fixtures
	    3. Run: bench execute church.utils.update_patches

	Ordering:
	    Use the "order" key to control insertion order in the patch data directory.
	    Files are prefixed with a zero-padded number (e.g. 01_, 02_) so that
	    insert_data.py processes them in the correct dependency order.

	        {"dt": "Form Tour", "patch": "v1_0", "order": 1}
	        -> 01_form_tour.json

	    Fixtures without "order" keep their default name and sort alphabetically
	    after any numbered files. Multiple fixtures can share the same order value
	    if their relative order doesn't matter.
	"""
	app_dir = os.path.dirname(__file__)
	hooks_path = os.path.join(app_dir, "hooks.py")
	fixtures_dir = os.path.join(app_dir, "fixtures")
	patches_dir = os.path.join(app_dir, "patches")

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

	for fixture in patch_fixtures:
		dt = fixture["dt"]
		patch_name = fixture["patch"]
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

		if os.path.exists(dest) and filecmp.cmp(src, dest, shallow=False):
			os.remove(src)
			print(f"  Unchanged: {dest_filename} (removed fixture copy)")
			unchanged += 1
		else:
			os.makedirs(dest_dir, exist_ok=True)
			shutil.move(src, dest)
			print(f"  Updated: {filename}.json -> patches/{patch_name}/data/{dest_filename}")
			moved += 1

	print(f"\nDone: {moved} moved, {unchanged} unchanged, {skipped} skipped")


def _find_fixtures(source):
	"""Parse hooks.py and return the fixtures list."""
	tree = ast.parse(source)
	for node in ast.walk(tree):
		if isinstance(node, ast.Assign):
			for target in node.targets:
				if isinstance(target, ast.Name) and target.id == "fixtures":
					return ast.literal_eval(ast.get_source_segment(source, node.value))
	return None
