import re

with open("scripts/run_daily_scan.py", "r") as f:
    content = f.read()

# Extract the f-string block
match = re.search(r'f"""(.*?)"""', content, re.DOTALL)
if match:
    runner_code = match.group(1)

    # Process the extracted code
    # Unescape braces
    runner_code = runner_code.replace("{{", "{").replace("}}", "}")
    # Fix newlines and tabs
    runner_code = runner_code.replace("\\n", "\n").replace("\\t", "\t")
    # Fix the target_dir injection
    runner_code = runner_code.replace("r'{target_dir}'", "{{TARGET_DIR}}")

    # Create the top-level constant string
    constant_decl = 'RUNNER_CODE_TEMPLATE = """' + runner_code + '"""\n\n'

    # Insert it after the imports
    import_end_idx = content.find("def load_state")
    new_content = content[:import_end_idx] + constant_decl + content[import_end_idx:]

    # Replace the old f-string block
    old_fstring_block = 'f"""' + match.group(1) + '"""'
    new_content = new_content.replace(old_fstring_block, "RUNNER_CODE_TEMPLATE.replace('{{TARGET_DIR}}', json.dumps(target_dir))")

    with open("scripts/run_daily_scan.py", "w") as f:
        f.write(new_content)
    print("Refactoring successful")
else:
    print("Could not find f-string block")
