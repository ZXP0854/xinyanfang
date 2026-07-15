"""
Update existing Resource.description values from resource_descriptions.py.

Usage:
  cd backend
  python update_resource_descriptions.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Resource
from resource_descriptions import get_resource_description


app = create_app(os.environ.get("FLASK_ENV", "development"))


with app.app_context():
    resources = Resource.query.all()
    updated = 0
    missing = []

    for resource in resources:
        description = get_resource_description(resource.module, resource.name)
        if description is None:
            missing.append(f"{resource.module} / {resource.name}")
            continue
        if resource.description != description:
            resource.description = description
            updated += 1

    db.session.commit()

    print(f"[OK] Updated {updated} resource descriptions")
    if missing:
        print("[WARN] No matching Excel description for:")
        for item in missing:
            print(f"  - {item}")
