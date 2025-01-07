console.log("EHRE")

const GAMESPEED = 0.1 // this is a percent of 1 second and defines how long it takes for the snack to travel between grid pieces of the board
const HEIGHT_OF_SEGMENT_X = 25;
const HEIGHT_OF_SEGMENT_Y = 25;
const SNAKE_COLOR = '#42f572';
const SNACK_COLOR = '#f54842';
BOARD_SIZE_X = 20;
BOARD_SIZE_Y = 20;
const Directions = Object.freeze({
    North:   Symbol("North"),
    South:  Symbol("South"),
    East:  Symbol("East"),
    West:  Symbol("West"),
});

function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}

function getVelocity(playerDirection) {
    console.log('playerDirection', playerDirection);
    switch (playerDirection) {
        case Directions.North:
            return [0,-1];
        case Directions.South:
            return [0,1];
        case Directions.West:
            return [-1,0];
        case Directions.East:
            return [1,0];
        default:
            return [0,0];
    }
}

function drawSegment(x, y, delta, playerDirection) {

    const velocity = getVelocity(playerDirection);
    console.log('velocity', velocity);
    // const smoothedX = velocity[0] * delta;
    // const smoothedY = velocity[1] * delta;
    const segment = document.createElement("div");
    segment.style.backgroundColor = SNAKE_COLOR;
    segment.style.position = 'absolute';
    segment.style.top = `${(y) * HEIGHT_OF_SEGMENT_Y}px`;
    segment.style.left = `${(x) * HEIGHT_OF_SEGMENT_X}px`;
    segment.style.width = `${HEIGHT_OF_SEGMENT_X}px`;
    segment.style.height = `${HEIGHT_OF_SEGMENT_Y}px`;
    segment.className = 'snake-segment';
    document.body.appendChild(segment);
    return segment;
}

function drawSnack(x, y) {
    const segment = document.createElement("div");
    segment.style.backgroundColor = SNACK_COLOR;
    segment.style.position = 'absolute';
    segment.style.top = `${y * HEIGHT_OF_SEGMENT_Y}px`;
    segment.style.left = `${x * HEIGHT_OF_SEGMENT_X}px`;
    segment.style.width = `${HEIGHT_OF_SEGMENT_X}px`;
    segment.style.height = `${HEIGHT_OF_SEGMENT_Y}px`;
    segment.id = 'snack';
    document.body.appendChild(segment);
    return segment;
}


class Game {
    snakeArray = [];
    playerDirection = Directions.North;
    gameStartTime = null;

    snack = null;
    tick = 0;

    constructor() {
        console.log('creating a new game');
        this.handleKeypress = this.handleKeypress.bind(this);
        document.addEventListener('keyup', this.handleKeypress);

        const animate = () => {
            requestAnimationFrame((t) => animate(t));
            this.cycle(0);
        }
        requestAnimationFrame(animate);

    }

    destroy() {
        document.removeEventListener('keyup');
    }

    // handle direction change
    handleKeypress(event) {
        console.log(`event.code '${event.code}'`);

        switch (event.code) {
            case 'ArrowDown':
                this.playerDirection = Directions.South;
                break;
            case 'ArrowLeft':
                this.playerDirection = Directions.West;
                break;
            case 'ArrowRight':
                this.playerDirection = Directions.East;
                break;
            case 'ArrowUp':
                this.playerDirection = Directions.North;
                break;
            default:
                console.debug('not a code we are interested in: ', event.code);
        }
    }

    resetGame() {
        this.snakeArray = [];
        this.playerDirection = Directions.North;
        this.gameStartTime = null;
        this.snack = null;
        this.tick = 0;
    }

    // t is a percent between steps that allows us to create smooth movement as the snake travels between positions
    cycle(t) {
        if (this.snakeArray.length === 0) {
            // we are beginning the game - position the snake somewhere
            this.snakeArray.push({ x: getRandomInt(BOARD_SIZE_X), y: getRandomInt(BOARD_SIZE_Y) });
            this.gameStartTime = Date.now();
        }

        if (this.snack === null) {
            this.snack = { x: getRandomInt(BOARD_SIZE_X), y: getRandomInt(BOARD_SIZE_Y) };
        }

        // more logic to follow here

        // check if enough time has elapsed to advance the game tick
        // this will be floor((current time - start time) / gamespeed). If this is greater than the current tick, then we advance the tick as well as move the snake, check for collisions, etc.
        const gameTime = (Date.now() - this.gameStartTime) / 1000 / GAMESPEED;
        let delta = 0;
        console.log('delta', delta);
        // console.log('gameTime', gameTime);
        if (Math.floor(gameTime) > this.tick) {
            console.log('this.playerDirection', this.playerDirection);
            const velocity = getVelocity(this.playerDirection);
            let xPosition = (this.snakeArray.at(-1).x + velocity[0]) % BOARD_SIZE_X;
            let yPosition = (this.snakeArray.at(-1).y + velocity[1]) % BOARD_SIZE_Y;

            if (yPosition < 0) {
                yPosition+=BOARD_SIZE_Y;
            }
            if (xPosition < 0) {
                xPosition+=BOARD_SIZE_X;
            }
            console.log('ypos', yPosition);
            this.snakeArray.push({ y: yPosition, x: xPosition });
            
            // check if there is a collision
            const snakeHead = this.snakeArray.at(-1);
            console.log('this.snack, snakeHead', this.snack, snakeHead);
            if (this.snack.x === snakeHead.x && this.snack.y === snakeHead.y) {
                console.log('collision!');
                this.snack = { x: getRandomInt(BOARD_SIZE_X), y: getRandomInt(BOARD_SIZE_Y) };
            }
            else if (this.snakeArray.slice(0, this.snakeArray.length - 2).findIndex((val) => val.x === snakeHead.x && val.y === snakeHead.y) !== -1) {
                console.log('self collision! game over');
                const maxSnakeLength = this.snakeArray.length;
                this.resetGame();
                alert(`Game over. Your snake was ${maxSnakeLength} segments long`);
            } else {
                this.snakeArray.splice(0, 1);
            }
            this.tick = this.tick + 1;
        }
        
        
        // draw!
        this.draw(0);
    }

    draw(delta) {
        // clear the screen
        document.body.innerHTML = '';

        // iterate over the snakeArray and draw these
        let segmentDirection = this.playerDirection;
        this.snakeArray.forEach((segment, idx) => {
            // check if the previous segment is defined and interpret the direction of the current segment, if so
            // if (previousSegment) {
            //     const deltaX = (segment.x - previousSegment.x) % 2;
            //     const deltaY = (segment.y - previousSegment.y) % 2;

            //     console.log('deltaX, deltaY', deltaX, deltaY);

            //     if (deltaX === 1) {
            //         segmentDirection = Directions.East;
            //     } else if (deltaX === -1) {
            //         segmentDirection = Directions.West;
            //     } else if (deltaY === 1) {
            //         segmentDirection = Directions.South;
            //     } else if (deltaY === -1) {
            //         segmentDirection = Directions.North;
            //     }
            // }

            // console.log('idx, segmentDirection', idx, segmentDirection);

            drawSegment(segment.x, segment.y, delta, segmentDirection);
        });

        // draw the snack
        drawSnack(this.snack.x, this.snack.y);
    }
}