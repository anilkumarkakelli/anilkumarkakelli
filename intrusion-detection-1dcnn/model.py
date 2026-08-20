"""1D CNN model for network intrusion detection."""

from __future__ import annotations

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


def build_1d_cnn(
    input_length: int,
    num_classes: int,
    filters: tuple[int, ...] = (64, 128, 256),
    kernel_size: int = 3,
    dropout: float = 0.5,
) -> keras.Model:
    """
    Build a 1D CNN classifier.

    Input features are treated as a 1D signal of length `input_length`
  (e.g. NSL-KDD has 41 features → shape (batch, 41, 1)).

    Args:
        input_length: Number of input features (sequence length).
        num_classes: 2 for binary (normal/attack), >2 for multi-class.
        filters: Conv1D filter sizes per block.
        kernel_size: Convolution kernel width.
        dropout: Dropout before the final dense layer.

    Returns:
        Compiled Keras model.
    """
    inputs = keras.Input(shape=(input_length, 1), name="features")

    x = inputs
    for i, n_filters in enumerate(filters):
        x = layers.Conv1D(
            n_filters,
            kernel_size=kernel_size,
            padding="same",
            activation="relu",
            name=f"conv1d_{i}",
        )(x)
        x = layers.BatchNormalization(name=f"bn_{i}")(x)
        x = layers.MaxPooling1D(pool_size=2, name=f"pool_{i}")(x)

    x = layers.GlobalAveragePooling1D(name="gap")(x)
    x = layers.Dense(128, activation="relu", name="dense_hidden")(x)
    x = layers.Dropout(dropout, name="dropout")(x)

    if num_classes == 2:
        outputs = layers.Dense(1, activation="sigmoid", name="output")(x)
        loss = "binary_crossentropy"
        metrics = [
            "accuracy",
            keras.metrics.Precision(name="precision"),
            keras.metrics.Recall(name="recall"),
            keras.metrics.AUC(name="auc"),
        ]
    else:
        outputs = layers.Dense(num_classes, activation="softmax", name="output")(x)
        loss = "sparse_categorical_crossentropy"
        metrics = ["accuracy"]

    model = keras.Model(inputs=inputs, outputs=outputs, name="intrusion_1dcnn")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss=loss,
        metrics=metrics,
    )
    return model


def count_parameters(model: keras.Model) -> int:
    return int(model.count_params())


if __name__ == "__main__":
    m = build_1d_cnn(input_length=41, num_classes=2)
    m.summary()
    print(f"Trainable parameters: {count_parameters(m):,}")
