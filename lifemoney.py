# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import japanize_matplotlib
########################################
# 定数定義
########################################

# 基本条件
START_AGE = 22
END_AGE = 65
roueki_number = END_AGE - START_AGE + 1  # 労働年数

# 税率表 (課税所得に応じた税率と控除額)
INCOME_TAX_TABLE = [
    (   1000,    1949000, 0.05,     0),
    (1950000,    3299000, 0.10,  97500),
    (3300000,    6949000, 0.20, 427500),
    (6950000,    8999000, 0.23, 636000),
    (9000000,   17999000, 0.33,1536000),
    (18000000,  39999000, 0.40,2796000),
    (40000000, 999999999, 0.45,4796000),
]

RESIDENT_TAX_RATE = 0.10
PROPERTY_TAX_RATE = 0.014

MARRY_AGE        = 30
MARRY_INT        = 1.5
CHILD_AGE        = 32
CHILD_COST       = 300000   
HOUSE_AGE        = 40
HOUSE_COST       = 30000000
CAR_AGE          = 45
CAR_COST         = 3000000  
EDUCATION_AGE    = 45
EDUCATION_COST   = 2000000  
FUNERAL_AGE      = 50
FUNERAL_COST     = 1000000

INFLATION_RATE = 0.02
RAISE_INTERVAL = 5
RAISE_RATE = 0.10

annual_income = 3520000
food_cost = 30000
rent_cost = 70000
utility_cost = 15000
living_goods_cost = 10000
other_cost = 50000

invest_ratio = 0.2
rimawari = 0.03

def calc_income_tax(income):
    for low, high, rate, deduction in INCOME_TAX_TABLE:
        if low <= income <= high:
            return income * rate - deduction
    return 0

def calc_resident_tax(income):
    return income * RESIDENT_TAX_RATE

def calc_property_tax(house_purchased):
    if house_purchased[0]:
        return (house_purchased[1]/6) * PROPERTY_TAX_RATE
    else:
        return 0

def event_marriage(annual_living_cost_parts):
    annual_living_cost_parts['rent'] *= MARRY_INT
    annual_living_cost_parts['utility'] *= MARRY_INT
    annual_living_cost_parts['living_goods'] *= MARRY_INT
    return annual_living_cost_parts

def event_child():
    return CHILD_COST

def event_house_purchase(annual_living_cost_parts):
    annual_living_cost_parts['rent'] = 0
    return annual_living_cost_parts

def event_education():
    return EDUCATION_COST

def event_car():
    return CAR_COST

def event_funeral():
    return FUNERAL_COST

def main():
    total_savings = 0.0
    house_purchased = (False, 0)
    married = False

    current_income = annual_income
    annual_living_cost_parts = {
        'food': food_cost * 12,
        'rent': rent_cost * 12,
        'utility': utility_cost * 12,
        'living_goods': living_goods_cost * 12,
        'other': other_cost * 12
    }

    events = {
        MARRY_AGE: 'marry',
        CHILD_AGE: 'child',
        HOUSE_AGE: 'house',
        EDUCATION_AGE: 'education',
        CAR_AGE: 'car',
        FUNERAL_AGE: 'funeral'
    }

    years = []
    savings_each_year = []
    event_points = []

    for age in range(START_AGE, END_AGE+1):
        year_index = age - START_AGE + 1

        if (year_index > 1) and ((year_index-1) % RAISE_INTERVAL == 0):
            current_income = current_income * (1 + RAISE_RATE)

        for k in annual_living_cost_parts.keys():
            annual_living_cost_parts[k] *= (1 + INFLATION_RATE)

        income_tax = calc_income_tax(current_income)
        resident_tax = calc_resident_tax(current_income)
        property_tax = calc_property_tax(house_purchased)

        event_cost = 0
        if age in events:
            event_type = events[age]
            if event_type == 'marry':
                married = True
                annual_living_cost_parts = event_marriage(annual_living_cost_parts)
                event_label = "Marriage"
            elif event_type == 'child':
                event_cost += event_child()
                event_label = "Child Birth"
            elif event_type == 'house':
                house_purchased = (True, HOUSE_COST)
                event_cost += HOUSE_COST
                annual_living_cost_parts = event_house_purchase(annual_living_cost_parts)
                event_label = "House Purchase"
            elif event_type == 'education':
                event_cost += event_education()
                event_label = "Child Education"
            elif event_type == 'car':
                event_cost += event_car()
                event_label = "Car Purchase"
            elif event_type == 'funeral':
                event_cost += event_funeral()
                event_label = "Funeral"
            
            event_points.append((year_index, event_type, event_label))

        total_annual_living_cost = sum(annual_living_cost_parts.values())
        after_tax_income = current_income - (income_tax + resident_tax + property_tax)
        annual_saving = after_tax_income - (total_annual_living_cost + event_cost)

        investment_amount = current_income * invest_ratio
        investment_return = investment_amount * rimawari
        annual_saving += investment_return

        total_savings += annual_saving

        years.append(year_index)
        savings_each_year.append(total_savings)

    # グラフ描画
    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(years, savings_each_year, marker='o', linestyle='-', color='b', label='Total Savings')

    # イベント注釈
    for ep in event_points:
        y_idx = ep[0] - 1
        if 0 <= y_idx < len(savings_each_year):
            x_coord = ep[0]
            y_coord = savings_each_year[y_idx]
            event_label = ep[2]
            ax.annotate(event_label,
                        xy=(x_coord, y_coord),
                        xytext=(x_coord, y_coord + (max(savings_each_year)*0.05)),
                        arrowprops=dict(facecolor='red', shrink=0.05),
                        horizontalalignment='center')

    # 縦軸を1000万単位で表示
    def millions_formatter(x, pos):
        # x を 10,000,000(=1千万)で割った値を表示
        return f'{x/10000000:.1f}'  # 必要なら単位表記を追加: f'{x/10000000:.1f}千万'
    ax.yaxis.set_major_formatter(FuncFormatter(millions_formatter))

    ax.set_title('ライフプラン')
    ax.set_xlabel('労働年数')
    ax.set_ylabel('合計資産(1000万円)')
    ax.grid(True)
    ax.legend()
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()