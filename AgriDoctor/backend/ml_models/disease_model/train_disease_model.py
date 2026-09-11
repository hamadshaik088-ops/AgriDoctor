"""Train the AgriDoctor crop/disease image classifier.

The dataset directory must contain one folder per class, with images inside
each folder. This supports the PlantVillage layout at dataset/PlantVillage/train
and writes the discovered class order beside the trained model.
"""

import argparse
import json
import random
from pathlib import Path

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 42
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def discover_classes(dataset_dir):
    classes = sorted(path.name for path in dataset_dir.iterdir() if path.is_dir())
    if len(classes) < 2:
        raise ValueError(f"Expected at least two class folders in {dataset_dir}.")
    empty = [name for name in classes if not any(
        path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        for path in (dataset_dir / name).iterdir()
    )]
    if empty:
        raise ValueError(f"These class folders contain no supported images: {empty}")
    return classes


def build_datasets(dataset_dir, class_names, max_images_per_class):
    randomizer = random.Random(SEED)
    train_files = []
    train_labels = []
    validation_files = []
    validation_labels = []
    image_counts = {}

    for label, class_name in enumerate(class_names):
        files = [
            path for path in (dataset_dir / class_name).iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        ]
        randomizer.shuffle(files)
        if max_images_per_class:
            files = files[:max_images_per_class]
        split_index = max(1, int(len(files) * 0.8))
        train_files.extend(str(path) for path in files[:split_index])
        train_labels.extend([label] * split_index)
        validation_files.extend(str(path) for path in files[split_index:])
        validation_labels.extend([label] * (len(files) - split_index))
        image_counts[class_name] = len(files)

    def load_image(path, label):
        image = tf.io.read_file(path)
        image = tf.image.decode_image(image, channels=3, expand_animations=False)
        image = tf.image.resize(image, IMAGE_SIZE)
        return image, tf.one_hot(label, len(class_names))

    train = tf.data.Dataset.from_tensor_slices((train_files, train_labels))
    train = train.shuffle(len(train_files), seed=SEED, reshuffle_each_iteration=True)
    train = train.map(load_image, num_parallel_calls=tf.data.AUTOTUNE).batch(BATCH_SIZE)
    validation = tf.data.Dataset.from_tensor_slices((validation_files, validation_labels))
    validation = validation.map(load_image, num_parallel_calls=tf.data.AUTOTUNE).batch(BATCH_SIZE)
    autotune = tf.data.AUTOTUNE
    return train.prefetch(autotune), validation.prefetch(autotune), image_counts


def build_model(class_count):
    augmentation = keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.08),
        layers.RandomZoom(0.12),
    ], name="augmentation")
    base = keras.applications.MobileNetV2(
        input_shape=(*IMAGE_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False
    inputs = keras.Input(shape=(*IMAGE_SIZE, 3))
    x = augmentation(inputs)
    x = keras.applications.mobilenet_v2.preprocess_input(x)
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.25)(x)
    outputs = layers.Dense(class_count, activation="softmax")(x)
    model = keras.Model(inputs, outputs)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("disease_model.keras"))
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--max-images-per-class", type=int, default=300)
    args = parser.parse_args()

    dataset_dir = args.dataset.resolve()
    if not dataset_dir.is_dir():
        raise SystemExit(f"Dataset directory does not exist: {dataset_dir}")
    class_names = discover_classes(dataset_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    train, validation, image_counts = build_datasets(dataset_dir, class_names, args.max_images_per_class)
    model = build_model(len(class_names))
    total_images = sum(image_counts.values())
    class_weight = {
        index: total_images / (len(class_names) * count)
        for index, name in enumerate(class_names)
        for count in [image_counts[name]]
    }
    callbacks = [
        keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=3, restore_best_weights=True),
        keras.callbacks.ModelCheckpoint(args.output, monitor="val_accuracy", save_best_only=True),
    ]
    history = model.fit(
        train,
        validation_data=validation,
        epochs=args.epochs,
        callbacks=callbacks,
        class_weight=class_weight,
    )
    model.save(args.output)
    class_names_path = args.output.parent / "class_names.json"
    class_names_path.write_text(json.dumps(class_names, indent=2) + "\n", encoding="utf-8")
    metrics = {
        "classes": class_names,
        "image_counts": image_counts,
        "final_training_accuracy": history.history["accuracy"][-1],
        "final_validation_accuracy": history.history["val_accuracy"][-1],
        "epochs_completed": len(history.history["loss"]),
    }
    (args.output.parent / "training_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(f"Saved model: {args.output.resolve()}")
    print(f"Saved classes: {class_names_path.resolve()}")
    print(f"Validation accuracy: {metrics['final_validation_accuracy']:.4f}")


if __name__ == "__main__":
    main()
