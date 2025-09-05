#!/usr/bin/env python3
"""
Survey Data Converter

This script converts all survey data to the standardized numerical values
according to the specified mapping rules.
"""

import pandas as pd
import os
import glob
from datetime import datetime

class SurveyDataConverter:
    def __init__(self):
        self.nasa_tlx_mapping = {
            0: 0,   # Very Low
            25: 25, # Low  
            50: 50, # Medium
            75: 75, # High
            100: 100 # Very High
        }
        
        self.system_understanding_mapping = {
            1: 0,   # Very Unclear
            2: 25,  # Unclear
            3: 50,  # Neutral
            4: 75,  # Clear
            5: 100  # Very Clear
        }
        
        self.model_impact_mapping = {
            1: 0,   # Strongly Disagree / Very Difficult
            2: 25,  # Disagree / Difficult
            3: 50,  # Neutral
            4: 75,  # Agree / Easy
            5: 100  # Strongly Agree / Very Easy
        }
        
        self.usability_mapping = {
            1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7
        }
        
        self.prior_knowledge_mapping = {
            1: 1, 2: 2, 3: 3, 4: 4, 5: 5
        }
        
        self.nasa_tlx_fields = [
            'mentalDemand', 'effortRequired', 'frustrationLevel', 
            'physicalDemand', 'temporalDemand', 'performance', 'effort', 'frustration'
        ]
        
        self.system_understanding_fields = [
            'factOpinionClarity', 'sourceInfluence', 'explanationHelpfulness'
        ]
        
        self.model_impact_fields = [
            'perspectiveAwareness', 'objectiveSubjectiveClarity', 'biasDetectionImprovement',
            'quickEvaluation', 'lessEffortThanExpected', 'quickJudgment', 'focusedReading',
            'futureUsage', 'likelyToUse', 'recommendToOthers', 'comparedToTraditional', 
            'trustInAnalysis', 'missedFacts'
        ]
        
        self.usability_fields = [
            'timeConsumingQuick', 'effortfulEffortless', 'slowFastJudgment', 'confusingClear'
        ]
        
        self.prior_knowledge_fields = [
            'familiarityBiasImpact', 'modelEffectivenessNewContent'
        ]
        
        self.text_fields = [
            'articleFamiliarity', 'otherHelpfulFeature', 'issuesEncountered', 
            'mostHelpfulFeature', 'additionalComments', 'missedFactsSpecify'
        ]

    def convert_value(self, value, field_name):
        """Convert a single value based on field type"""
        if pd.isna(value) or value == '' or value == 'nan':
            return ''
        
        if field_name in self.text_fields:
            return str(value)
        
        try:
            numeric_value = float(value)
            
            if field_name in self.nasa_tlx_fields:
                return int(numeric_value)
            
            elif field_name in self.system_understanding_fields:
                return self.system_understanding_mapping.get(int(numeric_value), int(numeric_value))
            
            elif field_name in self.model_impact_fields:
                return self.model_impact_mapping.get(int(numeric_value), int(numeric_value))
            
            elif field_name in self.usability_fields:
                return int(numeric_value)
            
            elif field_name in self.prior_knowledge_fields:
                return int(numeric_value)
            
            else:
                return int(numeric_value)
                
        except (ValueError, TypeError):
            return str(value)

    def convert_csv_file(self, input_file, output_file=None):
        """Convert a single CSV file"""
        if not os.path.exists(input_file):
            print(f"File not found: {input_file}")
            return False
        
        try:
            df = pd.read_csv(input_file)
            
            print(f"Converting {input_file}...")
            print(f"Original shape: {df.shape}")
            
            for column in df.columns:
                if column in df.columns:
                    df[column] = df[column].apply(lambda x: self.convert_value(x, column))
            
            if output_file is None:
                base_name = os.path.splitext(input_file)[0]
                output_file = f"{base_name}_converted.csv"
            
            df.to_csv(output_file, index=False)
            print(f"Converted data saved to: {output_file}")
            print(f"Converted shape: {df.shape}")
            
            print("\nSample of converted data:")
            print(df.head())
            print("\n" + "="*50 + "\n")
            
            return True
            
        except Exception as e:
            print(f"Error converting {input_file}: {str(e)}")
            return False

    def convert_all_survey_data(self):
        """Convert all survey data files in the research_data directory"""
        research_data_dir = "research_data"
        
        if not os.path.exists(research_data_dir):
            print(f"Research data directory not found: {research_data_dir}")
            return
        
        csv_files = glob.glob(os.path.join(research_data_dir, "*.csv"))
        
        if not csv_files:
            print("No CSV files found in research_data directory")
            return
        
        print(f"Found {len(csv_files)} CSV files to convert:")
        for file in csv_files:
            print(f"  - {file}")
        print()
        
        converted_files = []
        for csv_file in csv_files:
            if "_converted" in csv_file:
                continue
                
            base_name = os.path.splitext(csv_file)[0]
            output_file = f"{base_name}_converted.csv"
            
            if self.convert_csv_file(csv_file, output_file):
                converted_files.append(output_file)
        
        print(f"\nConversion complete! {len(converted_files)} files converted:")
        for file in converted_files:
            print(f"  ✅ {file}")

    def show_conversion_mapping(self):
        """Display the conversion mappings being used"""
        print("SURVEY DATA CONVERSION MAPPINGS")
        print("=" * 50)
        
        print("\n1. NASA-TLX (0-100 scale) - Already correct:")
        print("   Very Low → 0, Low → 25, Medium → 50, High → 75, Very High → 100")
        print(f"   Fields: {', '.join(self.nasa_tlx_fields)}")
        
        print("\n2. System Understanding (1-5 → 0-100 conversion):")
        print("   1 (Very Unclear) → 0, 2 (Unclear) → 25, 3 (Neutral) → 50")
        print("   4 (Clear) → 75, 5 (Very Clear) → 100")
        print(f"   Fields: {', '.join(self.system_understanding_fields)}")
        
        print("\n3. Model Impact (1-5 → 0-100 conversion):")
        print("   1 (Strongly Disagree) → 0, 2 (Disagree) → 25, 3 (Neutral) → 50")
        print("   4 (Agree) → 75, 5 (Strongly Agree) → 100")
        print(f"   Fields: {', '.join(self.model_impact_fields)}")
        
        print("\n4. Usability (1-7 scale) - Keep as is:")
        print("   1 → 1, 2 → 2, 3 → 3, 4 → 4, 5 → 5, 6 → 6, 7 → 7")
        print(f"   Fields: {', '.join(self.usability_fields)}")
        
        print("\n5. Prior Knowledge (1-5 scale) - Keep as is:")
        print("   1 → 1, 2 → 2, 3 → 3, 4 → 4, 5 → 5")
        print(f"   Fields: {', '.join(self.prior_knowledge_fields)}")
        
        print("\n6. Text Fields - Keep as is:")
        print(f"   Fields: {', '.join(self.text_fields)}")
        print("\n" + "=" * 50 + "\n")


def main():
    converter = SurveyDataConverter()
    
    print("Survey Data Converter")
    print("=" * 30)
    
    converter.show_conversion_mapping()
    
    converter.convert_all_survey_data()


if __name__ == "__main__":
    main()