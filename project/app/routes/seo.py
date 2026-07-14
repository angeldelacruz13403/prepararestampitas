from flask import Blueprint, Response, current_app, render_template_string, url_for

from app.models import GalleryImage


seo_bp = Blueprint("seo", __name__)


@seo_bp.route("/robots.txt")
def robots():
    text = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            f"Sitemap: {url_for('seo.sitemap', _external=True)}",
        ]
    )
    return Response(text, mimetype="text/plain")


@seo_bp.route("/sitemap.xml")
def sitemap():
    static_routes = [
        "public.home",
        "public.gallery",
        "public.services",
        "public.about",
        "public.contact",
        "public.privacy_policy",
        "public.cookie_policy",
    ]
    urls = [url_for(route, _external=True) for route in static_routes]

    for image in GalleryImage.query.filter_by(is_public=True).all():
        urls.append(url_for("public.gallery", _external=True) + f"?image={image.id}")

    xml_template = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">{% for u in urls %}
  <url><loc>{{ u }}</loc></url>{% endfor %}
</urlset>"""
    return Response(render_template_string(xml_template, urls=urls), mimetype="application/xml")
