from class_defs import Plant, Day, Weather, WeatherCondition
from functions import live_a_day, water_plant, is_alive
def test__with_no_sunlight_plant_dies_after_5_days():
    weather = Weather(WeatherCondition.STORMY)

    plant = Plant()
    for step in range(5):
        d = Day(weather=weather)
        plant = live_a_day(plant, d)
    
    assert is_alive(plant) is False

def test__with_sunlight_plant_lives_after_5_days():
    weather = Weather(WeatherCondition.SUNNY)

    plant = Plant()
    for _ in range(5):
        d = Day(weather=weather)
        plant = water_plant(plant)
        plant = live_a_day(plant, d)

    
    assert is_alive(plant) is True

def test__with_no_water_flower_dies_after_4_days():
    weather = Weather(WeatherCondition.SUNNY)

    plant = Plant()
    for _ in range(4):
        d = Day(weather=weather)
        plant = live_a_day(plant, d)
    
    assert is_alive(plant) is False

def test__with_with_water_flower_is_alive_after_3_days():
    weather = Weather(WeatherCondition.SUNNY)

    plant = Plant()
    for _ in range(4):
        d = Day(weather=weather)
        plant = water_plant(plant)
        plant = live_a_day(plant, d)
    
    assert is_alive(plant) is True