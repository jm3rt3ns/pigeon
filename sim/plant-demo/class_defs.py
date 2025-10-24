
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
    
class Weather:
    def __init__(self, condition: str):
        self.condition = condition

class Day:
    def __init__(self, weather):
        self.weather = weather