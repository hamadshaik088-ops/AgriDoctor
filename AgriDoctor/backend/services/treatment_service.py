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
    ("groundnut", "tikka leaf spot"): [
        ("Mancozeb 75% WP", "Dithane M-45 or equivalent registered product"),
        ("Chlorothalonil 75% WP", "Kavach or equivalent registered product"),
    ],
    ("groundnut", "rust"): [
        ("Mancozeb 75% WP", "Dithane M-45 or equivalent registered product"),
        ("Tebuconazole 25.9% EC", "Folicur or equivalent registered product"),
    ],
}


def _normalize_name(value):
    return value.strip().lower().replace("_", " ").replace("-", " ").replace("/", " ")


def get_treatments_for_disease(crop, disease_name):
    crop_name = crop.strip().lower()
    disease_key = _normalize_name(disease_name)

    exact = (crop_name, disease_key)
    if exact in TREATMENTS:
        treatments = TREATMENTS[exact]
    else:
        treatments = []
        for (crop_key, disease_label), items in TREATMENTS.items():
            if crop_key == crop_name and (
                disease_key == disease_label or disease_key in disease_label or disease_label in disease_key
            ):
                treatments = items
                break
        if not treatments:
            treatments = [
                ("Mancozeb 75% WP", "Dithane M-45 or equivalent registered product"),
                ("Copper oxychloride 50% WP", "Blitox or equivalent registered product"),
            ]

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
