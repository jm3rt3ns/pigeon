
# enum of weather conditions
class WeatherCondition:
    SUNNY = "sunny",
    STORMY = "stormy"

class PlantSpecies:
    FLOWER = "flower"
    CACTUS = "cactus"

class Plant:
    def __init__(self):
        self.health = 100

        # set the water needs based on species
        self.species = PlantSpecies.FLOWER
        self.water_loss_per_day = 40 if self.species == PlantSpecies.FLOWER else 5

    def live_a_day(self, day):
        self.photosynthesize(day)
        # water loss
        self.health -= self.water_loss_per_day
        return self

    def photosynthesize(self, day):
        if day.weather.condition == WeatherCondition.SUNNY:
            self.health += 10 # up to a max of 100
            if self.health > 100:
                self.health = 100
        else:
            self.health -= 20

    def is_alive(self):
        return self.health > 0
    
class Weather:
    def __init__(self, condition: str):
        self.condition = condition

class Day:
    def __init__(self, weather):
        self.weather = weather

    def simulate(self):
        pass


class Person:
    def water_plant(self, plant: Plant):
        plant.health += 40
        if plant.health > 100:
            plant.health = 100

        return plant