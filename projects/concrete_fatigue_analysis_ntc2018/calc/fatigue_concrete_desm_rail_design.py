#calc/fatigue_concrete_desm_rail_design.py
import pandas as pd
from projects.concrete_fatigue_analysis_ntc2018.calc.railway_concrete_lambda import *

def make_general_settings_df_concrete_rail(data):
    return pd.DataFrame([data])

def make_input_df_concrete_rail(case_id, method, inputs):
    df = pd.DataFrame([inputs])
    df["case_id"] = case_id
    df["method"] = method
    return df

def basecalc_concrete_rail(general, inputs, temp_result_df):
    case_id = inputs["case_id"]
    fcd = inputs["fcm"] / general["factor_rcfat"]
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "fcd"] = fcd
    return temp_result_df


def update_lambda0_concrete_rail(inputs, temp_result_df, temp_input_df):
    case_id = inputs["case_id"]
    
    fcd = temp_result_df.loc[temp_result_df["case_id"] == case_id, "fcd"].values[0]
    zone_type = temp_input_df.loc[temp_input_df["case_id"] == case_id, "zone_type"].values[0]
    if zone_type == "Compression zone":
        lambda0=0.94+0.2*(inputs["con_σcperm"]/fcd)
    else:
        lambda0=1

    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda0"] = lambda0
    return temp_result_df



def update_lambda1_concrete_rail(inputs, temp_result_df, temp_input_df):
    case_id = inputs["case_id"]
    lambda1 = get_lambda1_rail(
        inputs["support"],
        inputs["zone_type"],
        inputs["span_length"],
        inputs["traffic"]
    )
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda1"] = lambda1
    return temp_result_df

def update_lambda2_concrete_rail(inputs, temp_result_df, temp_input_df):
    case_id = inputs["case_id"]
    lambda2 = 1+1/8*math.log10((inputs["vol"])/25000000)
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda2"] = lambda2
    return temp_result_df

def update_lambda3_concrete_rail(inputs, temp_result_df, temp_input_df):
    case_id = inputs["case_id"]
    lambda3 = 1+1/8*math.log10(inputs["nyear"]/100)
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda3"] = lambda3
    return temp_result_df

def update_lambda4_concrete_rail(inputs, temp_result_df, temp_input_df):
    case_id = inputs["case_id"]
    judgement_a = inputs["con_deltaσ1max"]/inputs["con_deltaσ12"]
    if judgement_a <= 0.8:
        lambda4 = 1+1/8*math.log10(inputs["nt"]/inputs["nc"])
    else:
        lambda4 = 1
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda4"] = lambda4
    return temp_result_df


def update_lambdac_concrete_rail(inputs, temp_result_df, temp_input_df):
    case_id = inputs["case_id"]
    lambdac = temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda0"]*temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda1"]*temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda2"]*temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda3"]*temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda4"]
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambdac"] = lambdac
    return temp_result_df


def update_sigma_cd_max_equ_concrete_rail(inputs, temp_result_df, temp_input_df):
    case_id = inputs["case_id"]
    con_σcperm = temp_input_df.loc[temp_input_df["case_id"] == case_id, "con_σcperm"]
    lambdac = temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambdac"]
    con_σcmax71 = temp_input_df.loc[temp_input_df["case_id"] == case_id, "con_σcmax71"]
    sigma_cd_max_equ = con_σcperm+lambdac*(con_σcmax71-con_σcperm)
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "sigma_cd_max_equ"] = sigma_cd_max_equ
    return temp_result_df


def update_sigma_cd_min_equ_concrete_rail(inputs, temp_result_df, temp_input_df):
    case_id = inputs["case_id"]
    con_σcperm = temp_input_df.loc[temp_input_df["case_id"] == case_id, "con_σcperm"]
    lambdac = temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambdac"]
    con_σcmax71 = temp_input_df.loc[temp_input_df["case_id"] == case_id, "con_σcmax71"]
    sigma_cd_min_equ = con_σcperm+lambdac*(con_σcperm-0)
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "sigma_cd_min_equ"] = sigma_cd_min_equ
    return temp_result_df

