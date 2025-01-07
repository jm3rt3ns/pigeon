# SNAKE 🐍

# To run locally:
```python3 -m http.server 8000```

# Background
I wrote the initial version of the classic game of snake in a night (~3 hours)

# Architecture:
* queue-type data structure for moving the snake and adding/removing segments
* using a "tick" to track game state and keep movement on a "track"
* game speed is adjustable but is fixed in relation to time (higher frame rates do not speed up the game)
* began with a test-driven approach
* tried to implement smooth movement, and may revisit, although I will need to add a velocity property to each segment so that it's own velocity direction is tracked correctly
* initially uses a basic render cycle that blocked JS execution/rendering, so I switched to requestAnimationFrame instead

# Areas to improve:
* smoother movement
* store the high score
* add sound effects
* allow user to adjust game speed (pre-game setup)
* smoother rendering/animation
* better visuals (a more realistic looking snake?)