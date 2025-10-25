#!/usr/bin/env python3
# /// script
# dependencies = ["jinja2"]
# ///
"""Validate Jinja2 templates in workflow registry."""

import json
import sys
from jinja2 import Template, TemplateSyntaxError
from pathlib import Path

def main():
    registry_path = Path(__file__).parent.parent.parent / "state" / "workflows.json"

    with open(registry_path) as f:
        registry = json.load(f)

    errors = []
    for wf_id, workflow in registry['workflows'].items():
        try:
            template = Template(workflow['prompt_template'])
            print(f'✅ {wf_id}: Template syntax valid')
        except TemplateSyntaxError as e:
            errors.append(f'{wf_id}: {e}')
            print(f'❌ {wf_id}: Template error: {e}')

    if errors:
        print(f'\n❌ {len(errors)} template(s) failed validation')
        sys.exit(1)
    else:
        print('\n✅ All templates validated')

if __name__ == '__main__':
    main()
