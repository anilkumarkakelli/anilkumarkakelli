# 1D CNN for Intrusion Detection

A compact **1-dimensional CNN** for classifying network traffic as **normal** or **attack** (binary), or multi-class attack types. Tabular features (e.g. NSL-KDD) are reshaped to `(features, 1)` and passed through Conv1D blocks.

## Architecture

```
Input (n_features, 1)
  → Conv1D(64) → BatchNorm → MaxPool
  → Conv1D(128) → BatchNorm → MaxPool
  → Conv1D(256) → BatchNorm → MaxPool
  → GlobalAveragePooling1D
  → Dense(128) → Dropout(0.5)
  → Output (sigmoid for binary / softmax for multi-class)
```

## Setup

```bash
cd intrusion-detection-1dcnn
pip install -r requirements.txt
```

## Quick demo (synthetic data)

```bash
python train.py --source synthetic --epochs 15 --output-dir outputs
```

Outputs: `best_model.keras`, `final_model.keras`, `training_curves.png`, `confusion_matrix.png`, `metrics.json`.

## Train on NSL-KDD

1. Download [NSL-KDD](https://www.unb.ca/cic/datasets/nsl.html) (`KDDTrain+.txt`, `KDDTest+.txt`).
2. Run:

```bash
python train.py \
  --source nsl_kdd \
  --train-path /path/to/KDDTrain+.txt \
  --test-path /path/to/KDDTest+.txt \
  --epochs 30 \
  --batch-size 128 \
  --output-dir outputs/nsl_kdd
```

## Multi-class (attack type)

```bash
python train.py --source nsl_kdd --train-path KDDTrain+.txt --multiclass
```

## Files

| File | Purpose |
|---|---|
| `model.py` | 1D CNN definition |
| `data.py` | NSL-KDD loader + synthetic generator |
| `train.py` | Training, evaluation, plots |

## Notes for class projects

- **Imbalance:** NSL-KDD is skewed; the trainer uses `class_weight` for binary mode.
- **Feature scaling:** categorical one-hot + numeric MinMaxScaler for NSL-KDD.
- **Real deployment:** export with `model.save()` and serve via TensorFlow Serving or convert to ONNX; feed live flow features from Zeek, Suricata, or CICFlowMeter.

## Expected metrics (synthetic demo)

On synthetic data you should see **>95% accuracy** within ~15 epochs. Real NSL-KDD results vary (~85–98% depending on split and preprocessing).
