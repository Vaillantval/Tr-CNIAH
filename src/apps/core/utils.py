# src/apps/core/utils.py
"""Génération PDF des certificats CNIAH via reportlab."""

import io
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# Couleurs CNIAH
_NAVY = colors.HexColor('#0a1931')
_GOLD = colors.HexColor('#c9a84c')
_LIGHT_GOLD = colors.HexColor('#f0e6c8')
_LIGHT_GRAY = colors.HexColor('#f8f8f8')


def _draw_certificate_border(c, w, h):
    """Cadre décoratif à double trait et coins ornementaux."""
    margin = 12 * mm
    inner = 17 * mm

    # Trait extérieur
    c.setStrokeColor(_NAVY)
    c.setLineWidth(2.5)
    c.rect(margin, margin, w - 2 * margin, h - 2 * margin)

    # Trait intérieur doré
    c.setStrokeColor(_GOLD)
    c.setLineWidth(1)
    c.rect(inner, inner, w - 2 * inner, h - 2 * inner)

    # Coins ornementaux (carrés aux 4 coins)
    corner = 6 * mm
    c.setFillColor(_GOLD)
    for x in [margin - 1.5, w - margin - corner + 1.5]:
        for y in [margin - 1.5, h - margin - corner + 1.5]:
            c.rect(x, y, corner, corner, fill=1, stroke=0)


def _center_text(c, text, y, font, size, color=_NAVY):
    c.setFont(font, size)
    c.setFillColor(color)
    tw = c.stringWidth(text, font, size)
    c.drawString((A4[0] - tw) / 2, y, text)


