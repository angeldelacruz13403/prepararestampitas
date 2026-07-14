from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import CategoryForm, GalleryImageForm
from app.models import ContactMessage, GalleryCategory, GalleryImage, Settings, User
from app.services.audit_service import log_admin_action
from app.services.image_service import save_and_optimize_image
from app.utils.decorators import roles_required


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@login_required
@roles_required("Admin", "Editor")
def dashboard():
    stats = {
        "users": User.query.count(),
        "categories": GalleryCategory.query.count(),
        "images": GalleryImage.query.count(),
        "messages": ContactMessage.query.filter_by(is_read=False).count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/categories", methods=["GET", "POST"])
@login_required
@roles_required("Admin", "Editor")
def categories():
    form = CategoryForm()
    records = GalleryCategory.query.order_by(GalleryCategory.name.asc()).all()

    if form.validate_on_submit():
        item = GalleryCategory(
            name=form.name.data.strip(),
            slug=form.slug.data.strip().lower(),
            description=form.description.data,
            is_active=form.is_active.data,
        )
        db.session.add(item)
        db.session.commit()
        log_admin_action(current_user.id, "create_category", item.slug)
        flash("Categoría creada.", "success")
        return redirect(url_for("admin.categories"))

    return render_template("admin/categories.html", form=form, records=records)


@admin_bp.route("/gallery", methods=["GET", "POST"])
@login_required
@roles_required("Admin", "Editor")
def gallery():
    form = GalleryImageForm()
    form.category_id.choices = [(c.id, c.name) for c in GalleryCategory.query.order_by(GalleryCategory.name.asc()).all()]

    if form.validate_on_submit() and form.image.data:
        original_name, webp_name = save_and_optimize_image(
            upload_dir=current_app.config["UPLOAD_FOLDER"],
            file=form.image.data,
        )
        image = GalleryImage(
            category_id=form.category_id.data,
            title=form.title.data.strip(),
            description=form.description.data,
            filename=original_name,
            webp_filename=webp_name,
            alt_text=form.alt_text.data,
            is_public=form.is_public.data,
            is_featured=form.is_featured.data,
        )
        db.session.add(image)
        db.session.commit()
        log_admin_action(current_user.id, "upload_image", image.title)
        flash("Imagen subida correctamente.", "success")
        return redirect(url_for("admin.gallery"))

    images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).limit(100).all()
    return render_template("admin/gallery.html", form=form, images=images)


@admin_bp.route("/users")
@login_required
@roles_required("Admin")
def users():
    records = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", records=records)


@admin_bp.route("/messages")
@login_required
@roles_required("Admin", "Editor")
def messages():
    records = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("admin/messages.html", records=records)


@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@roles_required("Admin")
def settings():
    record = Settings.query.first()
    if not record:
        record = Settings()
        db.session.add(record)
        db.session.commit()

    if request.method == "POST":
        record.site_name = request.form.get("site_name", record.site_name).strip()
        record.site_description = request.form.get("site_description", record.site_description).strip()
        record.contact_email = request.form.get("contact_email", record.contact_email)
        db.session.commit()
        log_admin_action(current_user.id, "update_settings")
        flash("Ajustes guardados.", "success")
        return redirect(url_for("admin.settings"))

    return render_template("admin/settings.html", record=record)


@admin_bp.route("/stats")
@login_required
@roles_required("Admin", "Editor")
def stats():
    stats_data = {
        "total_images": GalleryImage.query.count(),
        "featured_images": GalleryImage.query.filter_by(is_featured=True).count(),
        "public_images": GalleryImage.query.filter_by(is_public=True).count(),
    }
    return render_template("admin/stats.html", stats=stats_data)
