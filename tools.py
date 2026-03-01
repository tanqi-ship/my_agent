"""
工具模块：定义Agent可以使用的所有工具
每个工具都是一个函数，用@tool装饰器标记
"""

from langchain_core.tools import tool
import datetime
import math


@tool
def get_current_time() -> str:
    """获取当前的日期和时间。当用户问现在几点、今天日期、星期几等时间相关问题时使用此工具。"""
    now = datetime.datetime.now()
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday = weekdays[now.weekday()]
    return f"{now.strftime('%Y年%m月%d日 %H:%M:%S')} {weekday}"


@tool
def calculator(expression: str) -> str:
    """数学计算器。当需要进行数学计算时使用。
    输入合法的数学表达式，如 '2+3*4'、'100/3'、'math.sqrt(144)'、'2**10'。"""
    try:
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算出错：{str(e)}"


@tool
def unit_converter(value: float, from_unit: str, to_unit: str) -> str:
    """单位换算工具。
    支持：温度(celsius↔fahrenheit)、长度(m↔ft, cm↔inch)、重量(kg↔lb)。
    参数：value=数值，from_unit=原单位，to_unit=目标单位。"""
    conversions = {
        ("celsius", "fahrenheit"): lambda v: v * 9 / 5 + 32,
        ("fahrenheit", "celsius"): lambda v: (v - 32) * 5 / 9,
        ("kg", "lb"): lambda v: v * 2.20462,
        ("lb", "kg"): lambda v: v / 2.20462,
        ("m", "ft"): lambda v: v * 3.28084,
        ("ft", "m"): lambda v: v / 3.28084,
        ("cm", "inch"): lambda v: v / 2.54,
        ("inch", "cm"): lambda v: v * 2.54,
    }
    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](value)
        return f"{value} {from_unit} = {round(result, 4)} {to_unit}"
    return f"不支持 {from_unit} → {to_unit} 的换算"


def get_all_tools():
    """返回所有工具的列表"""
    return [get_current_time, calculator, unit_converter]