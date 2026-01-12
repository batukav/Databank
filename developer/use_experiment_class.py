"""
Example script to demonstrate the use of the Experiment class.
"""

from DatabankLib.core import Databank

def main():
    """
    Initializes the databank, loads experiments, and demonstrates
    accessing their data and performing transformations.
    """
    print("Initializing databank...")
    db = Databank()

    print("\nLoading experiments...")
    experiments = db.get_experiments()

    if not experiments:
        print("No experiments found.")
        return

    print(f"\nFound {len(experiments)} experiments.")

    for exp in experiments:
        print(f"\n--- Experiment ID: {exp.exp_id} ---")
        print("Metadata:")
        for key, value in exp.metadata.items():
            print(f"  {key}: {value}")

        print("\nRaw Data:")
        print(exp.data)

        print("\nTransformed Data:")
        transformed_data = exp.transform_data()
        print(transformed_data)
        print("--------------------------------\n")

if __name__ == "__main__":
    main()

