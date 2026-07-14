from flask import Blueprint, flash, render_template, request
from sqlalchemy import or_

from app.extensions import db
from app.forms import ContactForm
from app.models import ContactMessage, GalleryCategory, GalleryImage, Services
from app.services.seo_service import build_seo_payload
from app.utils.security import get_client_ip, rate_limit


public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    featured = GalleryImage.query.filter_by(is_featured=True, is_public=True).limit(8).all()
    services = Services.query.filter_by(is_active=True).limit(6).all()
    seo = build_seo_payload("Cruz Cofrade | Fotografía de Semana Santa", "Cobertura profesional de hermandades, cultos y procesiones.")
    return render_template("public/home.html", featured=featured, services=services, seo=seo)


@public_bp.route("/gallery")
def gallery():
    page = request.args.get("page", 1, type=int)
    query_text = request.args.get("q", "", type=str).strip()
    category_slug = request.args.get("category", "", type=str).strip()

    query = GalleryImage.query.filter_by(is_public=True)

    if query_text:
        search = f"%{query_text}%"
        query = query.filter(or_(GalleryImage.title.ilike(search), GalleryImage.description.ilike(search)))

    if category_slug:
        query = query.join(GalleryCategory).filter(GalleryCategory.slug == category_slug)

    images = query.order_by(GalleryImage.created_at.desc()).paginate(page=page, per_page=12, error_out=False)
    categories = GalleryCategory.query.filter_by(is_active=True).order_by(GalleryCategory.name.asc()).all()

    seo = build_seo_payload("Galería | Cruz Cofrade", "Galería de fotografía cofrade en alta calidad.")
    return render_template(
        "public/gallery.html",
        images=images,
        categories=categories,
        current_query=query_text,
        current_category=category_slug,
        seo=seo,
    )


@public_bp.route("/services")
def services():
    records = Services.query.filter_by(is_active=True).order_by(Services.title.asc()).all()
    seo = build_seo_payload("Servicios | Cruz Cofrade", "Servicios fotográficos para hermandades y eventos.")
    return render_template("public/services.html", services=records, seo=seo)


@public_bp.route("/about")
def about():
    seo = build_seo_payload("Sobre mí | Cruz Cofrade", "Fotógrafo profesional especializado en Semana Santa.")
    return render_template("public/about.html", seo=seo)


@public_bp.route("/contact", methods=["GET", "POST"])
@rate_limit("contact", max_calls=5, period_seconds=600)
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = ContactMessage(
            name=form.name.data.strip(),
            email=form.email.data.lower().strip(),
            subject=form.subject.data.strip(),
            message=form.message.data.strip(),
            ip_address=get_client_ip(),
        )
        db.session.add(msg)
        db.session.commit()
        flash("Mensaje enviado correctamente.", "success")

    seo = build_seo_payload("Contacto | Cruz Cofrade", "Contacta para reportajes y coberturas de Semana Santa.")
    return render_template("public/contact.html", form=form, seo=seo)


@public_bp.route("/privacy-policy")
def privacy_policy():
    seo = build_seo_payload("Política de privacidad | Cruz Cofrade", "Información de tratamiento de datos personales.")
    return render_template("public/privacy_policy.html", seo=seo)


@public_bp.route("/cookie-policy")
def cookie_policy():
    seo = build_seo_payload("Política de cookies | Cruz Cofrade", "Información sobre uso de cookies.")
    return render_template("public/cookie_policy.html", seo=seo)


@public_bp.app_errorhandler(429)
def too_many_requests(_error):
    return render_template("errors/429.html"), 429
