#   calc/fatigue_steel_grider_design.py
import pandas as pd
import numpy as np
import math
from projects.concrete_fatigue_analysis_ntc2018.calc.steelgirder_lambda import *
import streamlit as st

def make_general_settings_df(data):
    """Create dataframe with general settings"""
    return pd.DataFrame([data])

def make_input_df(case_id, method, inputs):
    """Create input dataframe with case ID and method"""
    df = pd.DataFrame([inputs])
    df["case_id"] = case_id
    df["method"] = method
    return df


def update_lambda1_rail(inputs, temp_result_df):
    """Calculate lambda1 value based on span length and traffic type"""
    case_id = inputs["case_id"]
    span_length = inputs["span_length"]
    traffic_type = inputs["traffic_type"]
    traffic_category = inputs.get("traffic_category", "Standard")
    
    lambda1_rail = get_lambda1_rail(span_length, traffic_type, traffic_category)
    
    # lambda1으로 저장하여 일관성 유지
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda1"] = lambda1_rail
    return temp_result_df

def update_lambda2_rail(inputs, temp_result_df):
    """Calculate lambda2 value based on annual traffic volume"""
    case_id = inputs["case_id"]
    annual_traffic = inputs["annual_traffic"]
    
    lambda2 = get_lambda2_rail(annual_traffic)
    
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda2"] = lambda2
    return temp_result_df

def update_lambda3_rail(inputs, temp_result_df):
    """Calculate lambda3 value based on design life"""
    case_id = inputs["case_id"]
    design_life = inputs["design_life"]
    
    lambda3 = get_lambda3_rail(design_life)
    
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda3"] = lambda3
    return temp_result_df

def update_lambda4_rail(inputs, temp_result_df):
    """Calculate lambda4 value based on stress ratio"""
    case_id = inputs["case_id"]
    delta_sigma1 = inputs["delta_sigma1"]
    delta_sigma12 = inputs["delta_sigma12"]
    
    # Calculate stress ratio Δσ1/Δσ1+2
    stress_ratio = delta_sigma1 / delta_sigma12 if delta_sigma12 != 0 else 1.0
    
    lambda4 = get_lambda4_rail(stress_ratio)
    
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "stress_ratio"] = stress_ratio
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda4"] = lambda4
    return temp_result_df

def update_lambda_s_rail(inputs, temp_result_df):
    """Calculate combined lambda coefficient for steel"""
    case_id = inputs["case_id"]
    
    # Get individual lambda values - 올바른 컬럼명 사용
    lambda1 = temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda1"].values[0] 
    lambda2 = temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda2"].values[0]
    lambda3 = temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda3"].values[0]
    lambda4 = temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda4"].values[0]
    
    # Calculate combined lambda
    lambda_s = calculate_lambda_s_rail(lambda1, lambda2, lambda3, lambda4)
    
    # Check if lambda exceeds maximum allowed value
    is_railway = inputs.get("bridge_type", "Railway") == "Railway"
    is_valid, lambda_max = check_lambda_max(lambda_s, is_railway)
    
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda_s"] = lambda_s
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda_max"] = lambda_max
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda_check"] = "OK" if is_valid else "NG"
    
    return temp_result_df

# def calculate_shear_stresses(inputs, temp_result_df):
#     """Calculate shear stresses if beam properties are provided"""
#     case_id = inputs["case_id"]
    
#     # Check if required properties are present
#     required_fields = ["Vs1", "Vs12", "bw", "J", "H", "Qn"]
#     if all(field in inputs for field in required_fields):
#         Vs1 = inputs["Vs1"]     # Shear force with single vehicle
#         Vs12 = inputs["Vs12"]   # Shear force with two vehicles
#         bw = inputs["bw"]       # Web thickness
#         J = inputs["J"]         # Moment of inertia
#         H = inputs["H"]         # Section height
#         Qn = inputs["Qn"]       # First moment of area
        
#         # Calculate shear stresses
#         tau1 = calculate_shear_stress(Vs1, Qn, J, bw)
#         tau12 = calculate_shear_stress(Vs12, Qn, J, bw)
        
#         # Save to result dataframe
#         temp_result_df.loc[temp_result_df["case_id"] == case_id, "tau1"] = tau1
#         temp_result_df.loc[temp_result_df["case_id"] == case_id, "tau12"] = tau12
        
#         # Calculate stress ratio for shear
#         shear_ratio = tau1 / tau12 if tau12 != 0 else 1.0
#         temp_result_df.loc[temp_result_df["case_id"] == case_id, "shear_ratio"] = shear_ratio
#     else:
#         # If shear stress is provided directly
#         if "tau1" in inputs:
#             temp_result_df.loc[temp_result_df["case_id"] == case_id, "tau1"] = inputs["tau1"]
#         if "tau12" in inputs:
#             temp_result_df.loc[temp_result_df["case_id"] == case_id, "tau12"] = inputs["tau12"]
            
#     return temp_result_df

# def calculate_equivalent_stresses(inputs, temp_result_df):
#     """Calculate equivalent stress ranges using lambda coefficient"""
#     case_id = inputs["case_id"]
    
#     # Get lambda coefficient
#     lambda_s = temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda_s"].values[0]
    
