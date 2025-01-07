# SNAKE

# to run locally:
python3 -m http.server 8000

# programmed in a night

Architecture:
* queue-type data structure for moving the snake and adding/removing segments
* began with a test-driven approach
* tried to implement smooth movement, and may revisit, although I will need to add a velocity property to each segment so that it's own velocity direction is tracked correctly
* initially uses a basic render cycle that blocked JS execution/rendering, so I switched to requestAnimationFrame instead