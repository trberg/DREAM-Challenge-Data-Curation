import pandas as pd
import argparse
from datetime import datetime
import dateutil.relativedelta
import os

class MortalityPrediction:
    def __init__(self, dataFolder):
        self.dataFolder = dataFolder
        self.months_cutoff = 6
        self.predictionWindow = 6

        self.endOfData = self.get_end_of_data(dataFolder)
        self.cutoff = self.get_cutoff_date()
        
        self.data = "data/"
        if not os.path.exists(self.data):
            os.mkdir(self.data)
        
        self.train = f"{self.data}training/"
        if not os.path.exists(self.train):
            os.mkdir(self.train)
        
        self.eval = f"{self.data}evaluation/"
        if not os.path.exists(self.eval):
            os.mkdir(self.eval)

        self.truePositives = "data/TP.csv"
        self.trueNegatives = "data/TN.csv"

        self.required_tables = [
            "condition_occurrence.csv", 
            "death.csv",  
            "drug_exposure.csv", 
            "measurement.csv", 
            "observation.csv", 
            "observation_period.csv", 
            "person.csv", 
            "procedure_occurrence.csv", 
            "visit_occurrence.csv"
        ]

    
    def __repr__(self):
        return "MortalityPrediction()"

    def __str__(self):
        return f"""
Mortality Prediction Object
Location of Data:\t{self.dataFolder}
End of Data:\t\t{self.endOfData}
Cut off date:\t\t{self.cutoff}
Number of months:\t{self.months_cutoff}
True positive:\t{self.truePositives}
True negative:\t{self.trueNegatives}
        """
    
    def get_end_of_data(self, path):
        death = pd.read_csv(f"{path}/death.csv")
        max_death = max(death["death_date"])
        max_death = datetime.strptime(max_death, "%Y-%m-%d")
        return max_death

    def get_window_begin(self, months):
        window_begin = self.cutoff - dateutil.relativedelta.relativedelta(months=months)
        return window_begin


    def get_cutoff_date(self):
        cutoff = self.endOfData - dateutil.relativedelta.relativedelta(months=self.months_cutoff)
        return cutoff

    def TP_TN_distinction(self):
        if os.path.exists(self.truePositives) and os.path.exists(self.trueNegatives):
            pass
        else:
            death = pd.read_csv(f"{self.dataFolder}/death.csv", usecols=["person_id", "death_date"])
            visits = pd.read_csv(f"{self.dataFolder}/visit_occurrence.csv", usecols=["person_id", "visit_start_date"])
            data = death.merge(visits, on="person_id", how="left")
            data["death_date"] = pd.to_datetime(data["death_date"])
            data["visit_start_date"] = pd.to_datetime(data["visit_start_date"])
            data["difference"] = data.apply(lambda x: x["death_date"]-dateutil.relativedelta.relativedelta(months=self.months_cutoff) <= x["visit_start_date"], axis=1)
            TP = data[data["difference"]][["person_id"]]
            TP.drop_duplicates(inplace=True)
            TP.to_csv(self.truePositives, index=False)

            person = pd.read_csv(f"{self.dataFolder}/person.csv")
            TN = person.merge(data, on="person_id", how="left")[["person_id", "difference"]]
            TN.fillna(False, inplace=True)
            TN = TN[~TN["difference"]][["person_id"]]
            TN.drop_duplicates(inplace=True)
            TN.to_csv(self.trueNegatives, index=False)

    def split_data_to_training_evaluation(self, ratio):

        visits = pd.read_csv(f"{self.dataFolder}/visit_occurrence.csv", usecols=["person_id", "visit_start_date"])
        visits["visit_start_date"] = pd.to_datetime(visits["visit_start_date"])
        visits["cutoff"] = self.cutoff

        i = 1
        eval_ratio = 0
        while (eval_ratio) < ratio:
            visits["window_begin"] = self.get_window_begin(months=i)
            visits["evaluation"] = visits.apply(lambda x: (x["visit_start_date"] > x["window_begin"]) & (x["visit_start_date"] <= x["cutoff"]), axis=1)
            
            #print (visits.head())

            total_patients = float(len((visits[["person_id"]]).drop_duplicates()))

            evaluation = visits[visits["evaluation"]][["person_id"]].drop_duplicates()
            eval_ratio = round((float(len(evaluation))/total_patients)*100, 3)

            training = visits[~visits["person_id"].isin(evaluation["person_id"])][["person_id"]].drop_duplicates()

            #print ("Pred window size:", i)
            #print (round((float(len(training))/total_patients)*100, 3))
            #print (eval_ratio)
            i += 1
        return training, evaluation
        
    def split_tables(self, train, evaluation):
        
        for tab in self.required_tables:
            if tab == "person.csv":
                pass
            else:
                print (f"spliting {tab}")
                data = pd.read_csv(f"{self.dataFolder}/{tab}")

                train_data = data.merge(train, on="person_id", how="right")
                train_data.to_csv(f"{self.train}/{tab}")
                train_data = None

                if tab != "death.csv":
                    eval_data = data.merge(evaluation, on="person_id", how="right")
                    eval_data.to_csv(f"{self.eval}/{tab}")
                    eval_data = None

    def create_goldstandard(self):
        TP = pd.read_csv(self.truePositives)
        TP["status"] = 1
        evals = pd.read_csv(self.eval)

        goldstandard = evals.merge(TP, on="person_id", how="left")[["person_id"]]
        goldstandard.fillna(0, inplace=True)
        goldstandard.to_csv(self.data)
        print (goldstandard)


    def check_tables(self, path):
        files = set(os.listdir(path))
        req_tables = set(self.required_tables)
        if len(req_tables.intersection(files)) == len(req_tables):
            return True, None
        else:
            missing_tables = [tab for tab in (req_tables-files)]
            return False, missing_tables

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--datafolder", required=True, help="Folder path to the full OMOP dataset")
    parser.add_argument("-r", "--evalRatio", default=20, help="Percentage of the evaluation dataset to the full dataset")
    args = parser.parse_args()

    mp = MortalityPrediction(args.datafolder)

    # checks to make sure that all necessary tables are available in the data folder
    status, tables = mp.check_tables(args.datafolder)

    if status:
        
        # categorize patients as True Positive and True Negative 
        mp.TP_TN_distinction()

        #generate training and evaluation patients
        training, evaluation = mp.split_data_to_training_evaluation(ratio=args.evalRatio)

        # split all tables in the required table list in training and evaluation using the generated patient lists
        mp.split_tables(training, evaluation)

        # build the goldstandard evaluation benchmark
        mp.create_goldstandard()

    else:
        print ("Tables are missing:")
        for tab in tables:
            print (f"\t{tab}")