#     # Get direct stress values
#     delta_sigma1 = inputs.get("delta_sigma1", 0)
#     delta_sigma12 = inputs.get("delta_sigma12", 0)
#     # Get shear stress values (either provided or calculated)
#     if "tau1" in temp_result_df.columns:
#         tau1 = temp_result_df.loc[temp_result_df["case_id"] == case_id, "tau1"].values[0]
#     else:
#         tau1 = inputs.get("tau1", 0)
    
#     # Calculate equivalent stress ranges
#     delta_sigma_equ = calculate_delta_sigma_equ(delta_sigma12, lambda_s)
#     delta_tau_equ = calculate_delta_tau_equ(tau1, lambda_s)
    
#     # Save to result dataframe
#     temp_result_df.loc[temp_result_df["case_id"] == case_id, "delta_sigma_equ"] = delta_sigma_equ
#     temp_result_df.loc[temp_result_df["case_id"] == case_id, "delta_tau_equ"] = delta_tau_equ
    
#     return temp_result_df

# def verify_fatigue_resistance(inputs, temp_result_df):
#     """Verify fatigue resistance by comparing equivalent stress ranges to design values"""
#     case_id = inputs["case_id"]
    
#     # Get equivalent stress ranges
#     delta_sigma_equ = temp_result_df.loc[temp_result_df["case_id"] == case_id, "delta_sigma_equ"].values[0]
#     delta_tau_equ = temp_result_df.loc[temp_result_df["case_id"] == case_id, "delta_tau_equ"].values[0]
    
#     # Get design values
#     delta_sigma_rsk = temp_result_df.loc[temp_result_df["case_id"] == case_id, "delta_sigma_rsk"].values[0]
#     delta_tau_rsk = temp_result_df.loc[temp_result_df["case_id"] == case_id, "delta_tau_rsk"].values[0]
    
#     # Calculate verification ratios
#     direct_stress_ratio = delta_sigma_equ / delta_sigma_rsk
#     shear_stress_ratio = delta_tau_equ / delta_tau_rsk
    
#     # Determine if verification is satisfied
#     direct_stress_check = "OK" if direct_stress_ratio <= 1.0 else "NG"
#     shear_stress_check = "OK" if shear_stress_ratio <= 1.0 else "NG"
    
#     # Save to result dataframe
#     temp_result_df.loc[temp_result_df["case_id"] == case_id, "direct_stress_ratio"] = direct_stress_ratio
#     temp_result_df.loc[temp_result_df["case_id"] == case_id, "shear_stress_ratio"] = shear_stress_ratio
#     temp_result_df.loc[temp_result_df["case_id"] == case_id, "direct_stress_check"] = direct_stress_check
#     temp_result_df.loc[temp_result_df["case_id"] == case_id, "shear_stress_check"] = shear_stress_check
    
#     # Overall check (both checks must be satisfied)
#     overall_check = "OK" if (direct_stress_check == "OK" and shear_stress_check == "OK") else "NG"
#     temp_result_df.loc[temp_result_df["case_id"] == case_id, "overall_check"] = overall_check
    
#     return temp_result_df

# def calculate_result_df(general, inputs):
#     """Perform all calculation steps and return final result dataframe"""
#     case_id = inputs["case_id"]
#     method = inputs.get("method", "rail_des")
    
#     # Initialize result dataframe
#     temp_result_df = pd.DataFrame([{"case_id": case_id}])
    
#     # Perform calculation steps
#     temp_result_df = update_lambda1_rail(inputs, temp_result_df)
#     temp_result_df = update_lambda2_rail(inputs, temp_result_df)
#     temp_result_df = update_lambda3_rail(inputs, temp_result_df)
#     temp_result_df = update_lambda4_rail(inputs, temp_result_df)
#     temp_result_df = update_lambda_s_rail(inputs, temp_result_df)
#     temp_result_df = calculate_shear_stresses(inputs, temp_result_df)
#     temp_result_df = calculate_equivalent_stresses(inputs, temp_result_df)
#     temp_result_df = verify_fatigue_resistance(inputs, temp_result_df)
    
#     # Add method to result
#     temp_result_df["method"] = method
    
#     return temp_result_df

# # Test the calculation module
# if __name__ == "__main__":
#     # Define general settings
#     general = make_general_settings_df({
#         "bridge_type": "railway_bridge",
#         "factor_rcfat": 1.5,
#         "factor_rsfat": 1.15,
#         "factor_rspfat": 1.15,
#         "factor_rf": 1.35
#     })
    
#     # Define input data
#     case_id = "case_001"
#     method = "method_steel_rail_des"
    
#     input_data = {
#         "case_id": case_id,
#         "name": "Railway Fatigue FOR STEEL GIRDER",
#         "bridge_type": "Railway",
#         "span_length": 35,
#         "annual_traffic": 25,
#         "design_life": 50,
#         "delta_sigma1": 192,
#         "delta_sigma12": 229,
#         "Vs1": 1828,
#         "Vs12": 1652,
#         "bw": 18,
#         "J": 41050000000,
#         "H": 2300,
#         "Qn": 35695652.17,
#         "traffic_type": "Mixed EC",
#         "traffic_category": "Standard"
#     }
    
#     # Create input dataframe
#     temp_input_df = make_input_df(case_id, method, input_data)
    
#     # Perform calculations
#     result_df = calculate_result_df(general, input_data)
    
#     # Display results
#     print("Input data:")
#     print(temp_input_df)
#     print("\nCalculation results:")
#     print(result_df)