
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)
from functools import wraps
from storage import load_data, save_data, get_next_id

app = Flask(__name__)
app.secret_key = "change-this-to-a-long-random-secret"


# -------------------------
# LOGIN PROTECTION
# -------------------------

def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper


# -------------------------
# PUBLIC PORTFOLIO
# -------------------------

@app.route("/")
def home():
    data = load_data()
    return render_template(
        "index.html",
        profile=data["profile"],
        skills=data["skills"],
        projects=data["projects"],
        achievements=data["achievements"]
    )


# -------------------------
# LOGIN AND LOGOUT
# -------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # Temporary demonstration credentials
        if username == "admin" and password == "admin123":
            session["logged_in"] = True
            return redirect(url_for("admin"))

        flash("Incorrect username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("home"))


# -------------------------
# ADMIN DASHBOARD
# -------------------------

@app.route("/admin")
@login_required
def admin():
    data = load_data()
    return render_template("admin.html", data=data)


# -------------------------
# UPDATE PROFILE
# -------------------------

@app.route("/admin/profile/update", methods=["POST"])
@login_required
def update_profile():
    data = load_data()

    fields = [
        "name", "title", "bio", "email",
        "location", "github", "linkedin", "website"
    ]

    for field in fields:
        data["profile"][field] = request.form.get(field, "").strip()

    save_data(data)
    flash("Profile updated successfully!", "success")
    return redirect(url_for("admin") + "#profile")


# -------------------------
# ADD PROJECT, SKILL OR ACHIEVEMENT
# -------------------------

@app.route("/admin/<section>/add", methods=["POST"])
@login_required
def add_item(section):

    if section not in ["projects", "skills", "achievements"]:
        return "Invalid section", 404

    data = load_data()
    item = request.form.to_dict()

    item["id"] = get_next_id(data[section])

    if section == "projects":
        item["technologies"] = [
            tech.strip()
            for tech in item.get("technologies", "").split(",")
            if tech.strip()
        ]
        item["year"] = int(item["year"]) if item.get("year", "").isdigit() else None
        item["featured"] = item.get("featured") == "on"

    data[section].append(item)
    save_data(data)

    flash("Item added successfully!", "success")
    return redirect(url_for("admin") + "#" + section)


# -------------------------
# UPDATE PROJECT, SKILL OR ACHIEVEMENT
# -------------------------

@app.route("/admin/<section>/<int:item_id>/update", methods=["POST"])
@login_required
def update_item(section, item_id):

    if section not in ["projects", "skills", "achievements"]:
        return "Invalid section", 404

    data = load_data()

    item = next(
        (x for x in data[section] if x["id"] == item_id),
        None
    )

    if item is None:
        return "Item not found", 404

    for key, value in request.form.items():
        if key == "id":
            continue
        if section == "projects" and key == "technologies":
            item[key] = [t.strip() for t in value.split(",") if t.strip()]
        elif section == "projects" and key == "year":
            item[key] = int(value) if value.isdigit() else None
        elif section == "projects" and key == "featured":
            item[key] = value == "on"
        else:
            item[key] = value.strip()

    if section == "projects":
        item["featured"] = request.form.get("featured") == "on"

    save_data(data)
    flash("Item updated successfully!", "success")
    return redirect(url_for("admin") + "#" + section)


# -------------------------
# DELETE PROJECT, SKILL OR ACHIEVEMENT
# -------------------------

@app.route("/admin/<section>/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(section, item_id):

    if section not in ["projects", "skills", "achievements"]:
        return "Invalid section", 404

    data = load_data()

    data[section] = [
        item for item in data[section]
        if item["id"] != item_id
    ]

    save_data(data)
    flash("Item deleted successfully!", "success")
    return redirect(url_for("admin") + "#" + section)


# ---------------- REST API ----------------

from flask import jsonify


# Fields that can be changed in the profile
PROFILE_FIELDS = [
    "name", "title", "bio", "email",
    "location", "github", "linkedin", "website"
]


# Allowed fields for each collection
ITEM_FIELDS = {
    "projects": [
        "title", "description", "technologies",
        "github_url", "demo_url", "image_url",
        "year", "featured"
    ],
    "skills": [
        "name", "category", "proficiency"
    ],
    "achievements": [
        "title", "description", "issuer",
        "date", "credential_url", "image_url"
    ]
}


def prepare_item(section, values):
    """Clean and validate fields received by the API."""

    item = {
        key: value
        for key, value in values.items()
        if key in ITEM_FIELDS[section]
    }

    if section == "projects":
        technologies = item.get("technologies", [])

        if isinstance(technologies, str):
            technologies = [
                tech.strip()
                for tech in technologies.split(",")
                if tech.strip()
            ]

        if not isinstance(technologies, list):
            raise ValueError("Technologies must be a list or comma-separated string.")

        item["technologies"] = technologies

        year = item.get("year")
        if year in ("", None):
            item["year"] = None
        else:
            try:
                item["year"] = int(year)
            except (ValueError, TypeError):
                raise ValueError("Year must be a valid number.")

        if "featured" in item:
            if not isinstance(item["featured"], bool):
                raise ValueError("Featured must be true or false.")

    return item


# GET profile
@app.route("/api/profile", methods=["GET"])
def api_get_profile():
    data = load_data()
    return jsonify(data["profile"]), 200


# UPDATE profile
@app.route("/api/profile", methods=["PUT"])
def api_update_profile():
    values = request.get_json(silent=True)

    if not isinstance(values, dict):
        return jsonify({"error": "Send a valid JSON object."}), 400

    data = load_data()

    for field in PROFILE_FIELDS:
        if field in values:
            data["profile"][field] = str(values[field]).strip()

    save_data(data)

    return jsonify({
        "message": "Profile updated successfully.",
        "profile": data["profile"]
    }), 200


# GET all items OR one item
@app.route("/api/<section>", methods=["GET"])
@app.route("/api/<section>/<int:item_id>", methods=["GET"])
def api_get_items(section, item_id=None):
    if section not in ITEM_FIELDS:
        return jsonify({"error": "Invalid section."}), 404

    data = load_data()
    items = data[section]

    if item_id is None:
        return jsonify(items), 200

    item = next(
        (x for x in items if x["id"] == item_id),
        None
    )

    if item is None:
        return jsonify({"error": "Item not found."}), 404

    return jsonify(item), 200


# ADD an item
@app.route("/api/<section>", methods=["POST"])
def api_add_item(section):
    if section not in ITEM_FIELDS:
        return jsonify({"error": "Invalid section."}), 404

    values = request.get_json(silent=True)

    if not isinstance(values, dict):
        return jsonify({"error": "Send a valid JSON object."}), 400

    data = load_data()

    try:
        item = prepare_item(section, values)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    # Check required fields
    required_fields = (
        ["title", "description"] if section != "skills"
        else ["name"]
    )

    missing = [
        field for field in required_fields
        if not item.get(field)
    ]

    if missing:
        return jsonify({
            "error": "Missing required fields.",
            "fields": missing
        }), 400

    item["id"] = get_next_id(data[section])
    data[section].append(item)

    save_data(data)

    return jsonify({
        "message": "Item added successfully.",
        "item": item
    }), 201


# UPDATE an item
@app.route("/api/<section>/<int:item_id>", methods=["PUT"])
def api_update_item(section, item_id):
    if section not in ITEM_FIELDS:
        return jsonify({"error": "Invalid section."}), 404

    values = request.get_json(silent=True)

    if not isinstance(values, dict):
        return jsonify({"error": "Send a valid JSON object."}), 400

    data = load_data()

    item = next(
        (x for x in data[section] if x["id"] == item_id),
        None
    )

    if item is None:
        return jsonify({"error": "Item not found."}), 404

    try:
        updates = prepare_item(section, values)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    item.update(updates)
    save_data(data)

    return jsonify({
        "message": "Item updated successfully.",
        "item": item
    }), 200


# DELETE an item
@app.route("/api/<section>/<int:item_id>", methods=["DELETE"])
def api_delete_item(section, item_id):
    if section not in ITEM_FIELDS:
        return jsonify({"error": "Invalid section."}), 404

    data = load_data()

    original_count = len(data[section])

    data[section] = [
        item for item in data[section]
        if item["id"] != item_id
    ]

    if len(data[section]) == original_count:
        return jsonify({"error": "Item not found."}), 404

    save_data(data)

    return jsonify({
        "message": "Item deleted successfully."
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
