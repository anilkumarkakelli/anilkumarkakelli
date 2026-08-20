#!/usr/bin/env python3
"""Train and evaluate a 1D CNN for intrusion detection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

from data import load_data
from model import build_1d_cnn


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="1D CNN intrusion detection")
    p.add_argument("--source", choices=["synthetic", "nsl_kdd"], default="synthetic")
    p.add_argument("--train-path", type=str, help="NSL-KDD train CSV path")
    p.add_argument("--test-path", type=str, help="Optional NSL-KDD test CSV path")
    p.add_argument("--binary", action="store_true", default=True)
    p.add_argument("--multiclass", action="store_true", help="Use multi-class labels")
    p.add_argument("--epochs", type=int, default=25)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--output-dir", type=str, default="outputs")
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def plot_history(history: tf.keras.callbacks.History, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].plot(history.history["loss"], label="train")
    axes[0].plot(history.history["val_loss"], label="val")
    axes[0].set_title("Loss")
    axes[0].set_xlabel("Epoch")
    axes[0].legend()

    axes[1].plot(history.history["accuracy"], label="train")
    axes[1].plot(history.history["val_accuracy"], label="val")
    axes[1].set_title("Accuracy")
    axes[1].set_xlabel("Epoch")
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(out_dir / "training_curves.png", dpi=150)
    plt.close(fig)


def plot_confusion(y_true: np.ndarray, y_pred: np.ndarray, labels: list[str], out_dir: Path) -> None:
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Confusion matrix")

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color="black")

    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(out_dir / "confusion_matrix.png", dpi=150)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    binary = not args.multiclass

    tf.keras.utils.set_random_seed(args.seed)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = load_data(
        source=args.source,
        train_path=args.train_path,
        test_path=args.test_path,
        binary=binary,
        random_state=args.seed,
    )

    print(f"Train: {data.x_train.shape}, Val: {data.x_val.shape}, Test: {data.x_test.shape}")
    print(f"Features: {data.num_features}, Classes: {data.num_classes}")
    print(f"Labels: {list(data.label_encoder.classes_)}")

    model = build_1d_cnn(
        input_length=data.num_features,
        num_classes=data.num_classes,
    )
    model.summary()

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=5, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6
        ),
        tf.keras.callbacks.ModelCheckpoint(
            out_dir / "best_model.keras",
            monitor="val_loss",
            save_best_only=True,
        ),
    ]

    class_weights = None
    if binary:
        n0 = int(np.sum(data.y_train == 0))
        n1 = int(np.sum(data.y_train == 1))
        total = n0 + n1
        class_weights = {0: total / (2 * n0), 1: total / (2 * n1)}
        print(f"Class weights: {class_weights}")

    history = model.fit(
        data.x_train,
        data.y_train,
        validation_data=(data.x_val, data.y_val),
        epochs=args.epochs,
        batch_size=args.batch_size,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1,
    )

    plot_history(history, out_dir)

    # Evaluate on test set
    test_metrics = model.evaluate(data.x_test, data.y_test, verbose=0)
    metric_names = model.metrics_names
    results = dict(zip(metric_names, [float(v) for v in test_metrics]))
    print("\nTest metrics:", results)

    if binary:
        y_prob = model.predict(data.x_test, verbose=0).ravel()
        y_pred = (y_prob >= 0.5).astype(int)
    else:
        y_prob = model.predict(data.x_test, verbose=0)
        y_pred = np.argmax(y_prob, axis=1)

    report = classification_report(
        data.y_test, y_pred, target_names=list(data.label_encoder.classes_), output_dict=True
    )
    print("\nClassification report:")
    print(classification_report(data.y_test, y_pred, target_names=list(data.label_encoder.classes_)))

    plot_confusion(
        data.y_test, y_pred, list(data.label_encoder.classes_), out_dir
    )

    model.save(out_dir / "final_model.keras")
    with open(out_dir / "metrics.json", "w") as f:
        json.dump({"test": results, "classification_report": report}, f, indent=2)

    print(f"\nSaved model and plots to {out_dir.resolve()}")


if __name__ == "__main__":
    main()
