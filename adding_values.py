import pandas as pd
import random
import argparse

def replacing_values(x, count, values):
    if count > (len(values)*10):
        return x
    else:
        count += 1
        return values[random.randint(0, 2)]


def adding_race_concepts(person_table):
    values = ["8657","8515","8557"]
    count = 0

    data = pd.read_csv(person_table)
    #print (data[["person_id", "gender_concept_id", "race_concept_id"]])
    data["race_concept_id"] = data["race_concept_id"].apply(lambda x: replacing_values(x, count, values))
    #print (data[["person_id", "gender_concept_id", "race_concept_id"]])
    data.to_csv(person_table)
    #exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--training", required=True, help="Path to the folder containing the full OMOP dataset")
    parser.add_argument("-e", "--evaluation", default=20, help="Percentage of the evaluation dataset to the full dataset")
    args = parser.parse_args()

    
    adding_race_concepts(args.training)
    adding_race_concepts(args.evaluation)