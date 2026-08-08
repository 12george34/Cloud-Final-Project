import pandas as pd
import time


def analyze_diets(csv_file):

    start_time = time.time()

    # Load dataset from Azure Blob Storage stream
    df = pd.read_csv(csv_file)


    print("Original dataset:")
    print(df.head())


    # Clean missing values
    numeric_columns = [
        "Protein(g)",
        "Carbs(g)",
        "Fat(g)"
    ]


    for col in numeric_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

        df[col] = df[col].fillna(
            df[col].mean()
        )


    # Calculate average macros by diet
    avg_macros = (
        df.groupby("Diet_type")[numeric_columns]
        .mean()
    )


    print("\nAverage Macronutrients:")
    print(avg_macros)


    # Convert macro averages into JSON format
    macro_results = []


    for diet, values in avg_macros.iterrows():

        macro_results.append(
            {
                "diet": diet,

                "protein":
                    round(
                        values["Protein(g)"],
                        2
                    ),

                "carbs":
                    round(
                        values["Carbs(g)"],
                        2
                    ),

                "fat":
                    round(
                        values["Fat(g)"],
                        2
                    )
            }
        )


    # Find highest protein diet
    highest_protein_diet = (
        avg_macros["Protein(g)"]
        .idxmax()
    )


    # Common cuisine per diet
    common_cuisine = (
        df.groupby("Diet_type")["Cuisine_type"]
        .agg(
            lambda x: x.mode()[0]
            if not x.mode().empty
            else "Unknown"
        )
    )


    cuisine_results = []


    for diet, cuisine in common_cuisine.items():

        cuisine_results.append(
            {
                "diet": diet,
                "cuisine": cuisine
            }
        )


    # Calculate additional metrics

    df["Protein_to_Carbs_ratio"] = (
        df["Protein(g)"] /
        df["Carbs(g)"].replace(0,1)
    )


    df["Carbs_to_Fat_ratio"] = (
        df["Carbs(g)"] /
        df["Fat(g)"].replace(0,1)
    )


    # Diet distribution for pie chart

    diet_distribution = (
        df["Diet_type"]
        .value_counts()
    )


    distribution_results = []


    for diet, count in diet_distribution.items():

        distribution_results.append(
            {
                "diet": diet,
                "count": int(count)
            }
        )


    # Top protein recipes

    top_protein = (
        df.sort_values(
            "Protein(g)",
            ascending=False
        )
        .groupby("Diet_type")
        .head(5)
    )


    top_protein_results = []


    for _, row in top_protein.iterrows():

        top_protein_results.append(
            {
                "diet": row["Diet_type"],

                "recipe":
                    row.get(
                        "Recipe_name",
                        "Unknown"
                    ),

                "protein":
                    float(
                        row["Protein(g)"]
                    ),

                "cuisine":
                    row.get(
                        "Cuisine_type",
                        "Unknown"
                    )
            }
        )


    execution_time = round(
        time.time() - start_time,
        3
    )


    # Return data for dashboard

    return {

        "macronutrients": macro_results,

        "dietDistribution":
            distribution_results,

        "commonCuisine":
            cuisine_results,

        "topProteinRecipes":
            top_protein_results,

        "highestProteinDiet":
            highest_protein_diet,

        "recordCount":
            len(df),

        "executionTimeSeconds":
            execution_time

    }