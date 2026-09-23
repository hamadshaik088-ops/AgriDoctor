TREATMENTS = {
    ("tomato", "early blight"): [
        ("Mancozeb 75% WP", "Dithane M-45 or equivalent registered product"),
        ("Chlorothalonil 75% WP", "Kavach or equivalent registered product"),
        ("Copper oxychloride 50% WP", "Blitox or equivalent registered product"),
    ],
    ("tomato", "late blight"): [
        ("Mancozeb 75% WP", "Dithane M-45 or equivalent registered product"),
        ("Metalaxyl 8% + Mancozeb 64% WP", "Ridomil Gold or equivalent registered product"),
        ("Cymoxanil 8% + Mancozeb 64% WP", "Curzate M8 or equivalent registered product"),
    ],
    ("tomato", "leaf mold"): [
        ("Mancozeb 75% WP", "Dithane M-45 or equivalent registered product"),
        ("Copper oxychloride 50% WP", "Blitox or equivalent registered product"),
    ],
    ("potato", "early blight"): [
        ("Mancozeb 75% WP", "Dithane M-45 or equivalent registered product"),
        ("Chlorothalonil 75% WP", "Kavach or equivalent registered product"),
    ],
    ("potato", "late blight"): [
        ("Metalaxyl 8% + Mancozeb 64% WP", "Ridomil Gold or equivalent registered product"),
        ("Cymoxanil 8% + Mancozeb 64% WP", "Curzate M8 or equivalent registered product"),
        ("Mancozeb 75% WP", "Dithane M-45 or equivalent registered product"),
    ],
    ("apple", "apple scab"): [
        ("Mancozeb 75% WP", "Registered equivalent product"),
        ("Captan 50% WP", "Registered equivalent product"),
    ],
    ("apple", "black rot"): [
        ("Mancozeb 75% WP", "Registered equivalent product"),
        ("Copper oxychloride 50% WP", "Registered equivalent product"),
    ],
    ("apple", "cedar apple rust"): [
        ("Mancozeb 75% WP", "Registered equivalent product"),
    ],
    ("blueberry", "healthy"): [],
    ("cherry (including sour)", "powdery mildew"): [
        ("Sulfur 80% WP", "Registered equivalent product"),
    ],
    ("corn (maize)", "cercospora leaf spot gray leaf spot"): [
        ("Mancozeb 75% WP", "Registered equivalent product"),
    ],
    ("corn (maize)", "common rust"): [
        ("Mancozeb 75% WP", "Registered equivalent product"),
    ],
    ("corn (maize)", "northern leaf blight"): [
        ("Mancozeb 75% WP", "Registered equivalent product"),
    ],
    ("grape", "black rot"): [
        ("Mancozeb 75% WP", "Registered equivalent product"),
        ("Copper oxychloride 50% WP", "Registered equivalent product"),
    ],
    ("grape", "leaf blight (isariopsis leaf spot)"): [
        ("Mancozeb 75% WP", "Registered equivalent product"),
    ],
    ("orange", "haunglongbing (citrus greening)"): [],
    ("peach", "bacterial spot"): [
        ("Copper oxychloride 50% WP", "Registered equivalent product"),
    ],
    ("pepper, bell", "bacterial spot"): [
        ("Copper oxychloride 50% WP", "Registered equivalent product"),
    ],
    ("squash", "powdery mildew"): [
        ("Sulfur 80% WP", "Registered equivalent product"),
    ],
    ("strawberry", "leaf scorch"): [],
    ("tomato", "bacterial spot"): [
        ("Copper oxychloride 50% WP", "Registered equivalent product"),
    ],
    ("tomato", "septoria leaf spot"): [
        ("Mancozeb 75% WP", "Registered equivalent product"),
        ("Chlorothalonil 75% WP", "Registered equivalent product"),
    ],
    ("tomato", "spider mites two spotted spider mite"): [
        ("Abamectin 1.9% EC", "Registered equivalent product"),
    ],
    ("tomato", "target spot"): [
        ("Mancozeb 75% WP", "Registered equivalent product"),
    ],
    ("tomato", "tomato yellow leaf curl virus"): [],
    ("tomato", "tomato mosaic virus"): [],
    ("groundnut", "tikka leaf spot"): [
        ("Mancozeb 75% WP", "Dithane M-45 or equivalent registered product"),
        ("Chlorothalonil 75% WP", "Kavach or equivalent registered product"),
    ],
    ("groundnut", "rust"): [
        ("Mancozeb 75% WP", "Dithane M-45 or equivalent registered product"),
        ("Tebuconazole 25.9% EC", "Folicur or equivalent registered product"),
    ],
    ("rice", "false smut"): [
        ("Propiconazole 25% EC", "Tilt or equivalent registered product"),
        ("Tebuconazole 25.9% EC", "Folicur or equivalent registered product"),
        ("Azoxystrobin 23% SC", "Amistar or equivalent registered product"),
    ],
}


def _normalize_name(value):
    return " ".join(value.strip().lower().replace("_", " ").replace("-", " ").replace("/", " ").split())


def _normalize_crop(value):
    crop_name = _normalize_name(value)
    aliases = {
        "solanum lycopersicum": "tomato",
        "solanum tuberosum": "potato",
        "malus domestica": "apple",
        "arachis hypogaea": "groundnut",
        "peanut": "groundnut",
        "oryza sativa": "rice",
        "paddy": "rice",
        "zea mays": "corn (maize)",
        "maize": "corn (maize)",
        "vitis vinifera": "grape",
    }
    return aliases.get(crop_name, crop_name)


def get_treatments_for_disease(crop, disease_name):
    crop_name = _normalize_crop(crop)
    disease_key = _normalize_name(disease_name)

    exact = (crop_name, disease_key)
    if exact in TREATMENTS:
        treatments = TREATMENTS[exact]
    else:
        treatments = None
        for (crop_key, disease_label), items in TREATMENTS.items():
            if crop_key == crop_name and (
                disease_key == disease_label or disease_key in disease_label or disease_label in disease_key
            ):
                treatments = items
                break
        if treatments is None:
            disease_without_crop = disease_key.removeprefix(f"{crop_name} ")
            for (crop_key, disease_label), items in TREATMENTS.items():
                if crop_key == crop_name and (
                    disease_without_crop == disease_label
                    or disease_without_crop in disease_label
                    or disease_label in disease_without_crop
                ):
                    treatments = items
                    break
        if treatments is None:
            return []

    return [{
        "crop": crop,
        "disease": disease_name,
        "treatment_category": "Fungicide option",
        "active_ingredient": active_ingredient,
        "product_name": product_name,
        "application_guidance": "Use only the dose and spray interval printed on the registered product label for this crop and disease.",
        "safety_precautions": "Wear gloves, protective clothing, and eye protection. Observe the product label and pre-harvest interval.",
        "pre_harvest_interval": "As per product label",
        "region": "India",
        "source": "Registered product label; verify current local approval",
        "last_updated": "2026-01-15"
    } for active_ingredient, product_name in treatments]