def update_scd_max_equ_concrete_rail(inputs, temp_result_df, temp_input_df):
    case_id = inputs["case_id"]
    sigma_cd_max_equ = temp_result_df.loc[temp_result_df["case_id"] == case_id, "sigma_cd_max_equ"]
    fcd = temp_result_df.loc[temp_result_df["case_id"] == case_id, "fcd"].values[0]
    scd_max_equ = sigma_cd_max_equ/fcd
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "scd_max_equ"] = scd_max_equ
    return temp_result_df

def update_scd_min_equ_concrete_rail(inputs, temp_result_df, temp_input_df):
    case_id = inputs["case_id"]
    sigma_cd_min_equ = temp_result_df.loc[temp_result_df["case_id"] == case_id, "sigma_cd_min_equ"]
    fcd = temp_result_df.loc[temp_result_df["case_id"] == case_id, "fcd"].values[0]
    scd_min_equ = sigma_cd_min_equ/fcd
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "scd_min_equ"] = scd_min_equ
    return temp_result_df


def calculate_discriminant_concrete_rail_des(inputs, temp_result_df):
    case_id = inputs["case_id"]
    scd_min_equ = temp_result_df.loc[temp_result_df["case_id"] == case_id, "scd_min_equ"].values[0]
    scd_max_equ = temp_result_df.loc[temp_result_df["case_id"] == case_id, "scd_max_equ"].values[0]
    print(type(scd_min_equ))
    requ= scd_min_equ/scd_max_equ
    discriminant_rail_des = 14*((1-scd_max_equ)/(1-requ)**0.5)
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "requ"] = requ
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "discriminant_rail_des"] = discriminant_rail_des
    return temp_result_df

# 테스트
# if __name__ == "__main__":
    # case_id = "case_001"
    # method = "method_simple"

    # general = make_general_settings_df({
    #     "bridge_type": "road_bridge",
    #     "factor_rcfat": 1.5,
    #     "factor_rsfat": 1.15,
    #     "factor_rspfat": 1.15,
    #     "factor_rf": 1.15
    # })

    # input_data = {
    #     "case_id": case_id,
    #     "name": "Railway Fatigue FOR CONCRETE COMPRESSION",
    #     "fcm": 20,
    #     "con_σcmax71": 7.4,
    #     "con_σcperm": 1.05,
    #     "con_deltaσ1max": 5.6,
    #     "con_deltaσ12": 5.95,
    #     "span_length": 35,
    #     "nyear": 50,
    #     "vol": 100000,
    #     "support": "simply",
    #     "zone_type": "compression",
    #     "traffic": "heavy",
    #     "nc": 2,
    #     "nt": 1
    # }

    # temp_input_df = make_input_df(case_id, method, input_data)

    # # 빈 result_df 먼저 생성
    # temp_result_df = pd.DataFrame([{
    #     "case_id": case_id
    # }])
    # temp_result_df = basecalc(general, input_data, temp_result_df)
    # temp_result_df = update_lambda0(input_data, temp_result_df, temp_input_df)
    # temp_result_df = update_lambda1(input_data, temp_result_df)
    # temp_result_df = update_lambda2(input_data, temp_result_df)
    # temp_result_df = update_lambda3(input_data, temp_result_df)
    # temp_result_df = update_lambda4(input_data, temp_result_df)
    # temp_result_df = update_lambdac(input_data, temp_result_df)
    # temp_result_df = update_sigma_cd_max_equ(input_data, temp_result_df)
    # temp_result_df = update_sigma_cd_min_equ(input_data, temp_result_df)
    # temp_result_df = update_scd_max_equ(input_data, temp_result_df, temp_input_df)
    # temp_result_df = update_scd_min_equ(input_data, temp_result_df, temp_input_df)
    # temp_result_df = calculate_discriminant_rail_des(input_data, temp_result_df)

    # # 결과 계산
    # final_result_df = calculate_result_df(input_data)

    # print(temp_input_df)
    # print(temp_result_df)
