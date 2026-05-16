# src/apps/core/utils.py
"""Génération PDF des certificats CNIAH via reportlab — format paysage A4."""

import io
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape as _landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


# Couleurs CNIAH
_NAVY = colors.HexColor('#0a1931')
_GOLD = colors.HexColor('#c9a84c')
_LIGHT_GOLD = colors.HexColor('#f0e6c8')
_LIGHT_GRAY = colors.HexColor('#f8f8f8')


def _draw_text_centered(c, text, y, font, size, color, page_w):
    c.setFont(font, size)
    c.setFillColor(color)
    tw = c.stringWidth(text, font, size)
    c.drawString((page_w - tw) / 2, y, text)


def _load_logo(config, settings):
    """Retourne le chemin du logo CNIAH (config ou static par défaut)."""
    logo_path = None
    if config.logo_organisation and hasattr(config.logo_organisation, 'path'):
        try:
            if os.path.exists(config.logo_organisation.path):
                logo_path = config.logo_organisation.path
        except Exception:
            pass
    if not logo_path:
        default = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo_cniah.png')
        if os.path.exists(default):
            logo_path = default
    return logo_path


def generer_certificat_pdf(certification) -> bytes:
    """Génère le PDF d'un certificat CNIAH en format paysage et retourne les bytes."""
    from apps.core.models import ConfigurationCertificat
    from django.conf import settings

    config = ConfigurationCertificat.get()

    buffer = io.BytesIO()
    page = _landscape(A4)   # 841.89 × 595.28 pt  ≈  297 × 210 mm
    w, h = page
    c = canvas.Canvas(buffer, pagesize=page)

    MARGIN = 15 * mm

    # ── Fond légèrement crème ──────────────────────────────────────────
    c.setFillColor(_LIGHT_GRAY)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # ── Bande navy en haut ─────────────────────────────────────────────
    HEADER_H = 32 * mm
    c.setFillColor(_NAVY)
    c.rect(0, h - HEADER_H, w, HEADER_H, fill=1, stroke=0)

    # ── Filet doré sous l'en-tête ──────────────────────────────────────
    GOLD_BAR = 2 * mm
    c.setFillColor(_GOLD)
    c.rect(0, h - HEADER_H - GOLD_BAR, w, GOLD_BAR, fill=1, stroke=0)

    # ── Bande navy en bas ──────────────────────────────────────────────
    FOOTER_H = 18 * mm
    c.setFillColor(_NAVY)
    c.rect(0, 0, w, FOOTER_H, fill=1, stroke=0)

    # ── Filet doré au-dessus du pied ───────────────────────────────────
    c.setFillColor(_GOLD)
    c.rect(0, FOOTER_H, w, GOLD_BAR, fill=1, stroke=0)

    # ── LOGO — en haut à gauche dans la bande navy ─────────────────────
    logo_path = _load_logo(config, settings)
    if logo_path:
        try:
            img = ImageReader(logo_path)
            iw, ih = img.getSize()
            logo_h = 24 * mm
            logo_w = logo_h * iw / ih
            logo_x = MARGIN
            logo_y = h - HEADER_H + (HEADER_H - logo_h) / 2
            c.drawImage(logo_path, logo_x, logo_y,
                        width=logo_w, height=logo_h,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # ── Nom de l'organisation (centré, blanc) ─────────────────────────
    org = "COLLÈGE NATIONAL DES INGÉNIEURS ET ARCHITECTES HAÏTIENS"
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(colors.white)
    org_tw = c.stringWidth(org, 'Helvetica-Bold', 9)
    c.drawString((w - org_tw) / 2, h - HEADER_H + (HEADER_H - 9) / 2, org)

    # ── Zone de contenu ────────────────────────────────────────────────
    # Entre le filet doré d'en-tête et le filet doré de pied de page.
    content_top = h - HEADER_H - GOLD_BAR

    # Titre du certificat
    y = content_top - 12 * mm
    _draw_text_centered(c, "CERTIFICAT D'EXERCICE PROFESSIONNEL",
                        y, 'Helvetica-Bold', 15, _NAVY, w)

    # Filet doré sous le titre
    y -= 9 * mm
    c.setStrokeColor(_GOLD)
    c.setLineWidth(1.5)
    c.line(MARGIN + 20 * mm, y, w - MARGIN - 20 * mm, y)

    # Texte d'introduction
    y -= 12 * mm
    _draw_text_centered(c,
        "Le Collège National des Ingénieurs et Architectes Haïtiens certifie que",
        y, 'Helvetica', 10, _NAVY, w)

    # Nom du membre (grand, gras)
    membre = certification.membre
    nom_complet = f"{membre.prenom.upper()} {membre.nom.upper()}"
    y -= 17 * mm
    _draw_text_centered(c, nom_complet, y, 'Helvetica-Bold', 22, _NAVY, w)

    # Filet doré sous le nom
    y -= 10 * mm
    c.setStrokeColor(_GOLD)
    c.setLineWidth(0.8)
    c.line(MARGIN + 40 * mm, y, w - MARGIN - 40 * mm, y)

    # Titre professionnel
    y -= 9 * mm
    _draw_text_centered(c, membre.titre.nom, y, 'Helvetica-Oblique', 12, _GOLD, w)

    # Corps du texte de certification
    y -= 14 * mm
    body_lines = [
        "est membre actif en règle du CNIAH et est autorisé(e) à exercer sa profession",
        "conformément aux dispositions du Décret-loi présidentiel du 25 mars 1974.",
    ]
    for line in body_lines:
        _draw_text_centered(c, line, y, 'Helvetica', 9, _NAVY, w)
        y -= 6 * mm

    # ── Section basse : encadré infos | QR code | Signature ──────────
    content_bottom = FOOTER_H + GOLD_BAR   # y du haut du filet doré au-dessus du pied
    BOX_Y = content_bottom + 3 * mm
    BOX_H = 44 * mm
    BOX_X = MARGIN
    BOX_W = 155 * mm

    # Encadré avec fond doré clair
    c.setFillColor(_LIGHT_GOLD)
    c.setStrokeColor(_GOLD)
    c.setLineWidth(1)
    c.roundRect(BOX_X, BOX_Y, BOX_W, BOX_H, 3 * mm, fill=1, stroke=1)

    box_top = BOX_Y + BOX_H
    col1_x = BOX_X + 10 * mm
    col2_x = BOX_X + BOX_W / 2 + 5 * mm

    # Ligne 1 : N° certificat + Date de délivrance
    lbl_y1 = box_top - 9 * mm
    val_y1 = box_top - 16 * mm
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(_NAVY)
    c.drawString(col1_x, lbl_y1, "N° DE CERTIFICAT")
    c.drawString(col2_x, lbl_y1, "DÉLIVRÉ LE")
    c.setFont('Helvetica', 9)
    c.drawString(col1_x, val_y1, certification.numero_certificat)
    c.drawString(col2_x, val_y1,
                 certification.date_delivrance.strftime('%d %B %Y'))

    # Ligne 2 : N° membre + Valide jusqu'au
    lbl_y2 = box_top - 27 * mm
    val_y2 = box_top - 34 * mm
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(_NAVY)
    c.drawString(col1_x, lbl_y2, "N° DE MEMBRE")
    c.drawString(col2_x, lbl_y2, "VALIDE JUSQU'AU")
    c.setFont('Helvetica', 9)
    c.drawString(col1_x, val_y2, membre.numero)
    c.drawString(col2_x, val_y2,
                 certification.date_expiration.strftime('%d %B %Y'))

    # ── QR Code ────────────────────────────────────────────────────────
    qr_x = BOX_X + BOX_W + 12 * mm
    qr_size = BOX_H - 8 * mm   # 36 mm, aligné sur la hauteur de l'encadré
    qr_y = BOX_Y + 4 * mm
    if certification.qr_code and hasattr(certification.qr_code, 'path'):
        try:
            c.drawImage(certification.qr_code.path,
                        qr_x, qr_y, width=qr_size, height=qr_size,
                        preserveAspectRatio=True, mask='auto')
            c.setFont('Helvetica', 6)
            c.setFillColor(_NAVY)
            lbl = "Vérifier l'authenticité"
            lbl_w = c.stringWidth(lbl, 'Helvetica', 6)
            c.drawString(qr_x + (qr_size - lbl_w) / 2, BOX_Y + 1 * mm, lbl)
        except Exception:
            pass

    # ── Signature ──────────────────────────────────────────────────────
    sig_x = qr_x + qr_size + 8 * mm
    sig_line_y = BOX_Y + 14 * mm
    sig_max_w = w - MARGIN - sig_x

    if config.signature_president and hasattr(config.signature_president, 'path'):
        try:
            si = ImageReader(config.signature_president.path)
            siw, sih = si.getSize()
            sig_h = 18 * mm
            sig_w = min(sig_h * siw / sih, sig_max_w)
            c.drawImage(config.signature_president.path,
                        sig_x, sig_line_y + 2 * mm,
                        width=sig_w, height=sig_h,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # Ligne de signature
    c.setStrokeColor(_NAVY)
    c.setLineWidth(0.5)
    c.line(sig_x, sig_line_y, sig_x + min(sig_max_w, 52 * mm), sig_line_y)

    # Nom et titre du président (sous la ligne)
    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(_NAVY)
    c.drawString(sig_x, sig_line_y - 5 * mm, config.nom_president)
    c.setFont('Helvetica', 7)
    c.drawString(sig_x, sig_line_y - 10 * mm, config.titre_president)

    # ── Texte de bas de page (centré, blanc) ──────────────────────────
    footer_text = config.texte_bas_page or ""
    if footer_text:
        c.setFont('Helvetica-Oblique', 6.5)
        c.setFillColor(colors.white)
        max_footer_w = w - 2 * MARGIN
        words = footer_text.split()
        lines_out, current = [], []
        for word in words:
            test = ' '.join(current + [word])
            if c.stringWidth(test, 'Helvetica-Oblique', 6.5) > max_footer_w:
                lines_out.append(' '.join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            lines_out.append(' '.join(current))

        fy = FOOTER_H / 2 + 3
        for fl in lines_out[:2]:
            fw = c.stringWidth(fl, 'Helvetica-Oblique', 6.5)
            c.drawString((w - fw) / 2, fy, fl)
            fy -= 4 * mm

    c.save()
    return buffer.getvalue()
