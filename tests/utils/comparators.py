import re


def compare_command_output(expected_output: str, actual_output: str, input_image_path: str) -> bool:
    # Replace anchor {input_image_path} with a real value
    expected_output = expected_output.replace('{input_image_path}', input_image_path)
    # Split outputs into separate lines
    expected_lines = expected_output.strip().split('\n')
    actual_lines = actual_output.strip().split('\n')
    if len(expected_lines) != len(actual_lines):
        print(f"Line count mismatch: expected {len(expected_lines)}, got {len(actual_lines)}")
        return False
    # Compare each string
    for expected_line, actual_line in zip(expected_lines, actual_lines):
        if '{result_image_link}' in expected_line:
            # Replace anchor {result_image_link} with a regular expression pattern to match any https URL with jpeg image
            expected_line = re.escape(expected_line).replace(r'\{result_image_link\}', r'https://[^\s]+\.jpeg')
            if not re.match(str(expected_line), actual_line):
                print(f"Mismatch:\nExpected (regex): {expected_line}\nActual: {actual_line}")
                return False
        else:
            if expected_line != actual_line:
                print(f"Mismatch:\nExpected: {expected_line}\nActual: {actual_line}")
                return False
    return True
