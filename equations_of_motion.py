from typing import List
# given a certain initial position, time, and initial velocity vector, calculate the current position of a point in 3d space

GRAVITATIONAL_CONSTANT = -9.81

def calculate_current_position(initial_v: List[float], initial_position: List[float], time: float) -> List[float]:
    x = initial_position[0] + initial_v[0] * time
    y = initial_position[1] + initial_v[1] * time
    rz = initial_position[2] + initial_v[2] * time + (0.5 * GRAVITATIONAL_CONSTANT) * (time ** 2)
    return [x, y, rz]

def test_after_one_second_when_velocity_is_zero_final_position_is_zero():
    initial_v = [0, 0, 0]
    initial_position = [0, 0, 4.905]

    assert calculate_current_position(initial_v, initial_position, 1) == [0, 0, 0]

def test_x_position_changes_as_expected():
    initial_v = [2, 0, 0]
    initial_position = [0, 0, 0]

    assert calculate_current_position(initial_v, initial_position, 1)[0] == 2

def test_y_position_changes_as_expected():
    initial_v = [0, 3, 0]
    initial_position = [0, 0, 0]

    assert calculate_current_position(initial_v, initial_position, 1)[1] == 3