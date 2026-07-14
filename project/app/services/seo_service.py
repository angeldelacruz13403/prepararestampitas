from flask import request, url_for


def build_seo_payload(title: str, description: str, image_url: str | None = None) -> dict:
    canonical = request.url
    return {
        "title": title,
        "description": description,
        "canonical": canonical,
        "og": {
            "title": title,
            "description": description,
            "url": canonical,
            "image": image_url or url_for("static", filename="images/og-default.jpg", _external=True),
            "type": "website",
        },
        "twitter": {
            "card": "summary_large_image",
            "title": title,
            "description": description,
            "image": image_url or url_for("static", filename="images/og-default.jpg", _external=True),
        },
        "json_ld": {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Cruz Cofrade",
            "url": request.url_root.rstrip("/"),
        },
    }
