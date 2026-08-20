"""Data loading and preprocessing for intrusion detection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, OneHotEncoder

# NSL-KDD column names (41 features + label + difficulty; we drop difficulty)
NSL_KDD_COLUMNS = [
    "duration",
    "protocol_type",
    "service",
    "flag",
    "src_bytes",
    "dst_bytes",
    "land",
    "wrong_fragment",
    "urgent",
    "hot",
    "num_failed_logins",
    "logged_in",
    "num_compromised",
    "root_shell",
    "su_attempted",
    "num_root",
    "num_file_creations",
    "num_shells",
    "num_access_files",
    "num_outbound_cmds",
    "is_host_login",
    "is_guest_login",
    "count",
    "srv_count",
    "serror_rate",
    "srv_serror_rate",
    "rerror_rate",
    "srv_rerror_rate",
    "same_srv_rate",
    "diff_srv_rate",
    "srv_diff_host_rate",
    "dst_host_count",
    "dst_host_srv_count",
    "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate",
    "dst_host_srv_serror_rate",
    "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate",
    "label",
    "difficulty",
]

CATEGORICAL_COLS = ["protocol_type", "service", "flag"]
NUMERIC_COLS = [c for c in NSL_KDD_COLUMNS if c not in CATEGORICAL_COLS + ["label", "difficulty"]]


@dataclass
class DatasetBundle:
    x_train: np.ndarray
    y_train: np.ndarray
    x_val: np.ndarray
    y_val: np.ndarray
    x_test: np.ndarray
    y_test: np.ndarray
    num_features: int
    num_classes: int
    label_encoder: LabelEncoder
    preprocessor: ColumnTransformer | Pipeline


def _attack_to_binary(label: str) -> str:
    return "normal" if str(label).strip().lower() == "normal" else "attack"


def load_nsl_kdd(
    train_path: str | Path,
    test_path: str | Path | None = None,
    *,
    binary: bool = True,
    test_size: float = 0.2,
    val_size: float = 0.1,
    random_state: int = 42,
) -> DatasetBundle:
    """
    Load NSL-KDD CSV files (no header row).

    Download (example):
      https://www.unb.ca/cic/datasets/nsl.html
    """
    train_path = Path(train_path)
    if not train_path.exists():
        raise FileNotFoundError(f"Training file not found: {train_path}")

    df_train = pd.read_csv(train_path, header=None, names=NSL_KDD_COLUMNS)
    df_train = df_train.drop(columns=["difficulty"], errors="ignore")

    if test_path:
        df_test = pd.read_csv(Path(test_path), header=None, names=NSL_KDD_COLUMNS)
        df_test = df_test.drop(columns=["difficulty"], errors="ignore")
        df = pd.concat([df_train, df_test], ignore_index=True)
    else:
        df = df_train

    labels = df["label"].astype(str)
    if binary:
        labels = labels.map(_attack_to_binary)
    else:
        # NSL-KDD labels often end with '.' — strip it
        labels = labels.str.rstrip(".")

    y_encoder = LabelEncoder()
    y = y_encoder.fit_transform(labels)

    x = df.drop(columns=["label"])
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_COLS),
            ("num", MinMaxScaler(), NUMERIC_COLS),
        ]
    )

    x_processed = preprocessor.fit_transform(x).astype(np.float32)
    # Shape for Conv1D: (samples, timesteps, channels)
    x_processed = x_processed.reshape(x_processed.shape[0], x_processed.shape[1], 1)

    x_temp, x_test, y_temp, y_test = train_test_split(
        x_processed, y, test_size=test_size, stratify=y, random_state=random_state
    )
    val_ratio = val_size / (1.0 - test_size)
    x_train, x_val, y_train, y_val = train_test_split(
        x_temp, y_temp, test_size=val_ratio, stratify=y_temp, random_state=random_state
    )

    num_classes = len(y_encoder.classes_)
    return DatasetBundle(
        x_train=x_train,
        y_train=y_train,
        x_val=x_val,
        y_val=y_val,
        x_test=x_test,
        y_test=y_test,
        num_features=x_train.shape[1],
        num_classes=2 if binary else num_classes,
        label_encoder=y_encoder,
        preprocessor=preprocessor,
    )


def generate_synthetic_intrusion_data(
    n_samples: int = 8000,
    n_features: int = 41,
    *,
    binary: bool = True,
    test_size: float = 0.2,
    val_size: float = 0.1,
    random_state: int = 42,
) -> DatasetBundle:
    """
    Synthetic tabular data mimicking normal vs attack traffic patterns.

    Useful for demos when NSL-KDD is not downloaded.
    Normal: lower mean, tighter variance. Attack: shifted + spiky features.
    """
    rng = np.random.default_rng(random_state)
    n_normal = n_samples // 2
    n_attack = n_samples - n_normal

    normal = rng.normal(loc=0.2, scale=0.15, size=(n_normal, n_features)).astype(np.float32)
    attack = rng.normal(loc=0.65, scale=0.25, size=(n_attack, n_features)).astype(np.float32)
    # Inject spike patterns on a few "alert" dimensions
    spike_dims = rng.choice(n_features, size=5, replace=False)
    attack[:, spike_dims] += rng.uniform(0.5, 1.5, size=(n_attack, len(spike_dims)))

    x = np.vstack([normal, attack])
    x = np.clip(x, 0.0, 1.0)
    x = x.reshape(x.shape[0], x.shape[1], 1)

    if binary:
        y = np.array([0] * n_normal + [1] * n_attack, dtype=np.int32)
        classes = np.array(["normal", "attack"])
    else:
        # 4 synthetic attack types
        y = np.zeros(n_samples, dtype=np.int32)
        y[n_normal:] = rng.integers(1, 4, size=n_attack)
        classes = np.array(["normal", "dos", "probe", "r2l"])

    le = LabelEncoder()
    le.classes_ = classes

    x_temp, x_test, y_temp, y_test = train_test_split(
        x, y, test_size=test_size, stratify=y, random_state=random_state
    )
    val_ratio = val_size / (1.0 - test_size)
    x_train, x_val, y_train, y_val = train_test_split(
        x_temp, y_temp, test_size=val_ratio, stratify=y_temp, random_state=random_state
    )

    num_classes = 2 if binary else len(classes)
    return DatasetBundle(
        x_train=x_train,
        y_train=y_train,
        x_val=x_val,
        y_val=y_val,
        x_test=x_test,
        y_test=y_test,
        num_features=n_features,
        num_classes=num_classes,
        label_encoder=le,
        preprocessor=Pipeline([]),  # no-op for synthetic
    )


def load_data(
    source: Literal["synthetic", "nsl_kdd"] = "synthetic",
    train_path: str | Path | None = None,
    test_path: str | Path | None = None,
    **kwargs,
) -> DatasetBundle:
    if source == "synthetic":
        return generate_synthetic_intrusion_data(**kwargs)
    if source == "nsl_kdd":
        if not train_path:
            raise ValueError("train_path is required for source='nsl_kdd'")
        return load_nsl_kdd(train_path, test_path, **kwargs)
    raise ValueError(f"Unknown source: {source}")