def generer_certificat_pdf(certification) -> bytes:
    """Génère le PDF d'un certificat CNIAH et retourne les bytes."""
    from apps.core.models import ConfigurationCertificat
    from django.conf import settings

    config = ConfigurationCertificat.get()

    buffer = io.BytesIO()
    w, h = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    # ── Fond légèrement crème ──────────────────────────────────────────
    c.setFillColor(_LIGHT_GRAY)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # ── Bande décorative haut (navy) ──────────────────────────────────
    c.setFillColor(_NAVY)
    c.rect(0, h - 28 * mm, w, 28 * mm, fill=1, stroke=0)

    # ── Bande décorative bas (navy) ───────────────────────────────────
    c.setFillColor(_NAVY)
    c.rect(0, 0, w, 22 * mm, fill=1, stroke=0)

    # ── Filet doré sous la bande haute ───────────────────────────────
    c.setFillColor(_GOLD)
    c.rect(0, h - 30 * mm, w, 2 * mm, fill=1, stroke=0)

    # ── Filet doré au-dessus de la bande basse ───────────────────────
    c.setFillColor(_GOLD)
    c.rect(0, 22 * mm, w, 2 * mm, fill=1, stroke=0)

    # ── Logo CNIAH (en-tête) ─────────────────────────────────────────
    logo_path = None
    if config.logo_organisation and hasattr(config.logo_organisation, 'path') and config.logo_organisation.path:
        try:
            logo_path = config.logo_organisation.path
        except Exception:
            pass
    if not logo_path:
        default = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo_cniah.png')
        if os.path.exists(default):
            logo_path = default

    logo_y = h - 27 * mm
    if logo_path:
        try:
            img = ImageReader(logo_path)
            iw, ih = img.getSize()
            logo_h = 20 * mm
            logo_w = logo_h * iw / ih
            c.drawImage(logo_path, (w - logo_w) / 2, logo_y + 2 * mm,
                        width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # ── Nom de l'organisation (bande blanche sur navy) ────────────────
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(colors.white)
    org = "COLLÈGE NATIONAL DES INGÉNIEURS ET ARCHITECTES HAÏTIENS"
    tw = c.stringWidth(org, 'Helvetica-Bold', 10)
    c.drawString((w - tw) / 2, h - 9 * mm, org)

    # ── CERTIFICAT D'EXERCICE ─────────────────────────────────────────
    _center_text(c, "CERTIFICAT D'EXERCICE PROFESSIONNEL",
                 h - 45 * mm, 'Helvetica-Bold', 16, _NAVY)

    # ── Filet doré sous le titre ──────────────────────────────────────
    c.setStrokeColor(_GOLD)
    c.setLineWidth(1.5)
    c.line(30 * mm, h - 49 * mm, w - 30 * mm, h - 49 * mm)

    # ── Corps du certificat ───────────────────────────────────────────
    c.setFont('Helvetica', 11)
    c.setFillColor(_NAVY)
    _center_text(c, "Le Collège National des Ingénieurs et Architectes Haïtiens certifie que",
                 h - 60 * mm, 'Helvetica', 11, _NAVY)

    # ── Nom du membre ─────────────────────────────────────────────────
    membre = certification.membre
    nom_complet = f"{membre.prenom.upper()} {membre.nom.upper()}"
    _center_text(c, nom_complet, h - 76 * mm, 'Helvetica-Bold', 24, _NAVY)

    # ── Trait sous le nom ─────────────────────────────────────────────
    c.setStrokeColor(_GOLD)
    c.setLineWidth(0.8)
    c.line(40 * mm, h - 80 * mm, w - 40 * mm, h - 80 * mm)

    # ── Titre professionnel ───────────────────────────────────────────
    _center_text(c, membre.titre.nom, h - 88 * mm, 'Helvetica-Oblique', 13, _GOLD)

    # ── Texte de certification ────────────────────────────────────────
    body_lines = [
        "est membre actif en règle du CNIAH et est autorisé(e) à exercer sa profession",
        "conformément aux dispositions du Décret-loi présidentiel du 25 mars 1974.",
    ]
    y_body = h - 102 * mm
    for line in body_lines:
        _center_text(c, line, y_body, 'Helvetica', 10.5, _NAVY)
        y_body -= 6 * mm

    # ── Encadré infos certificat ──────────────────────────────────────
    box_y = h - 130 * mm
    box_h = 28 * mm
    c.setFillColor(_LIGHT_GOLD)
    c.setStrokeColor(_GOLD)
    c.setLineWidth(1)
    c.roundRect(30 * mm, box_y, w - 60 * mm, box_h, 4 * mm, fill=1, stroke=1)

    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(_NAVY)
    col1_x = 40 * mm
    col2_x = w / 2 + 10 * mm

    # Ligne 1
    c.drawString(col1_x, box_y + box_h - 9 * mm, "N° DE CERTIFICAT")
    c.drawString(col2_x, box_y + box_h - 9 * mm, "DÉLIVRÉ LE")
    c.setFont('Helvetica', 9)
    c.drawString(col1_x, box_y + box_h - 15 * mm, certification.numero_certificat)
    c.drawString(col2_x, box_y + box_h - 15 * mm,
                 certification.date_delivrance.strftime('%d %B %Y'))

    # Ligne 2
    c.setFont('Helvetica-Bold', 9)
    c.drawString(col1_x, box_y + box_h - 21 * mm, "N° DE MEMBRE")
    c.drawString(col2_x, box_y + box_h - 21 * mm, "VALIDE JUSQU'AU")
    c.setFont('Helvetica', 9)
    c.drawString(col1_x, box_y + box_h - 27 * mm, membre.numero)
    c.drawString(col2_x, box_y + box_h - 27 * mm,
                 certification.date_expiration.strftime('%d %B %Y'))

    # ── Zone signature ────────────────────────────────────────────────
    sig_y_base = 30 * mm
    sig_x = 35 * mm

    # Signature du président
    if config.signature_president and hasattr(config.signature_president, 'path'):
        try:
            sig_img = ImageReader(config.signature_president.path)
            siw, sih = sig_img.getSize()
            sig_h = 18 * mm
            sig_w = sig_h * siw / sih
            c.drawImage(config.signature_president.path,
                        sig_x, sig_y_base + 2 * mm,
                        width=sig_w, height=sig_h,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # Ligne de signature
    c.setStrokeColor(_NAVY)
    c.setLineWidth(0.5)
    c.line(sig_x, sig_y_base + 1 * mm, sig_x + 55 * mm, sig_y_base + 1 * mm)

    # Nom et titre du président
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(colors.white)
    c.drawString(sig_x, sig_y_base - 4 * mm, config.nom_president)
    c.setFont('Helvetica', 7.5)
    c.drawString(sig_x, sig_y_base - 8.5 * mm, config.titre_president)

    # ── QR Code ───────────────────────────────────────────────────────
    if certification.qr_code and hasattr(certification.qr_code, 'path'):
        try:
            qr_size = 22 * mm
            qr_x = w - qr_size - 30 * mm
            qr_y = 25 * mm
            c.drawImage(certification.qr_code.path, qr_x, qr_y,
                        width=qr_size, height=qr_size, preserveAspectRatio=True, mask='auto')
            c.setFont('Helvetica', 5.5)
            c.setFillColor(colors.white)
            c.drawString(qr_x, qr_y - 3.5 * mm, "Vérifier l'authenticité")
        except Exception:
            pass

    # ── Texte de bas de page ──────────────────────────────────────────
    c.setFont('Helvetica-Oblique', 7)
    c.setFillColor(colors.white)
    footer = config.texte_bas_page or ""
    # Wrap simple à 100 chars
    words = footer.split()
    lines, line = [], []
    for w_txt in words:
        if sum(len(x) + 1 for x in line) + len(w_txt) > 100:
            lines.append(' '.join(line))
            line = [w_txt]
        else:
            line.append(w_txt)
    if line:
        lines.append(' '.join(line))

    footer_y = 11 * mm
    for fl in lines[:2]:
        ftw = c.stringWidth(fl, 'Helvetica-Oblique', 7)
        c.drawString((A4[0] - ftw) / 2, footer_y, fl)
        footer_y -= 4 * mm

    c.save()
    return buffer.getvalue()
