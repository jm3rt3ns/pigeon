import numpy as np

def get_gravity_vector(player_origin):
    # assume origin of globe at (0, 0, 0)
    globe_origin = np.array([0, 0, 0])

    result = np.array(
        [
            player_origin[0] - globe_origin[0],
            player_origin[1] - globe_origin[1],
            player_origin[2] - globe_origin[2],
        ]
    )

    return -1 * result / np.linalg.norm(result)

def get_player_vector(player_vector):
    result = np.array(
        [
            player_vector[0],
            player_vector[1],
            player_vector[2],
        ]
    )

    return result / np.linalg.norm(result)

def test_vectors_are_correct_when_not_shifted():
    player_location = np.array([0, 10, 0])
    non_rotated_player_movement_vector = [1, 0, 0]
    g = get_gravity_vector(player_location)
    p = get_player_vector(non_rotated_player_movement_vector)

    assert (g == [0, -1, 0]).all()
    assert (p == [1, 0, 0]).all()

def test_vectors_are_correct_when_shifted():
    player_location = np.array([10, 0, 0])
    non_rotated_player_movement_vector = [1, 0, 0]
    g = get_gravity_vector(player_location)
    p = get_player_vector(non_rotated_player_movement_vector)

    assert (g == [-1, 0, 0]).all()
    assert (p == [0, -1, 0]).all()