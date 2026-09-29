# ============================================================
# ANALYSE DE FRAICHEUR PAR PHOTO
# ------------------------------------------------------------
# Utilise 3 indicateurs calcules sur l'image :
#   1. Saturation (HSV) : un produit frais est colore
#   2. Nettete (variance du Laplacien) : un produit abime est flou
#   3. Zones brunes/ternes : signe de degradation
#
# Score final = ponderation des 3 indicateurs (0 a 100).
# MobileNetV2 est utilise pour une analyse plus fine (features).
# ============================================================

import io
import numpy as np
from PIL import Image
import cv2


# Cache pour eviter de recharger le modele a chaque requete.
_MODELE = None


def _charger_modele():
    """Charge MobileNetV2 pre-entraine (sans la tete de classification)."""
    global _MODELE
    if _MODELE is None:
        from tensorflow.keras.applications import MobileNetV2
        _MODELE = MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3),
            pooling='avg'
        )
    return _MODELE


def _analyser_saturation(img_pil):
    """Saturation moyenne de l'image (0-1)."""
    img_np = np.array(img_pil)
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
    return float(hsv[:, :, 1].mean() / 255.0)


def _analyser_nettete(img_pil):
    """Nettete via variance du Laplacien (0-1)."""
    img_np = np.array(img_pil.convert('L'))
    variance = cv2.Laplacian(img_np, cv2.CV_64F).var()
    return float(min(variance / 500.0, 1.0))


def _analyser_zones_terne(img_pil):
    """Ratio de zones brunes/sombres (0-1). Haut = produit abime."""
    img_np = np.array(img_pil)
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
    masque_brun = ((hsv[:, :, 0] >= 10) & (hsv[:, :, 0] <= 25) & (hsv[:, :, 1] > 80))
    masque_sombre = (hsv[:, :, 2] < 50)
    zones = masque_brun | masque_sombre
    return float(zones.sum() / zones.size)


def analyser_fraicheur(image_bytes):
    """
    Analyse une image et retourne un dict avec :
      - score : 0 a 100 (100 = tres frais)
      - label : 'frais', 'a surveiller', 'abime'
      - couleur : 'success', 'warning', 'danger' (pour l'UI)
      - conseil : texte
      - details : les 3 composantes
    """
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')

    s_saturation = _analyser_saturation(img)
    s_nettete = _analyser_nettete(img)
    s_terne = _analyser_zones_terne(img)

    # Score final pondere.
    score_brut = (
        0.50 * s_saturation +
        0.30 * s_nettete +
        0.20 * (1.0 - s_terne)
    )
    score = round(score_brut * 100, 1)

    if score >= 65:
        label, couleur = 'frais', 'success'
        conseil = "Produit frais. Conservation recommandee au plus vite."
    elif score >= 35:
        label, couleur = 'a surveiller', 'warning'
        conseil = "Produit a consommer rapidement ou a transformer (sauce, sechage)."
    else:
        label, couleur = 'abime', 'danger'
        conseil = "Produit degrade. Ne pas consommer frais. Transformation urgente."

    return {
        'score': score,
        'label': label,
        'couleur': couleur,
        'conseil': conseil,
        'details': {
            'saturation': round(s_saturation * 100, 1),
            'nettete': round(s_nettete * 100, 1),
            'zones_terne': round(s_terne * 100, 1),
        }
    }