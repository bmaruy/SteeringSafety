"""
Script to create filtered PreciseWiki indices from collected correct/incorrect indices.

Usage:
    python -m data.datasets.create_filtered_precisewiki --input data/datasets/precisewiki_indices.json

This will create a file at data/datasets/precisewiki_filtered_indices.json with the structure:
{
    "train": [list of indices],
    "validation": [list of indices],
    "test": [list of indices],
    ...
}
"""

import json
import argparse
import random
from pathlib import Path

def create_filtered_indices(
    input_file: str,
    output_file: str = None,
    n_test_correct: int = 100,
    n_test_incorrect: int = 100,
    seed: int = 42
):
    """
    Create filtered indices from the collected correct/incorrect indices.

    Args:
        input_file: Path to the JSON file with indices (precisewiki_indices.json)
        output_file: Path to save the filtered indices (default: data/datasets/precisewiki_filtered_indices.json)
        n_test_correct: Number of correct test samples to include
        n_test_incorrect: Number of incorrect test samples to randomly select
        seed: Random seed for reproducibility
    """
    random.seed(seed)

    # Load the indices
    with open(input_file, 'r') as f:
        indices_data = json.load(f)

    # Handle both formats:
    # Format 1 (simple): {"train_correct_indices": [...], "test_correct_indices": [...], ...}
    # Format 2 (full results): {"train": {"correct": [{"index": ...}, ...]}, ...}

    if "train_correct_indices" in indices_data:
        # Simple format - indices directly
        train_correct_indices = indices_data["train_correct_indices"]
        train_incorrect_indices = indices_data.get("train_incorrect_indices", [])
        test_correct_indices = indices_data["test_correct_indices"]
        test_incorrect_indices = indices_data["test_incorrect_indices"]
    else:
        # Full results format - need to extract indices from dicts
        train_correct_indices = [s['index'] for s in indices_data['train']['correct']]
        train_incorrect_indices = [s['index'] for s in indices_data['train'].get('incorrect', [])]
        test_correct_indices = [s['index'] for s in indices_data['test']['correct']]
        test_incorrect_indices = [s['index'] for s in indices_data['test']['incorrect']]

    # Train: use all correct samples
    train_indices = train_correct_indices
    print(f"Train: Using all {len(train_indices)} correct samples")

    # Test correct: use up to n_test_correct
    if len(test_correct_indices) > n_test_correct:
        test_correct_selected = random.sample(test_correct_indices, n_test_correct)
    else:
        test_correct_selected = test_correct_indices
    print(f"Test correct: Using {len(test_correct_selected)} samples (requested {n_test_correct})")

    # Test incorrect: randomly sample n_test_incorrect
    if len(test_incorrect_indices) > n_test_incorrect:
        test_incorrect_selected = random.sample(test_incorrect_indices, n_test_incorrect)
    else:
        test_incorrect_selected = test_incorrect_indices
        print(f"Warning: Only {len(test_incorrect_indices)} incorrect samples available, using all")
    print(f"Test incorrect: Using {len(test_incorrect_selected)} samples (requested {n_test_incorrect})")

    # Combine test indices and shuffle
    test_indices = test_correct_selected + test_incorrect_selected
    random.shuffle(test_indices)
    print(f"Test total: {len(test_indices)} samples")

    # Validation: use subset of train indices
    validation_indices = train_indices[:max(1, len(train_indices)//4)]
    print(f"Validation: Using {len(validation_indices)} samples (subset of train)")

    # Create output structure
    filtered_indices = {
        "train": train_indices,
        "validation": validation_indices,
        "test": test_indices,
        "metadata": {
            "train_count": len(train_indices),
            "validation_count": len(validation_indices),
            "test_count": len(test_indices),
            "test_correct_count": len(test_correct_selected),
            "test_incorrect_count": len(test_incorrect_selected),
            "n_test_correct_requested": n_test_correct,
            "n_test_incorrect_requested": n_test_incorrect,
            "seed": seed,
            "source_file": str(input_file)
        },
        # Keep separate lists for reference
        "test_correct_indices": test_correct_selected,
        "test_incorrect_indices": test_incorrect_selected
    }

    # Determine output path
    if output_file is None:
        output_file = Path(__file__).parent / "precisewiki_filtered_indices.json"

    # Save
    with open(output_file, 'w') as f:
        json.dump(filtered_indices, f, indent=2)

    print(f"\nSaved filtered indices to: {output_file}")
    print(f"  Train samples: {len(train_indices)}")
    print(f"  Validation samples: {len(validation_indices)}")
    print(f"  Test samples: {len(test_indices)} ({len(test_correct_selected)} correct + {len(test_incorrect_selected)} incorrect)")

    return filtered_indices


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create filtered PreciseWiki indices")
    parser.add_argument("--input", type=str, required=True, help="Path to precisewiki_indices.json")
    parser.add_argument("--output", type=str, default=None, help="Output path (default: data/datasets/precisewiki_filtered_indices.json)")
    parser.add_argument("--n_test_correct", type=int, default=100, help="Number of correct test samples")
    parser.add_argument("--n_test_incorrect", type=int, default=100, help="Number of incorrect test samples to randomly select")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()

    create_filtered_indices(
        input_file=args.input,
        output_file=args.output,
        n_test_correct=args.n_test_correct,
        n_test_incorrect=args.n_test_incorrect,
        seed=args.seed
    )
