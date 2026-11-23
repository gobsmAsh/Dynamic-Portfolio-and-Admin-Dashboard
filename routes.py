@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # Temporary example credentials
        if username == "admin" and password == "admin123":
            return redirect(url_for("admin"))

        else:
            return "Invalid username or password!"

    return render_template("login.html")


from flask import Blueprint, request, redirect, url_for, flash, session

from models import load_data, save_data, get_next_id

routes = Blueprint("routes", __name__)


# READ - Display portfolio
@routes.route("/")
def home():
    data = load_data()

    from flask import render_template
    return render_template("index.html", data=data)


# CREATE - Add project
@routes.route("/admin/projects/add", methods=["POST"])
def add_project():

    if not session.get("admin"):
        return redirect(url_for("routes.login"))

    data = load_data()

    project = {
        "id": get_next_id(data["projects"]),
        "title": request.form.get("title", "").strip(),
        "description": request.form.get("description", "").strip(),
        "technologies": [
            tech.strip()
            for tech in request.form.get("technologies", "").split(",")
            if tech.strip()
        ],
        "image": request.form.get("image", "").strip(),
        "github": request.form.get("github", "").strip(),
        "live_demo": request.form.get("live_demo", "").strip(),
        "featured": request.form.get("featured") == "on"
    }

    if not project["title"]:
        flash("Project title is required.", "error")
        return redirect(url_for("routes.admin"))

    data["projects"].append(project)
    save_data(data)

    flash("Project added successfully!", "success")
    return redirect(url_for("routes.admin"))


# UPDATE - Edit project
@routes.route("/admin/projects/update/<int:project_id>", methods=["POST"])
def update_project(project_id):

    if not session.get("admin"):
        return redirect(url_for("routes.login"))

    data = load_data()

    for project in data["projects"]:
        if project["id"] == project_id:

            project["title"] = request.form.get("title", "").strip()
            project["description"] = request.form.get("description", "").strip()
            project["technologies"] = [
                tech.strip()
                for tech in request.form.get("technologies", "").split(",")
                if tech.strip()
            ]
            project["image"] = request.form.get("image", "").strip()
            project["github"] = request.form.get("github", "").strip()
            project["live_demo"] = request.form.get("live_demo", "").strip()
            project["featured"] = request.form.get("featured") == "on"

            save_data(data)
            flash("Project updated successfully!", "success")
            break
    else:
        flash("Project not found.", "error")

    return redirect(url_for("routes.admin"))


# DELETE - Delete project
@routes.route("/admin/projects/delete/<int:project_id>", methods=["POST"])
def delete_project(project_id):

    if not session.get("admin"):
        return redirect(url_for("routes.login"))

    data = load_data()

    original_count = len(data["projects"])

    data["projects"] = [
        project for project in data["projects"]
        if project["id"] != project_id
    ]

    if len(data["projects"]) == original_count:
        flash("Project not found.", "error")
    else:
        save_data(data)
        flash("Project deleted successfully!", "success")

    return redirect(url_for("routes.admin"))
