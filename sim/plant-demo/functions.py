from class_defs import Day, Plant, WeatherCondition

def live_a_day(plant: Plant, day: Day):
    plant = photosynthesize(plant, day.weather.condition)
    # water loss
    plant.health -= plant.water_loss_per_day
    return plant

def photosynthesize(plant: Plant, weather_condition):
    if weather_condition == WeatherCondition.SUNNY:
        plant.health += 10 # up to a max of 100
        if plant.health > 100:
            plant.health = 100
    else:
        plant.health -= 20
    return plant

def is_alive(plant):
    return plant.health > 0

def water_plant(plant: Plant):
    plant.health += 40
    if plant.health > 100:
        plant.health = 100

    return plant